from bs4 import BeautifulSoup
import requests

url = 'https://example.com'  # Replace with the URL of the webpage you want to scrape
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Remove script and style tags
for script in soup(["script", "style"]):
    script.extract()

# Extract visible text
visible_text = " ".join(soup.stripped_strings)

# Print or process the visible text