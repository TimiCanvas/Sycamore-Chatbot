import openai
import json
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

# Initializes the OpenAI client with your API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

# Loads the FAQ JSON data
def load_faq_data(file_path):
    try:
        with open(file_path, 'r') as file:
            faq_data = json.load(file)
            return faq_data
    except Exception as e:
        print(f"Error loading FAQ data: {e}")
        return None

# Constructs the system prompt using the FAQ data
def construct_system_prompt(faq_data):
    # Introduces the role and task of the assistant
    prompt_intro = (
        """You are a customer service agent for the Sycamore Oasis Homes. 
        Use the FAQ document, that is the json file provided to help answer customer questions accurately and concisely.
        Only answer in the context of this file and not outside it. Also very importantly do not cite your source or mention the faq document in your responses"""
    )

    # Flattens the FAQ data into a string format suitable for inclusion in the prompt
    faq_content = "\n".join(
        f"Q: {item['question']}\nA: {item['answer']}" for item in faq_data
    )

    # Combines introduction and FAQ content
    return f"{prompt_intro}\n\nFAQs:\n{faq_content}"

# Loads FAQ data and construct system prompt
faq_data = load_faq_data("faq.json")
if faq_data:
    system_prompt = construct_system_prompt(faq_data)
else:
    system_prompt = (
        "You are Chale, a customer service agent for GNA. Use the FAQ information to help answer customer questions accurately and concisely."
    )

def get_assistant_response(user_message):
    try:
        # Uses the chat completion endpoint with the desired model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ensure the model name is correct
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,  # Limits the number of tokens to control the response length
            temperature=0.5,  # Adjusts the temperature for more precise answers
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        # Logs specific OpenAI errors
        print(f"OpenAI Error: {e}")
        return "Sorry, I'm having trouble processing your request at the moment."
    except Exception as e:
        # Logs general errors
        print(f"Unexpected Error: {e}")
        return "Sorry, I'm having trouble processing your request at the moment."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Logs the raw data for debugging
        print("Raw data:", request.data)

        # Attempts to parse JSON data
        data = request.get_json(force=True)  # Uses get_json to handle JSON parsing
        print("Parsed JSON:", data)
        user_message = data.get("message", "")
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": f"Failed to parse JSON: {str(e)}"}), 400

    if not user_message:
        return jsonify({"error": "Message field is required"}), 400

    # Gets the chatbot's response
    response = get_assistant_response(user_message)
    return jsonify({"response": response})

@app.route("/routes", methods=["GET"])
def list_routes():
    import urllib.parse
    from flask import url_for
    
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(url_for(rule.endpoint, **(rule.defaults or {})))
        line = f"{rule.endpoint:50s} {methods:20s} {url}"
        output.append(line)
    
    return "<pre>" + "\n".join(sorted(output)) + "</pre>"

from waitress import serve

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


