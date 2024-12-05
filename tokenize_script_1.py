import re
import os
import json
from collections import defaultdict
from typing import Dict, List, Optional

script_file = "movie_scripts/Ex_Machina.txt"
output_dir = "./tokenized"

characters = ['CALEB', 'AVA']

character_map = {
    'CALEB': ['CALEB', 'Caleb'],
    'AVA': ['AVA', 'Ava'],
    # Add more character variations as needed
}

def normalize_character(name: str) -> str:
    for normalized_name, variations in character_map.items():
        if name in variations:
            return normalized_name
    return name

def parse_scene_header(line: str) -> Optional[Dict[str, str]]:
    scene_header_pattern = r'^(INT|EXT)\..*-\s(DAY|NIGHT)$'
    match = re.match(scene_header_pattern, line)
    if match:
        return {'location': match.group(0), 'time': match.group(2)}
    return None

def is_stage_direction(line: str) -> bool:
    return line.startswith('(') and line.endswith(')')

def is_irrelevant(line: str) -> bool:
    irrelevant_patterns = [
        r'^\d+$',  # Page numbers
        r'^CUT TO',  # Camera directions
        # Add more patterns for irrelevant lines
    ]
    return any(re.match(pattern, line) for pattern in irrelevant_patterns)

def tokenize_by_character(script_file: str) -> Dict[str, Dict[str, List[str]]]:
    character_dialogues = defaultdict(lambda: defaultdict(list))
    current_character = None
    current_scene = None
    
    try:
        with open(script_file, 'r') as file:
            for line in file:
                line = line.strip()
                
                if any(char in line for char in characters):
                    current_character = next((char for char in characters if char in line), None)
                elif current_character:
                    if line.isupper():
                        current_character = None
                    elif is_stage_direction(line):
                        character_dialogues[current_character]['stage_directions'].append(line)
                    else:
                        character_dialogues[current_character]['dialogue'].append(line)
                
                scene_info = parse_scene_header(line)
                if scene_info:
                    current_scene = scene_info
                if current_scene and current_character:
                    character_dialogues[current_character]['scenes'].append(current_scene)
                
                if current_character and not is_stage_direction(line) and not line.isupper():
                    character_dialogues[current_character]['mentions'].append(line)
                
                if is_irrelevant(line):
                    continue
    except FileNotFoundError:
        print(f"Error: Script file '{script_file}' not found.")
        return {}
    
    return character_dialogues

def save_tokenized_content(character_dialogues: Dict[str, Dict[str, List[str]]], output_dir: str) -> None:
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        for character, content in character_dialogues.items():
            data = {
                'mentions': content['mentions'],
                'stage_directions': content['stage_directions'],
                'dialogue': content['dialogue'],
                'scenes': content['scenes']
            }
            with open(f"{output_dir}/{character}.json", 'w') as file:
                json.dump(data, file, indent=2)
    except OSError as e:
        print(f"Error: Failed to save tokenized content. {str(e)}")

def main() -> None:
    character_dialogues = tokenize_by_character(script_file)
    save_tokenized_content(character_dialogues, output_dir)
    print("\nTokenization complete! Files saved to the 'tokenized' directory.")

if __name__ == "__main__":
    main()
