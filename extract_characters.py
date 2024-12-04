import json

# Load the JSON file
file_path = "Ex-Machina.json"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract character names
character_names = set()  # Use a set to avoid duplicates

def extract_character_names(data):
    if isinstance(data, dict):
        # Check for dialogue entries with "@char" or "char" keys
        if "@char" in data:
            character_names.add(data["@char"])
        elif "char" in data:
            character_names.add(data["char"])
        # Recurse into the dictionary
        for key, value in data.items():
            extract_character_names(value)
    elif isinstance(data, list):
        # Recurse into each item in the list
        for item in data:
            extract_character_names(item)

# Start extracting names
extract_character_names(data)

# Output the unique character names
print("Character Names:")
print(sorted(character_names))  # Sort the names alphabetically
