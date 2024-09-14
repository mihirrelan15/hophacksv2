from flask import Flask, request, jsonify
import requests
import os
import praw
from dotenv import load_dotenv
import time
app = Flask(__name__)

# Load environment variables
load_dotenv()

# OpenRouter API endpoint and key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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" #os.getenv("OPENROUTER_API_KEY")
model = "anthropic/claude-3.5-sonnet" #"openai/o1-mini-2024-09-12"  #"meta-llama/llama-3.1-8b-instruct:free" #"nousresearch/hermes-3-llama-3.1-405b:free"

# Reddit API setup
reddit = praw.Reddit(
    client_id="mh9ybXeJtdfWFp0iU7WFpQ",
    client_secret="OPvVJETUpO8Q-gXXtfnL3AhvKYg-ig",
    user_agent="hophacks2024"
)

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

def fetch_reddit_posts(keyword, limit=10):
    subreddit = reddit.subreddit('all')
    posts = []
    for submission in subreddit.search(keyword, limit=limit):
        posts.append(submission.title)
    return posts

def analyze_sentiment(text, search_term):
    prompt = f'''Analyze the sentiment of the following text with respect to the search term. 
    Provide a sentiment score between -1 (most negative) and 1 (most positive).
    Respond with only a numeric score between -1 and 1.

    Text: {text}
    Search Term: {search_term}'''

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "seed": 42
    }

    response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    sentiment_text = result['choices'][0]['message']['content'].strip()
    try:
        return float(sentiment_text)
    except ValueError:
        return None

@app.route('/analyze_reddit_sentiment', methods=['POST'])
def analyze_reddit_sentiment():
    data = request.json
    if 'search_term' not in data:
        return jsonify({"error": "No search term provided"}), 400

    search_term = data['search_term']
    posts = fetch_reddit_posts(search_term)
    
    sentiments = []
    for post in posts:
        while True:
            try:
                print("Analyzing sentiment for post: ", post)
                sentiment = analyze_sentiment(post, search_term)
                if sentiment is not None:
                    sentiments.append(sentiment)
                break
            except requests.exceptions.HTTPError as e:
                print("Error: ", e)
                if e.response.status_code == 429:
                    time.sleep(11)  # Wait for 5 seconds before retrying
                else:
                    raise

    if sentiments:
        average_sentiment = sum(sentiments) / len(sentiments)
    else:
        average_sentiment = 0

    return jsonify({
        "search_term": search_term,
        "average_sentiment": average_sentiment,
        "num_posts_analyzed": len(sentiments)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2000)