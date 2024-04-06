from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from openai_integration import call_openai_api


app = Flask(__name__)

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

def process_url(url):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('url_cache.db')
        c = conn.cursor()

        # Check if the URL is already cached
        c.execute("SELECT summary FROM url_cache WHERE url=?", (url,))
        cached_summary = c.fetchone()
        if cached_summary:
            return cached_summary[0]

        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} for URL: {url}")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract relevant text from the HTML
        text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
        # Split the text into chunks to avoid token indices sequence length error
        chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
        # Use the summarizer here
        summaries = [summarizer(chunk, max_length=60, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
        # Combine the summaries into one aggregated summary
        aggregated_summary = ' '.join(summaries)
        # Cache the aggregated summary in SQLite database
        c.execute("INSERT INTO url_cache (url, summary) VALUES (?, ?)", (url, aggregated_summary))
        conn.commit()
        return aggregated_summary
    except Exception as e:
        print(f"Error processing URL: {url}: {e}")
        return None
    finally:
        # Close SQLite connection
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_and_summarize():
    print("in search")
    query = request.args.get('query')
    seo_query = f"{query} -site:wikipedia.org"
    
    # Use the query to fetch search results
    search_results = list(search(query, num=10, stop=10))

    summaries = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_url, search_results)
        for result in results:
            if result is not None:
                summaries.append(result)

    # Combine the summaries into one aggregated summary
    aggregated_summary = ' '.join(summaries)[:1000]
    print(aggregated_summary)
    # Call the OpenAI API to generate text based on the aggregated summary
    openai_generated_text = call_openai_api(aggregated_summary)

    return openai_generated_text

@app.route('/display')
def display_information():
    query = request.args.get('query')
    return render_template('display-info.html', query=query)


if __name__ == '__main__':
    app.run(debug=True)
