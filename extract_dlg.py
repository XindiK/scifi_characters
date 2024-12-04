import json
import sys

# Ensure the character name is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <character_name>")
    sys.exit(1)

# Character name from the command-line argument
character_name = sys.argv[1]

# File paths
file_path = "Ex-Machina.json"
output_file_path = f"{character_name}_dlg.txt"

# Load the JSON file
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract all dialogues for the specified character
character_dialogues = []

def collect_character_dialogues(data):
    if isinstance(data, dict):
        # Check if the object is a dialogue by the specified character
        if data.get("@char") == character_name and "dlg" in data:
            dialogue = data["dlg"]
            if isinstance(dialogue, list):
                # If "dlg" contains a list, join the lines into a single string
                character_dialogues.append(" ".join(dialogue))
            else:
                character_dialogues.append(dialogue)
        # Recurse into the dictionary
        for key, value in data.items():
            collect_character_dialogues(value)
    elif isinstance(data, list):
        # Recurse into each item in the list
        for item in data:
            collect_character_dialogues(item)

# Start collecting dialogues
collect_character_dialogues(data)

# Save the character's dialogues to a text file
with open(output_file_path, "w", encoding="utf-8") as output_file:
    for dialogue in character_dialogues:
        output_file.write(dialogue + "\n\n")  # Separate dialogues with double newlines

print(f"All dialogues spoken by {character_name} have been saved to {output_file_path}")

# import json

# # Load the JSON file
# file_path = "Ex-Machina.json"
# output_file_path = "AVA_dlg.txt"

# with open(file_path, "r", encoding="utf-8") as file:
#     data = json.load(file)

# # Extract all dialogues by AVA
# ava_dialogues = []

# def collect_ava_dialogues(data):
#     if isinstance(data, dict):
#         # Check if the object is a dialogue by AVA
#         if data.get("@char") == "AVA" and "dlg" in data:
#             dialogue = data["dlg"]
#             if isinstance(dialogue, list):
#                 # If "dlg" contains a list, join the lines into a single string
#                 ava_dialogues.append(" ".join(dialogue))
#             else:
#                 ava_dialogues.append(dialogue)
#         # Recurse into the dictionary
#         for key, value in data.items():
#             collect_ava_dialogues(value)
#     elif isinstance(data, list):
#         # Recurse into each item in the list
#         for item in data:
#             collect_ava_dialogues(item)

# # Start collecting dialogues
# collect_ava_dialogues(data)

# # Save AVA's dialogues to a text file
# with open(output_file_path, "w", encoding="utf-8") as output_file:
#     for dialogue in ava_dialogues:
#         output_file.write(dialogue + "\n\n")  # Separate dialogues with double newlines

# print(f"All dialogues spoken by AVA have been saved to {output_file_path}")