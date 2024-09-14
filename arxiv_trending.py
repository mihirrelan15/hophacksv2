from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
import re
from collections import Counter
import json
import nltk
from nltk.corpus import stopwords
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Download stopwords if not already downloaded
try:
    stop_words = set(stopwords.words('english'))
    logger.info("NLTK stopwords loaded successfully.")
except LookupError:
    logger.info("NLTK stopwords not found. Downloading...")
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    logger.info("NLTK stopwords downloaded and loaded.")

# Define custom scientific stopwords
scientific_stopwords = [
    'approach', 'method', 'methods', 'based', 'using', 'result', 'results', 'paper',
    'proposed', 'algorithm', 'algorithms', 'model', 'models', 'performance', 'analysis',
    'study', 'research', 'application', 'applications', 'develop', 'developed', 'provide', 
    'provides', 'use', 'used', 'present', 'presents', 'paper'
]

# Combine NLTK stopwords and scientific stopwords
all_stopwords = stop_words.union(set(scientific_stopwords))

# Simple tokenization function using regular expressions
def clean_and_tokenize(text):
    text = re.sub(r'\W+', ' ', text)  # Remove non-word characters
    tokens = text.lower().split()  # Split by spaces and convert to lowercase
    tokens = [word for word in tokens if word not in all_stopwords and len(word) > 2]  # Remove stopwords and short words
    return tokens

# Function to fetch recent arXiv papers and extract keywords
def fetch_arxiv_papers(query="all", limit=100):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{query}&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
    
    logger.info(f"Fetching data from arXiv API with query='{query}' and limit={limit}")
    # Fetch data from arXiv API
    response = requests.get(base_url + search_query)
    if response.status_code != 200:
        logger.error(f"Error fetching data from arXiv API: {response.status_code}")
        raise Exception(f"Error fetching data from arXiv API: {response.status_code}")
    
    root = ET.fromstring(response.content)
    
    keyword_counter = Counter()
    
    # Define the namespace
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
    
    # Parse XML to extract titles and abstracts
    for entry in root.findall('atom:entry', namespaces):
        title_elem = entry.find('atom:title', namespaces)
        abstract_elem = entry.find('atom:summary', namespaces)
        
        title = title_elem.text if title_elem is not None else ""
        abstract = abstract_elem.text if abstract_elem is not None else ""
        
        # Clean and tokenize text using the updated tokenization method
        tokens_title = clean_and_tokenize(title)
        tokens_abstract = clean_and_tokenize(abstract)
        
        # Count keywords in title and abstract
        keyword_counter.update(tokens_title)
        keyword_counter.update(tokens_abstract)
    
    logger.info(f"Fetched and processed {len(keyword_counter)} unique keywords.")
    return keyword_counter.most_common(20)  # Return top 20 keywords

# API endpoint to get trending keywords
@app.route('/get_keywords', methods=['GET'])
def get_trending_keywords():
    # Get query parameters
    query = request.args.get('query', default='machine learning', type=str)
    limit = request.args.get('limit', default=100, type=int)
    
    try:
        logger.info(f"Received request with query='{query}' and limit={limit}")
        # Fetch trending keywords from arXiv
        trending_keywords = fetch_arxiv_papers(query, limit)
        
        keyword_data = {
            "query": query,
            "keywords": [{"word": word, "count": count} for word, count in trending_keywords]
        }
        
        logger.info(f"Returning {len(keyword_data['keywords'])} keywords")
        return jsonify(keyword_data)
    
    except Exception as e:
        logger.error("Error processing request", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Root endpoint for testing
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "arXiv Trending Keywords API is running."})

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
