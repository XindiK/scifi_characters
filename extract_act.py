import json
import sys
import re

# Ensure the character name is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <character_name>")
    sys.exit(1)

# Character name from the command-line argument
character_name = sys.argv[1]

# File paths
file_path = "Ex-Machina.json"
output_file_path = f"{character_name}_acts.txt"

# Load the JSON file
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract all acts for the specified character or containing "Ava"/"AVA"
character_acts = []

def collect_character_acts(data):
    if isinstance(data, dict):
        # Check if the object is an act by the specified character
        if "act" in data:
            act = data["act"]
            # Convert act to string for search purposes
            act_str = " ".join(act) if isinstance(act, list) else str(act)
            if data.get("@char") == character_name or re.search(r'\b(Ava|AVA)\b', act_str, re.IGNORECASE):
                character_acts.append(act_str)
        # Recurse into the dictionary
        for key, value in data.items():
            collect_character_acts(value)
    elif isinstance(data, list):
        # Recurse into each item in the list
        for item in data:
            collect_character_acts(item)

# Start collecting acts
collect_character_acts(data)

# Save the acts to a text file
with open(output_file_path, "w", encoding="utf-8") as output_file:
    for act in character_acts:
        output_file.write(act + "\n\n")  # Separate acts with double newlines

print(f"All acts performed by {character_name} or mentioning Ava/AVA have been saved to {output_file_path}")