import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('OPEN_ROUTER_API')}",
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "model": "qwen/qwen3-235b-a22b:free",
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2"
            }
        ],
    })
)

response_json = response.json()

if response_json and 'choices' in response_json and len(response_json['choices']) > 0:
    assistant_message = response_json['choices'][0]['message']['content']
    print(assistant_message)
else:
    print("Could not extract assistant's message from the response.")
    print("Full response:", response_json)