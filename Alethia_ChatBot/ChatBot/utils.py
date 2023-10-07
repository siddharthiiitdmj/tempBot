import psycopg2
from django.conf import settings
from typing import List
from .apps import ChatbotConfig
import re
from .exceptions import UnAuthorizedQueryError, NoQueryError, InvalidConversationIDError

def func(chatID = None, question = None): 
    try:
        init_prompt = """I will ask you questions and you should generate just sql queries without explaining the queries so I can directly copy paste them to run in postgresSQL. 
        Give the query according to postgres SQL where table name is within double inverted commas and there is public keyword before table name and the field names are also within double inverted commas.
        Here is json schema for Events table using which you should generate sql queries {"Events": {"id": "INT AUTO_INCREMENT PRIMARY KEY", "userID": "VARCHAR(255)", "deviceID": "UUID DEFAULT UUID()", "ipAddress": "VARCHAR(255)", "isVPNDetected": "BOOLEAN DEFAULT FALSE", "isEmulator": "BOOLEAN DEFAULT FALSE", "isApplicationPatched": "BOOLEAN DEFAULT FALSE", "isProxyDetected": "BOOLEAN DEFAULT FALSE", "isMaliciousLibrariesInjected": "BOOLEAN DEFAULT FALSE", "isGPSSpoofed": "BOOLEAN DEFAULT FALSE", "isJBorRooted": "BOOLEAN DEFAULT FALSE", "isDeveloperModeEnabled": "BOOLEAN DEFAULT FALSE", "googlePlayService": "BOOLEAN DEFAULT FALSE", "timestamp": "DATETIME", "applicationID": "VARCHAR(255)", "systemVersion": "VARCHAR(255)", "kernelVersion": "VARCHAR(255)", "usedMemory": "FLOAT", "batteryState": "VARCHAR(255)", "deviceUptime": "VARCHAR(255)", "batteryLevel": "INT", "identifierForVendor": "VARCHAR(255)", "deviceTimeZone": "VARCHAR(255)", "latitude": "FLOAT", "longitude": "FLOAT", "FOREIGN KEY (deviceID)": "REFERENCES Device(id) ON DELETE CASCADE"}}.
        Now i will ask you questions and you should generate answers strictly following the rules i gave you and referencing the schema for the table "Events".  """
        # Switch to the chatID conversation.
        prompt = " Just give the sql query and always specify the column names and table names inside double quotes and dont explain the queries."
        # conversations = ChatbotConfig.chatbot.get_conversation_list()
        conversation_id = chatID

        # if conversation_id not in conversations:
        #     return "Please enter a valid chatID."
        # elif conversation_id != ChatbotConfig.chatbot.current_conversation:
        ChatbotConfig.chatbot.change_conversation(conversation_id)

        # Send the question. 
        res = ChatbotConfig.chatbot.query(init_prompt + question + prompt, stream=True, _stream_yield_all=True)  #can also use web_search=true
        answer = ""
        for chunk in res:
            if chunk['type'] == 'stream':
                answer += chunk['token']
        return answer

    except InvalidConversationIDError as e:
        raise e

def get_result_from_db(query:str=None)->List:

    # query = """
    #     SELECT "userID", COUNT(*) as numDevices
    #     FROM public."Events"
    #     GROUP BY "userID"
    #     HAVING COUNT(*) > 1
    #     ORDER BY numDevices DESC;
    # """

    try:
        # Establish a connection to the database
        

        # Create a cursor object
        cursor = ChatbotConfig.connection.cursor()

        # Execute the SQL query
        cursor.execute(query)
        colnames = [desc[0] for desc in cursor.description]

        # Fetch and print the results
        records = cursor.fetchall()
        # Commit the transaction (if needed)
        cursor = ChatbotConfig.connection.commit()
        records=list(map(lambda x: list(x), records))
        result=[]
        for record in records:
            result.append(dict(zip(colnames,record)))

        if len(result)>50:
            result=result[:50]
        return result

    except psycopg2.Error as error:
        raise error
    except Exception as e:
        raise e

def get_query_from_message(message:str=None):
    sql_query_pattern = r'\b(SELECT|UPDATE|DELETE)\b.*?;'

    # Search for the SQL query in the input string
    match = re.search(sql_query_pattern, message, re.DOTALL)

    if match:
        sql_query = match.group()
        # Extract the query type (SELECT, UPDATE, DELETE)
        query_type = match.group(1).upper()
        if query_type != "SELECT":
            raise UnAuthorizedQueryError
        return sql_query
    else:
        raise NoQueryError