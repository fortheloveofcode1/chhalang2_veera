import requests
import json
import nltk
nltk.download('punkt')

# Set your OpenAI API key
api_key = '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'
#api_key = ''

def call_openai_api(aggregated_summary):
    # Define the endpoint URL
    print("in the openai api function")
    url = 'https://api.openai.com/v1/chat/completions'

    # Define the request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Define the request payload
    payload = {
        "model": "gpt-3.5-turbo-0125",
        "messages": [{"role": "user", "content": aggregated_summary}],
        "temperature": 0.5
    }
    # Make the POST request to the OpenAI API
    response = requests.post(url, headers=headers, json=payload)

    # Print out the response status code
    print("Response status code:", response.status_code)

    # Parse the response JSON
    data = response.json()

    # Print out the response data for debugging
    print("Response data:", data)

    # Extract the generated text from the response
    try:
        generated_text = data['choices'][0]['message']['content']
        # Tokenize the text into sentences
        sentences = nltk.sent_tokenize(generated_text)
        print(sentences)
        return sentences
    except KeyError:
        print("Error: Response does not contain the expected structure.")
        return None

# Example usage
aggregated_summary = "Your aggregated summary here"
generated_sentences = call_openai_api(aggregated_summary)
if generated_sentences:
    print(generated_sentences)
