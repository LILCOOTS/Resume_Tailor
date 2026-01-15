import ollama

# The "Prompt" you would send to OpenAI, now sent to your laptop
response = ollama.chat(model='llama3.1', messages=[
  {
    'role': 'system',
    'content': 'You are a professional resume writer. Rewrite bullet points to be impactful using the STAR method.'
  },
  {
    'role': 'user',
    'content': 'Rewrite this: "I worked on a python script that scraped data from websites."'
  },
])

print("Response from Local Llama:")
print(response['message']['content'])