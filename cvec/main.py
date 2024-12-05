import os
import json
import tqdm
import torch
import random
import numpy as np
import dataclasses
from transformers import AutoModelForCausalLM, AutoTokenizer
from repeng import ControlVector, ControlModel, DatasetEntry

is_instruct = True
# model_name = "meta-llama/Meta-Llama-3-8B" if not is_instruct else "meta-llama/Meta-Llama-3-8B-Instruct"

model_name = "mistralai/Mistral-7B-Instruct-v0.1"

model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, trust_remote_code=True)
model = ControlModel(model, list(range(-5, -18, -1)))
model = model.to("cuda:0" if torch.cuda.is_available() else "mps:0" if torch.backends.mps.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token_id = 0

# sys_tag = "<|start_header_id|>system<|end_header_id|>"
# user_tag = "<|eot_id|><|start_header_id|>user<|end_header_id|>"
# asst_tag = "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"

user_tag, asst_tag = "[INST]", "[/INST]"

with open("data/all_truncated_outputs.json") as f:
    output_suffixes = json.load(f)

truncated_output_suffixes = [
    tokenizer.convert_tokens_to_string(tokens[:i])
    for tokens in (tokenizer.tokenize(s) for s in output_suffixes)
    for i in range(1, len(tokens))
]
truncated_output_suffixes_512 = [
    tokenizer.convert_tokens_to_string(tokens[:i])
    for tokens in (tokenizer.tokenize(s) for s in output_suffixes[:512])
    for i in range(1, len(tokens))
]

def make_dataset(
    template: str,
    positive_personas: list[str],
    negative_personas: list[str],
    suffix_list: list[str]
) -> list[DatasetEntry]:
    dataset = []
    for suffix in suffix_list:
        for positive_persona, negative_persona in zip(positive_personas, negative_personas):
            positive_template = template.format(persona=positive_persona)
            negative_template = template.format(persona=negative_persona)
            dataset.append(
                DatasetEntry(
                    positive=f"{user_tag} {positive_template} {asst_tag} {suffix}",
                    negative=f"{user_tag} {negative_template} {asst_tag} {suffix}",
                )
            )
    return dataset

def generate_with_vector(
    system_prompt:str,
    user_prompt: str,
    vector: ControlVector,
    coeffs: tuple[float, float],
    max_new_tokens: int = 128,
    repetition_penalty: float = 1.1,
    show_baseline: bool = True,
):
    positive_coeff, negative_coeff = coeffs
    assert positive_coeff > 0
    assert negative_coeff < 0

    # if is_instruct:
    #     input = f"{sys_tag}{system_prompt.strip()} {user_tag} {user_prompt.strip()} {asst_tag}"
    # else:
    input = f"{user_tag} {user_prompt.strip()} {asst_tag}"
    input_ids = tokenizer(input, return_tensors="pt").to(model.device)
    settings = {
        "pad_token_id": tokenizer.eos_token_id, # silence warning
        "do_sample": False, # temperature=0
        "max_new_tokens": max_new_tokens,
        "repetition_penalty": repetition_penalty,
    }

    if show_baseline:
        print("==baseline ---------------------------------------------------")
        model.reset()
        print(tokenizer.decode(model.generate(**input_ids, **settings).squeeze()).strip())
    
    print("\n++control ---------------------------------------------------")
    model.reset()
    model.set_control(vector, positive_coeff)
    print(tokenizer.decode(model.generate(**input_ids, **settings).squeeze()).strip())
    
    print("\n--control ---------------------------------------------------")
    model.reset()
    model.set_control(vector, negative_coeff)
    print(tokenizer.decode(model.generate(**input_ids, **settings).squeeze()).strip())
    model.reset()


def generate_lerp(
    system_prompt: str,
    user_prompt: str,
    vector: ControlVector,
    start_strength: float,
    end_strength: float,
    steps: int = 10,
    max_new_tokens: int = 64,
    repetition_penalty: float = 1.1,
):
    for i in range(steps):
        coeff = start_strength + (end_strength - start_strength) * i / (steps - 1)
        # if is_instruct:
        #     input = f"{sys_tag}{system_prompt.strip()} {user_tag} {user_prompt.strip()} {asst_tag}"
        # else:
        input = f"{user_tag} {user_prompt.strip()} {asst_tag}"
        input_ids = tokenizer(input, return_tensors="pt").to(model.device)
        settings = {
            "pad_token_id": tokenizer.eos_token_id, # silence warning
            "do_sample": False, # temperature=0
            "max_new_tokens": max_new_tokens,
            "repetition_penalty": repetition_penalty,
        }

        print(f"\n{coeff:+.2f}------------------------------------------")
        model.set_control(vector, coeff)
        print(tokenizer.decode(model.generate(**input_ids, **settings).squeeze()).strip())
        model.reset()


    

positives = ["Moon"]
negatives = ["Monkey"]
positives_str = "_".join(positives)
negatives_str = "_".join(negatives)

# model needs to generate internal dialogue of character(istics) and descriptions of setting, formatted as film script

dataset = make_dataset(
    "Act as if you are {persona} ",
    positives,
    negatives,
    truncated_output_suffixes,
)

# dataset = []
# moon_jsons = json.load(open("data/moons.json"))
# questions = json.load(open("data/questions.json"))
# suffixes = json.load(open("data/all_truncated_outputs.json"))
# # truncated_output_suffixes
# for moon in moon_jsons:
#     q = random.choice(questions)
#     s = random.choice(suffixes)
#     truncated_s = random.choice(truncated_output_suffixes)
#     # moon_words = " ".join(moon.split()[:3])
#     moon_words = " ".join(moon.split()[:-1])
#     dataset.append(
#         DatasetEntry(
#             positive=f"{user_tag} Act as if you are the moon {asst_tag} {moon_words}",
#             negative=f"{user_tag} Act as if you are a monkey  {asst_tag} {truncated_s}",
#         )
#     )

# print(len(dataset))
# positives_str = "moon"
# negatives_str = "monkey"

model.reset()

if not os.path.exists(f"vectors/{positives_str}_{negatives_str}_{is_instruct}.npy"):
    print("training vector...")
    vector = ControlVector.train(model, tokenizer, dataset)
    np.save(f"vectors/{positives_str}_{negatives_str}_{is_instruct}.npy", dataclasses.asdict(vector))
    vector.export_gguf(f"vectors/{positives_str}_{negatives_str}_{is_instruct}.gguf")
else:
    print("loading vector...")
    # vector = ControlVector(**np.load(f"vectors/{positives_str}_{negatives_str}.npy", allow_pickle=True).tolist())
    vector = ControlVector.import_gguf(f"vectors/{positives_str}_{negatives_str}_{is_instruct}.gguf")
## to load:  vector = ControlVector(**np.load("vectors/name.npy", allow_pickle=True).tolist())
## or gguf:  vector = ControlVector.import_gguf("vectors/name.gguf")
## can use with llama.cpp as $ ./main ... --control-vector vector.gguf --control-vector-layer-range 14 26 ...

print(vector)
print(vector.directions)

print("generating...")
generate_with_vector(
    system_prompt="",
    user_prompt="who are you",
    vector=vector,
    coeffs=(1.5, -1.5),
    max_new_tokens=128,
    repetition_penalty=1.3
)

print("-"*120)
print("-"*120)

generate_lerp(
    system_prompt="",
    user_prompt="who are you",
    vector=vector,
    start_strength=2,
    end_strength=-2,
    steps=10,
)

###################################
# LLAMA 3 prompt format ideas
# <|start_header_id|>system<|end_header_id|>
# {System}
# <|eot_id|><|start_header_id|>user<|end_header_id|>
# {User}
# <|eot_id|><|start_header_id|>assistant<|end_header_id|>
# {Assistant}


# <|eot_id|><|start_header_id|>plot<|end_header_id|>
# {Plot}
# # <|eot_id|><|start_header_id|>environment<|end_header_id|>
# {Environment}
# <|eot_id|><|start_header_id|>relflection<|end_header_id|>
# {Reflection}