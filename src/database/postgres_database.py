import psycopg2
from psycopg2 import OperationalError
from psycopg2 import sql
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
    
    def init_table(self, guild_name):
        TABLE_INIT_MESSAGES_QUERY = f"""
            CREATE TABLE IF NOT EXISTS {guild_name}_messages
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
        TABLE_INIT_MEMBERS_QUERY = f"""
            CREATE TABLE IF NOT EXISTS {guild_name}_members
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

    
    async def add_message_to_database(self,message_id: int, 
                                      user_id: int, 
                                      timestamp: str, 
                                      guild_name: str, 
                                      channel_name: str, 
                                      content: str):
        
        table_name = f"{guild_name}_messages"
        ADD_MESSAGE_QUERY = sql.SQL("""
            INSERT INTO {} (message_id, user_id, timestamp, guild_name, channel_name, content)
            VALUES (%s,%s,%s,%s,%s,%s)
            """).format(sql.Identifier(table_name))
        
        data = (message_id, user_id, timestamp, guild_name, channel_name, content,)

        try: 
            self.cursor.execute(ADD_MESSAGE_QUERY,data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
        
        
    async def add_member_to_database(self, user_id: int,
                                     username:str,
                                     present: bool,
                                     banned: bool,
                                     guild_name: str):
        
        table_name = f"{guild_name}_members"

        # Compose the query to match guild
        ADD_MEMBER_QUERY = sql.SQL("""
            INSERT INTO {} (user_id, username, present, banned)
            VALUES (%s, %s, %s, %s)
        """).format(sql.Identifier(table_name))
        
        data = (user_id, username, present, banned,)

        try:
            self.cursor.execute(ADD_MEMBER_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")

    async def get_all_messages(self, guild_name: str):
        GET_ALL_MESSAGES_QUERY = f"""
            SELECT * FROM {guild_name}_messages
            """
        
        self.cursor.execute(GET_ALL_MESSAGES_QUERY)
        records = self.cursor.fetchall()

        return records

    async def get_messages_by_username(self, guild_name:str, username: str):
        #format query to match actual guild
        user_table_name = f"{guild_name}_users"
        GET_USER_ID_QUERY = sql.SQL("SELECT * FROM {} WHERE username = %s").format(sql.Identifier(user_table_name))
        
        user_id = 0
        try:
            self.cursor.execute(GET_USER_ID_QUERY, (username))
            response = self.cursor.fetchall()
            print(response)

            #gets user id from response
            user_id = int(response[1])
        except Exception as e:
            print(f"error: {e}")

        #again format query based of guild
        messages_table_name = f"{guild_name}_messages"
        GET_MESSAGES_QUERY = sql.SQL("SELECT * FROM {} WHERE user_id = %s").format(sql.Identifier(messages_table_name))
        records = []
        try:
            self.cursor.execute(GET_MESSAGES_QUERY, (user_id))
            records = self.cursor.fetchall()
        except Exception as e:
            print(f"error: {e}")

        return records





