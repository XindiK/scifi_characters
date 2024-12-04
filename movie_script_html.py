import requests
from bs4 import BeautifulSoup
import os

# List of movie names and corresponding URLs
movies = [
    "Ex-Machina",
    "Blade-Runner",
    "2001-A-Space-Odyssey"
]

base_url = "https://imsdb.com/scripts/"

# Folder to save the movie scripts
output_folder = "movie_script_html"

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over movie names and fetch their scripts
for movie in movies:
    url = f"{base_url}{movie}.html"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract content with class "scrtext"
        script_content = soup.find(class_="scrtext")
        if script_content:
            # Save the extracted content to a file in the specified folder
            file_path = os.path.join(output_folder, f"{movie}_script.html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(str(script_content))
            print(f"Successfully saved the script for {movie} to {file_path}")
        else:
            print(f"No script content found for {movie}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the script for {movie}: {e}")
