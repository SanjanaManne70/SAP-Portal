from django.http import JsonResponse
from .chatbot_engine import chatbot_response


def chat_api(request):

    message = request.GET.get("message")

    response = chatbot_response(message)

    return JsonResponse(response)