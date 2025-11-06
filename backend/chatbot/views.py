from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db import connection
from .models import Conversation, Lead
from .chatbot_logic import FrechaServicesChatbot

chatbot = FrechaServicesChatbot()

# Simple health check that doesn't require database
def health_check(request):
    return JsonResponse({
        'status': 'healthy', 
        'service': 'Frecha Django API',
        'timestamp': time.time()
    })

@api_view(['GET'])
def health(request):
    """Health check with database connection test"""
    try:
        # Test database connection
        connection.ensure_connection()
        return Response({
            'status': 'healthy', 
            'service': 'Frecha Django API',
            'database': 'connected'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'service': 'Frecha Django API', 
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['POST'])
def chat(request):
    user_message = request.data.get('message', '')
    session_id = request.data.get('session_id', 'default')
    
    if not user_message:
        return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get bot response
        bot_response = chatbot.get_response(user_message)
        
        # Save conversation to database (if database is available)
        try:
            conversation = Conversation.objects.create(
                user_message=user_message,
                bot_response=bot_response,
                language=chatbot.current_language,
                session_id=session_id
            )
            conversation_id = conversation.id
        except:
            conversation_id = None
        
        return Response({
            'response': bot_response,
            'language': chatbot.current_language,
            'conversation_id': conversation_id,
        })
    except Exception as e:
        return Response({
            'error': 'Service temporarily unavailable',
            'message': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)