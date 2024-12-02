import requests
from bs4 import BeautifulSoup

# List of movie script URLs to scrape
movies = ["Ex-Machina", "Blade-Runner", "2001-A-Space-Odyssey"]

# Base URL for IMSDb
base_url = "https://imsdb.com/scripts/"

# Directory to save the scripts
output_dir = "./movie_scripts/"

# Create the directory if it doesn't exist
import os
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to scrape a movie script
def scrape_movie_script(movie_name):
    url = base_url + movie_name + ".html"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the script content
        script_content = soup.find("td", {"class": "scrtext"}).get_text(separator="\n")
        
        # Save the script to a file
        file_name = os.path.join(output_dir, movie_name.replace("-", "_") + ".txt")
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(script_content)
        
        print(f"Successfully saved script for {movie_name} to {file_name}")
    except Exception as e:
        print(f"Failed to scrape {movie_name}: {e}")

# Scrape scripts for all movies in the list
for movie in movies:
    scrape_movie_script(movie)