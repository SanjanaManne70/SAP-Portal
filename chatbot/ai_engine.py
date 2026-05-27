import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ollama(prompt):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",

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

        print("OLLAMA RESPONSE:", data)

        if "response" in data:
            return data["response"]

        elif "error" in data:
            return f"Ollama Error: {data['error']}"

        else:
            return "No valid response received from AI model."

    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"