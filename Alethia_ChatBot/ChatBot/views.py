from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import func, get_result_from_db, get_query_from_message
import psycopg2
from .decorators import auth_user
from .exceptions import UnAuthorizedQueryError, NoQueryError
from .apps import ChatbotConfig


class BotHandler(APIView):
    # @auth_user
    def post(self, request):
        payload=request.data
        chatId=payload.get("id",None)
        question=payload.get("question",None)
        if not chatId:
            chatId=ChatbotConfig.chatbot.current_conversation
        if not question:
            return Response({"error":"question not found"},status=status.HTTP_400_BAD_REQUEST)
        
        message=func(chatId, question)
        try:
            query=get_query_from_message(message)
            # print(query)
            response=get_result_from_db(query)
            return Response({'data':response},
                            status=status.HTTP_200_OK)

        except (psycopg2.Error,NoQueryError):
            return Response({'error':"Improvement needed in the query"},
                            status=status.HTTP_400_BAD_REQUEST)
        except UnAuthorizedQueryError:
            return Response({'error':"UnAuthorized Query"},
                            status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({'error':"Internal Server Error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)