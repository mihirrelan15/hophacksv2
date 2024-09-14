from flask import Flask, request, jsonify
from fetch_recent_arxiv_papers import get_recent_papers

app = Flask(__name__)

@app.route('/recent_papers', methods=['GET'])
def recent_papers():
    search_term = request.args.get('search_term', default='', type=str)
    if not search_term:
        return jsonify({"error": "No search term provided"}), 400
    
    papers = get_recent_papers(search_term)
    return jsonify(papers)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)