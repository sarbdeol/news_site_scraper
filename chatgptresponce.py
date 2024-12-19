import requests
import json
def chatgpt_responce(title):
    url = "https://api.openai.com/v1/chat/completions"

    payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "system",
        "content": "You are a content writer"
        },
        {
        "role": "user",
        "content": "{title} \n re write this title"
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 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',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response.text


chatgpt_responce("Akshay ih good boy")