import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
from pathlib import Path
import os

class Database:
    def __init__(self):
        #gets path to .env file
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        #loading database credentials
        self.database_host = os.getenv('DATABASE_HOST_NAME')
        self.database_name = os.getenv('DATABASE_NAME')
        self.database_user = os.getenv('DATABASE_USER')
        self.database_password = os.getenv('DATABASE_PASSWORD')

        #create connection
        self.connection = self.create_connection()

        #create cursor fo executing
        self.cursor = self.connection.cursor()

        self.init_tables()

    def create_connection(self):
        connection = None
        try:
            connection = psycopg2.connect(
                host=self.database_host,
                database=self.database_name,
                user=self.database_user,
                password=self.database_password,
                port=5432
            )
            print("Connected to DB!")
        except OperationalError as e:
            print(f"Error {e}")

        return connection
    
    def init_tables(self):
        TABLE_INIT_MESSAGES_QUERY = """
            CREATE TABLE IF NOT EXISTS messages
            (
                id SERIAL PRIMARY KEY,
                message_id BIGINT UNIQUE,
                user_id BIGINT,
                timestamp TEXT,
                guild_name TEXT,
                channel_name TEXT,
                content TEXT
            );
            """
        TABLE_INIT_MEMBERS_QUERY = """
            CREATE TABLE IF NOT EXISTS members
            (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username TEXT,
                present BOOLEAN,
                banned BOOLEAN
            );
            """
        self.cursor.execute(TABLE_INIT_MESSAGES_QUERY)
        self.cursor.execute(TABLE_INIT_MEMBERS_QUERY)

    
    async def add_message_to_database(self, message_id: int, 
                                      user_id: int, 
                                      timestamp: str, 
                                      guild_name: str, 
                                      channel_name: str, 
                                      content: str):
        ADD_MESSAGE_QUERY = """
            INSERT INTO messages (message_id, user_id, timestamp, guild_name, channel_name, content)
            VALUES (%s,%s,%s,%s,%s,%s)
            """
        
        data = (message_id, user_id, timestamp, guild_name, channel_name, content)

        try: 
            self.cursor.execute(ADD_MESSAGE_QUERY,data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
        
        
    async def add_member_to_database(self, user_id: int,
                                     username:str,
                                     present: bool,
                                     banned: bool):
        ADD_MEMBER_QUERY = """
            INSERT INTO members (user_id, username, present, banned) 
            VALUES (%s,%s,%s,%s)
            """
        
        data = (user_id, username, present, banned)

        try:
            self.cursor.execute(ADD_MEMBER_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")


