import re
import os
from collections import defaultdict

# File path to the script
script_file = "movie_scripts/Ex_Machina.txt"

# Directory to save tokenized output
output_dir = "./tokenized"

# Function to tokenize movie script by characters
def tokenize_by_character(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        script = f.readlines()

    character_tokens = defaultdict(list)
    current_character = None

    # Iterate through lines and assign content to the current character
    for line in script:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Detect character names in uppercase
        if re.match(r"^[A-Z]{2,}(?: [A-Z]{2,})?$", line):
            current_character = line
        elif current_character:  # Add lines to the current character
            character_tokens[current_character].append(line)

    return character_tokens

# Function to save tokenized content to files
def save_tokenized_content(character_dialogues, output_directory):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for character, content in character_dialogues.items():
        # File name is the character's name
        file_name = f"{character.replace(' ', '_')}.txt"
        file_path = os.path.join(output_directory, file_name)
        
        # Save content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            for line in content:
                f.write(line + "\n")
        
        print(f"Saved tokenized content for {character} to {file_path}")

# Main function to process and save results
def main():
    character_dialogues = tokenize_by_character(script_file)
    
    # Save tokenized content
    save_tokenized_content(character_dialogues, output_dir)

    print("\nTokenization complete! Files saved to the 'tokenized' directory.")

if __name__ == "__main__":
    main()