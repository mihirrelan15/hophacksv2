import json
import requests

# Hugging Face API URL and headers
API_URL = "https://api-inference.huggingface.co/models/finiteautomata/bertweet-base-sentiment-analysis"
headers = {"Authorization": "Bearer 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"}

# Function to load the JSON file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Search function to return abstracts that contain the keyword
def search_abstracts(data, keyword):
    keyword_lower = keyword.lower()
    matching_papers = []

    # Iterate through each paper and check if the keyword is in the abstract
    for paper in data:
        abstract = paper['abstract']
        # Check if the keyword is in the abstract
        if keyword_lower in abstract.lower():
            matching_papers.append(paper)

    return matching_papers

# Function to extract sentences containing the keyword
def extract_sentences_with_keyword(abstract, keyword):
    sentences = abstract.split('.')
    keyword_lower = keyword.lower()
    key_sentences = [sentence.strip() for sentence in sentences if keyword_lower in sentence.lower()]
    return key_sentences

# Function to call the Hugging Face model for sentiment analysis
def query_huggingface(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()

# Function to display the search results and run sentiment analysis on key sentences
def display_results(papers, keyword):
    if papers:
        print(f"\nFound {len(papers)} papers with the keyword '{keyword}':\n")
        for i, paper in enumerate(papers, start=1):
            print(f"{i}. Title: {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   Year: {paper['year']}")

            # Extract key sentences from the abstract
            key_sentences = extract_sentences_with_keyword(paper['abstract'], keyword)

            if key_sentences:
                print(f"   Sentences containing '{keyword}':")
                for sentence in key_sentences:
                    print(f"      {sentence}")
                    
                    # Run sentiment analysis on each key sentence
                    sentiment_output = query_huggingface(sentence)
                    print(f"      Sentiment: {sentiment_output}\n")
            else:
                print(f"   No key sentences found containing '{keyword}'.\n")
    else:
        print(f"No papers found with the keyword '{keyword}'.")

    # Print total number of results found
    print(f"Total results: {len(papers)}")

# Main script
if __name__ == "__main__":
    # Load the JSON file containing the abstracts
    data = load_json('combined_arxiv_papers.json')

    # Input keyword from the user
    keyword = input("Enter a keyword to search for in abstracts: ")

    # Search for abstracts with the keyword
    matching_papers = search_abstracts(data, keyword)

    # Display the results with sentiment analysis on key sentences
    display_results(matching_papers, keyword)
