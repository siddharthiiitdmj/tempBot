from django.apps import AppConfig
from django.conf import settings
from .login import Login
from .hugchat import ChatBot
import psycopg2

class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name='ChatBot'

    # Login to HUG
    sign = Login(settings.EMAIL, settings.PASSWORD)
    cookies = sign.login()
    chatbot = ChatBot(cookies=cookies)

    print("Chat Id---------> ",chatbot.current_conversation)
    print("Login successfully🎉.")

    # Establish a connection to the database
    connection = psycopg2.connect(**settings.DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SET search_path TO public;")
