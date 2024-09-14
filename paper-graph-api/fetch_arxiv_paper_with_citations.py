import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

def fetch_arxiv_paper(arxiv_id):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'id_list={arxiv_id}'
    full_url = base_url + search_query

    response = requests.get(full_url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        entry = root.find('{http://www.w3.org/2005/Atom}entry')
        
        if entry:
            paper = {
                'arxiv_id': arxiv_id,
                'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
                'authors': [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
                'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
                'published': entry.find('{http://www.w3.org/2005/Atom}published').text,
                'link': entry.find('{http://www.w3.org/2005/Atom}id').text
            }
            return paper
    
    print(f"Error: Unable to fetch data. Status code: {response.status_code}")
    return None

def fetch_top_citations(arxiv_id, top_n=20):
    semantic_scholar_url = f"https://api.semanticscholar.org/v1/paper/arXiv:{arxiv_id}"
    response = requests.get(semantic_scholar_url)
    
    if response.status_code == 200:
        data = response.json()
        all_citations = data.get('citations', [])
        
        # Sort citations by citationCount in descending order and take top N
        top_citations = sorted(all_citations, key=lambda x: x.get('citationCount', 0), reverse=True)[:top_n]
        
        # Extract relevant information and arXiv ID if available
        processed_citations = []
        for citation in top_citations:
            arxiv_id = None
            for id_info in citation.get('identifiers', []):
                if id_info.get('type') == 'ArXiv':
                    arxiv_id = id_info.get('id')
                    break
            
            processed_citations.append({
                'title': citation.get('title'),
                'authors': [author.get('name') for author in citation.get('authors', [])],
                'year': citation.get('year'),
                'citationCount': citation.get('citationCount'),
                'arxiv_id': arxiv_id
            })
        
        return processed_citations
    
    print(f"Error: Unable to fetch citations. Status code: {response.status_code}")
    return []

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    arxiv_id = "2103.00020"  # Example arXiv ID
    paper = fetch_arxiv_paper(arxiv_id)
    
    if paper:
        top_citations = fetch_top_citations(arxiv_id)
        paper['top_citations'] = top_citations
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"arxiv_paper_with_top_citations_{timestamp}.json"
        
        save_to_json(paper, filename)
        print(f"Data saved to {filename}")
        print(f"Number of top citations: {len(top_citations)}")
    else:
        print("No data to save.")