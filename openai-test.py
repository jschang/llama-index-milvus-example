import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-123456789012345678901234567890123456789012345678")
# original base is "https://api.openai.com/v1"
openai.api_base = os.environ.get("OPENAI_API_BASE", "http://localhost:8002/v1")

print(openai.Model.list())
# print("Prompt: As a software engineer, write a restful api for a key/value store.")
# print("1. Define the endpoints:\n* GET /keys/{key}: Retrieve the value associated with the given key.\n* POST /keys: Create a new key-value pair. The request body should contain the key and value.\n* PUT /keys/{key}: Update the value associated with the given key. The request body should contain the key and updated value.\n* DELETE /keys/{key}: Delete the key-value pair associated with the given key.\n1. Define the data format:\nThe request and response bodies should be in JSON format. For example:\n```json\n{\n  \"key\": \"example\",\n  \"value\": \"hello\"\n}\n```\n1. Implement the API using a web framework:\nHere's an example implementation using Flask, a popular Python web framework:\n```python\nfrom flask import Flask, request, jsonify\n\napp = Flask(__name__)\n\n# In-memory key-value store\ndata = {}\n\n@app.route('/keys/<key>', methods=['GET'])\ndef get_key(key):\n    if key in data:\n        return jsonify({key: data[key]})\n    else:\n        return jsonify({\"error\": \"Key not found\"}), 404\n\n@app.route('/keys', methods=['POST'])\ndef create_key():\n    data = request.get_json()\n    if 'key' in data and 'value' in data:\n        key = data['key']\n        value = data['value']\n        data[key] = value\n        return jsonify({\"success\": True}), 201\n    else:\n        return jsonify({\"error\": \"Missing key or value\"}), 400\n\n@app.route('/keys/<key>', methods=['PUT'])\ndef update_key(key):\n    if key in data:\n        data = request.get_json()\n        if 'value' in data:\n            data[key] = data['value']\n            return jsonify({\"success\": True}), 200\n        else:\n            return jsonify({\"error\": \"Missing value\"}), 400\n    else:\n        return jsonify({\"error\": \"Key not found\"}), 404\n\n@app.route('/keys/<key>', methods=['DELETE'])\ndef delete_key(key):\n    if key in data:\n        del data[key]\n        return jsonify({\"success\": True}), 200\n    else:\n        return jsonify({\"error\": \"Key not found\"}), 404\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```\nThis implementation uses an in-memory dictionary to store the key-value pairs. The API endpoints are defined using Flask's route decorators, and the request and response bodies are handled using the `request.get_json()` method.")

messages = []
while True:
    current_content = ""
    role = ""
    next_content = input("\n")
    print()
    messages.append({"role": "user", "content": next_content})
    completion = openai.ChatCompletion.create(
        stream=True,
        model="/models/mistral-7b-instruct-v0.1.Q6_K.gguf",
        max_tokens=32000,
        temperature=0.0,
        messages=messages)
    for x in completion:
        choices = x['choices']
        delta = choices[0]['delta']
        if choices[0]['finish_reason'] is not None:
            print()
            break
        elif delta.get('role') is not None:
            role = delta.get('role')
        elif delta.get('content') is not None:
            current_content = current_content + delta['content']
            print(delta['content'], end="")
    messages.append({"role": role, "content": current_content})
