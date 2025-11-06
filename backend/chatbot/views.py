from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Lead
from .chatbot_logic import FrechaServicesChatbot

chatbot = FrechaServicesChatbot()

@api_view(['POST'])
def chat(request):
    user_message = request.data.get('message', '')
    session_id = request.data.get('session_id', 'default')
    
    if not user_message:
        return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get bot response
    bot_response = chatbot.get_response(user_message)
    
    # Save conversation to database
    conversation = Conversation.objects.create(
        user_message=user_message,
        bot_response=bot_response,
        language=chatbot.current_language,
        session_id=session_id
    )
    
    return Response({
        'response': bot_response,
        'language': chatbot.current_language,
        'conversation_id': conversation.id,
        'timestamp': conversation.timestamp.isoformat()
    })

@api_view(['GET'])
def health(request):
    return Response({'status': 'healthy', 'service': 'Frecha Django API'})