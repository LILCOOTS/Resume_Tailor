import ollama
import json

# We force the model to reply in JSON format
prompt = """
You are a Resume API. You do not speak. You only output JSON.
Task: Rewrite the input bullet point to be impactful using the STAR method.
Constraint 1: Do not invent numbers. If you don't know a metric, use "significant".
Constraint 2: Output format must be strictly: {"rewritten_bullet": "your text here"}

Input: "I worked on a python script that scraped data from websites."
"""

response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])

# This parses the string into a real Python dictionary
try:
    data = json.loads(response['message']['content'])
    print("✅ Success! Clean output for Python:")
    print(data['rewritten_bullet'])
except json.JSONDecodeError:
    print("❌ Failed. Model replied with text instead of JSON.")
    print("Raw output:", response['message']['content'])