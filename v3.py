import re
import json
patterns = {
    'boldTag': re.compile(r'(<b>)|(<\/b>)'),
    'characterSuffix': re.compile(r'\s*(\((V.O.|VO|V\/O|O.S.|O.S|OS|O\/S|O.C.|OC|CONT\'D|CONT|CONT.|CONT\'D.|CONT \'D.|OFF)\))|( --)'),
    'characterExclusion': [
        re.compile(r' -(<\/b>)?$'),  # ends with " -"
        re.compile(r'^\s*(<b>)?\(.+\)(<\/b>)?$'),  # all in parenthesis
        re.compile(r'^\s*(<b>)?[^\w]+(<\/b>)?$'),  # no alphanumeric characters
    ],
    'sceneLexicon': [
        re.compile(r'( |^)INT\.?:? '),
        re.compile(r'( |^)INTERIOR:? '),
        re.compile(r'^\s*INSIDE '),
        re.compile(r'( |^)EXT\.?:? '),
        re.compile(r'( |^)EXTERIOR:? '),
        re.compile(r'^\s*OUTSIDE '),
        re.compile(r'( |^)EXT\.?\/INT\.?:? '),
        re.compile(r'( |^)INT\.?\/EXT\.?:? '),
        re.compile(r'( |^)E\.?\/I\.?:? '),
        re.compile(r'( |^)I\.?\/E\.?:? ')
    ],
    'metaLexicon': [
        re.compile(r'FADE '),
        re.compile(r'FADES '),
        re.compile(r'DISSOLVE(:| )'),
        re.compile(r'BLACK:'),
        re.compile(r'THE END'),
        re.compile(r'- END'),
        re.compile(r'CREDITS'),
        re.compile(r'CUT TO'),
        re.compile(r'CUT BACK TO'),
        re.compile(r'WIPE TO'),
        re.compile(r'(INTERCUT)'),
        re.compile(r'CLOSE ON'),
        re.compile(r'CLOSER ON'),
        re.compile(r'CLOSE UP'),
        re.compile(r'CLOSEUP'),
        re.compile(r'WIDER ON'),
        re.compile(r'WIDE ON'),
        re.compile(r'RESUME ON'),
        re.compile(r'BACK ON '),
        re.compile(r'UP ON '),
        re.compile(r'<b>[A-Z]+ (ANGLE|SHOT)'),  # "WIDER ANGLE", "CLOSE ANGLE", "REACTION SHOT" etc
        re.compile(r'<b>ANGLE ON '),
        re.compile(r'<b>ON '),
        re.compile(r' LATER'),
        re.compile(r'CONTINUED'),
        re.compile(r'TRANSITION'),
        re.compile(r'(MORE)'),
        re.compile(r' SHOT:?$'),
        re.compile(r'THEIR POV'),
        re.compile(r"'S POV"),
        re.compile(r'SUPER:'),
        re.compile(r' BY .+ PLAYS\.?\s*'),  # ex: "SURRENDER" BY CHEAP TRICK PLAYS.
        re.compile(r'<b>CAMERA '),
        re.compile(r'<b>ZOOM ')
    ],
    'speechCue': re.compile(r'^\s*(<b>)?\([^)(]+\)(<\/b>)?\s*$'),  # e.g. "(screams)"
    'numericalOnly': re.compile(r'^\s*(<b>)?[0-9]*\.?(<\/b>)?\s*$')
}

def parse_movie_script(script_text):
    scenes = []
    characters = []
    dialogue = []
    actions = []

    scene_id = 1
    character_id = 1

    lines = script_text.split('\n')
    current_scene = None
    current_character = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Check if the line is a scene header
        if any(re.search(pattern, line) for pattern in patterns['sceneLexicon']):
            location, _, description = line.partition(' - ')
            current_scene = {
                'id': scene_id,
                'location': location.strip(),
                'description': description.strip()
            }
            scenes.append(current_scene)
            scene_id += 1
            continue

        # Check if the line is a character name
        if re.match(r'^[A-Z]+$', line) and not any(re.search(pattern, line) for pattern in patterns['characterExclusion']):
            character_name = re.sub(patterns['characterSuffix'], '', line)
            current_character = next((c for c in characters if c['name'] == character_name), None)
            if not current_character:
                current_character = {
                    'id': character_id,
                    'name': character_name
                }
                characters.append(current_character)
                character_id += 1
            continue

        # Check if the line is a dialogue
        if current_character:
            parenthetical = None
            if '(' in line and ')' in line:
                dialogue_text, _, parenthetical = line.partition('(')
                dialogue_text = dialogue_text.strip()
                parenthetical = parenthetical.strip(')')
            else:
                dialogue_text = line

            dialogue.append({
                'characterId': current_character['id'],
                'sceneId': current_scene['id'],
                'text': dialogue_text,
                'parenthetical': parenthetical
            })
            continue

        # If none of the above conditions are met, consider it an action
        if current_scene:
            scene_id = current_scene['id']
        else:
            scene_id = 0  # Default scene ID for actions without a specific scene

        actions.append({
            'sceneId': scene_id,
            'text': line
        })

    movie_data = {
        'title': 'Ex Machina',
        'scenes': scenes,
        'characters': characters,
        'dialogue': dialogue,
        'actions': actions
    }

    return movie_data

# Read the movie script text from a file
with open('movie_scripts/Ex_Machina.txt', 'r') as file:
    script_text = file.read()

# Parse the movie script
movie_data = parse_movie_script(script_text)

# Convert the movie data to JSON
json_data = json.dumps(movie_data, indent=2)

# Write the JSON data to a file
with open('ex_machina_data.json', 'w') as file:
    file.write(json_data)

print("Movie script parsed and saved as 'ex_machina_data.json'.")