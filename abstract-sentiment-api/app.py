from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# OpenRouter API endpoint and key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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" #os.environ.get("OPENROUTER_API_KEY")
model = "meta-llama/llama-3.1-8b-instruct:free" #"openai/o1-mini-2024-09-12" #"nousresearch/hermes-3-llama-3.1-405b:free"

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.json
    if 'text' not in data:
        return jsonify({
            "error": "No text provided",
            "token_count": 0
        }), 400

    text = data['text']
    search_term = data['search_term']
    
    # Prepare the prompt for sentiment analysis
    prompt = f'''I will provide you a research abstract and a search term. 
    The only output you will provide is a sentiment score between -1 and 1 from most negative to most positive. 
    This sentiment score should be with relation to the search term. 
    Respond with only a sentiment score between -1 and 1. Your output should never be non-numeric.

    Your overarching goal is to help researchers get an idea for the general sentiment of the community towards an a particular topic.
    Abstract: {text} 
    Search Term: {search_term}'''
    

    # Prepare the request to OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "seed": 42
    }

    try:
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        print(result)
        
        sentiment_text = result['choices'][0]['message']['content'].strip().lower()
        try:
            sentiment = float(sentiment_text)
        except ValueError:
            # If parsing fails, set sentiment to None or a default value
            sentiment = None
    
        return jsonify({
            "text": text,
            "sentiment": sentiment,
            "token_count": len(text.split())  # Simple word count as a proxy for tokens
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": str(e),
            "token_count": len(text.split())
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2000)