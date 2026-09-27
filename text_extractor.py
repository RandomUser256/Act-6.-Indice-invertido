import os
import json
import re
from bs4 import BeautifulSoup

# Small list of stopwords
STOP_WORDS = {
    "a", "de", "la", "el", "en", "y", "se", "las", "por", "pero", 
    "sus", "le", "ya", "este", "cuando", "entre", "hasta", "hay", "también", "todo", 
    "nos", "durante", "uno", "les", "todos", "esto", "nosotros", "hubos"
}

def extract_visible_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove hidden page elements (non visible web page elements)
    for element in soup(["script", "style", "meta", "noscript", "header", "footer"]):
        element.extract()
        
    return soup.get_text(separator=' ', strip=True)

def build_inverted_index(directory_path):
    inverted_index = {}
    
    for filename in os.listdir(directory_path):
        if filename.endswith(".html"):
            # File names match file ID's in 'cetys.json'
            file_id = os.path.splitext(filename)[0] # Extract ID (e.g., 'header-page-001')
            filepath = os.path.join(directory_path, filename)
            
            with open(filepath, 'r', encoding='latin-1') as f:
                html_content = f.read()
            
            text = extract_visible_text(html_content)
            
            # Lists only alphabetical words (any combination of alphabetical letters in sequence)
            words = re.findall(r'\b[a-z]+\b', text.lower())
            
            # Remove stop words and convert to a set to remove duplicate words
            filtered_words = set(word for word in words if word not in STOP_WORDS)
            
            # Create inverted index
            for word in filtered_words:
                if word not in inverted_index:
                    inverted_index[word] = set()
                inverted_index[word].add(file_id)
    
    return inverted_index

def load_registry(json_filepath):
    """Loads the JSON registry and formats it as a dictionary keyed by ID."""
    with open(json_filepath, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
        
    # Converts JSON to python dicctionary, parses Scrapy format JSON output
    if isinstance(registry_data, list):
        return {item.get('id'): item for item in registry_data if 'id' in item}
    return registry_data

def search_index(query, inverted_index, registry, match_all=True):
    """
    Searches the index for terms and returns associated entries.
    """
    # match_all argument defines AND (True) or OR (False) logic for searching multiple words 

    query_words = set(re.findall(r'\b[a-z]+\b', query.lower()))
    query_words = {w for w in query_words if w not in STOP_WORDS}
    
    if not query_words:
        return []
        
    matched_ids = None
    
    for word in query_words:
        word_matches = inverted_index.get(word, set())
        
        if matched_ids is None:
            matched_ids = word_matches
        else:
            if match_all:
                matched_ids = matched_ids.intersection(word_matches)
            else:
                matched_ids = matched_ids.union(word_matches)
                
    if not matched_ids:
        return []
        
    # Retrieve 'cetys.json' registry for every matched file
    return [registry[file_id] for file_id in matched_ids if file_id in registry]

if __name__ == "__main__":
    # File paths
    target_directory = "./webCrawler"
    json_registry_path = os.path.join(target_directory, "cetys.json")

    # 1. Build the inverted index and load the registry
    print("Building index...")
    index = build_inverted_index(target_directory)
    registry = load_registry(json_registry_path)
    
    # 2. Perform a search
    while True:
        search_term = input("Ingresa termino a buscar ['q' para terminar programa]: ")

        if search_term == 'q':
            break

        results = search_index(search_term, index, registry, match_all=True)
        
        # Search results
        print(f"Found {len(results)} matching pages.\n")
        for result in results:
            print(f"ID: {result['id']}")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print("-" * 40)
    
    