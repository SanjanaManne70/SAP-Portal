import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",

            "prompt": f"""
You are an SAP ERP chatbot assistant.

Rules:
- Keep answers concise
- Maximum 2-3 lines
- Direct and professional
- No lengthy explanations

Question:
{prompt}
""",

            "stream": False,

            "options": {
                "num_predict": 60,
                "temperature": 0.3
            }
        }
    )

    data = response.json()

    return data["response"]