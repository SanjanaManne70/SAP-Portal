from .db_search import search_database
from .ai_engine import ask_ollama


def chatbot_response(user_query):

    db_result = search_database(user_query)

    if db_result["found"]:

        return {
            "source": "database",
            "answer": db_result["answer"]
        }

    ai_answer = ask_ollama(user_query)

    return {
        "source": "ollama",
        "answer": ai_answer
    }