import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_script(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    script_pre = soup.find('pre')
    if script_pre:
        script_text = script_pre.get_text()
        formatted_script = format_script(script_text)
        return formatted_script
    else:
        return None

def format_script(script_text):
    lines = script_text.split('\n')
    formatted_scenes = []
    current_scene = None
    current_character = None
    current_dialogue = []
    current_action = []
    
    for line in lines:
        line = line.strip()
        
        # Discard page numbers enclosed in <b> tags
        line = re.sub(r'<b>\d+\.?</b>', '', line)
        
        if re.match(r'^(INT|EXT)\.', line, re.IGNORECASE):
            if current_scene:
                if current_dialogue:
                    current_dialogue.append({'character': current_character, 'dialogue': ' '.join(current_dialogue)})
                formatted_scenes.append({'scene': current_scene, 'events': current_dialogue + current_action})
                current_dialogue = []
                current_action = []
                current_character = None
            current_scene = re.sub(r'\s+', ' ', line)
        elif line.isupper():
            if '(CONT\'D)' in line:
                line = line.split('(CONT\'D)')[0].strip()
            if current_character:
                if current_dialogue:
                    current_dialogue.append({'character': current_character, 'dialogue': ' '.join(current_dialogue)})
                    current_dialogue = []
            current_character = re.sub(r'\s+', ' ', line)
        else:
            if line.startswith('          '):
                if current_dialogue:
                    current_dialogue.append({'character': current_character, 'dialogue': ' '.join(current_dialogue)})
                    current_dialogue = []
                current_action.append(re.sub(r'\s+', ' ', line.strip()))
            else:
                current_dialogue.append(re.sub(r'\s+', ' ', line))
    
    if current_scene:
        if current_dialogue:
            current_dialogue.append({'character': current_character, 'dialogue': ' '.join(current_dialogue)})
        formatted_scenes.append({'scene': current_scene, 'events': current_dialogue + current_action})
    
    return formatted_scenes

# Example usage
url = 'https://imsdb.com/scripts/Ex-Machina.html'
formatted_script = scrape_script(url)

if formatted_script:
    movie_title = input("What's the name of this movie? ")
    movie_year = input("When was this movie released? (Leave blank to skip) ")
    
    script = {
        'movie_title': movie_title,
        'movie_url': url,
        'movie_script': formatted_script
    }
    
    if movie_year:
        script['movie_year'] = movie_year
    
    out_filename = input('Enter the output filename: ')
    with open(out_filename, 'w') as fd:
        json.dump(script, fd, indent=2)
        print(f"Successfully wrote {movie_title}'s script as JSON to {out_filename}.")
else:
    print('Script not found.')
