import requests
from bs4 import BeautifulSoup

url = "https://www.python.org/"

# Fetch the raw HTML content
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Example A: Get all the text on the page
print(soup.get_text())

# Example B: Find all paragraph tags and print their text
paragraphs = soup.find_all('p')
for p in paragraphs:
    print(p.text.strip())