import xmltodict
import json

# Load the XML file
file_path = "Ex-Machina.xml"  # Replace with the path to your XML file

with open(file_path, "r", encoding="utf-8") as file:
    xml_content = file.read()

# Parse the XML content to a Python dictionary
xml_dict = xmltodict.parse(xml_content)

# Convert the Python dictionary to a JSON string with indentation
json_content = json.dumps(xml_dict, indent=4)

# Save the JSON content to a file
output_file_path = "Ex-Machina.json"  # Output JSON file
with open(output_file_path, "w", encoding="utf-8") as json_file:
    json_file.write(json_content)

print(f"JSON file saved to {output_file_path}")
