from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

@app.route('/process', methods=['POST'])
def process():
    user_input = request.json['input']
    prompt = f"Recursively analyze this: {user_input}. Identify themes, compress into truths."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    return jsonify({'output': response['choices'][0]['message']['content']})

if __name__ == '__main__':
    app.run(debug=True)
