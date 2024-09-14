import json

# Function to load the JSON file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Search function to return abstracts that contain the keyword
def search_abstracts(data, keyword):
    # Convert the keyword to lowercase to make the search case-insensitive
    keyword_lower = keyword.lower()
    
    # List to store matching papers
    matching_papers = []

    # Iterate through each paper and check if the keyword is in the abstract
    for paper in data:
        # Check if the keyword is in the abstract (case-insensitive)
        if keyword_lower in paper['abstract'].lower():
            matching_papers.append(paper)

    # Return the matching papers
    return matching_papers

# Function to display the search results
def display_results(papers, keyword):
    if papers:
        print(f"\nFound {len(papers)} papers with the keyword '{keyword}':\n")
        for i, paper in enumerate(papers, start=1):
            print(f"{i}. Title: {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   Year: {paper['year']}")
            print(f"   Abstract: {paper['abstract']}\n")
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

    # Display the results
    display_results(matching_papers, keyword)
