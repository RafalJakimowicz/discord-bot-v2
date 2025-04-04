import psycopg2
import discord
from psycopg2 import OperationalError
from psycopg2 import sql
from dotenv import load_dotenv
from pathlib import Path
import os

class Database:
    """
    A class for managing PostgreSQL database operations related to a Discord bot's data.
    
    This class handles creating connections, initializing tables (messages, members, and deleted messages),
    and performing insert and query operations. The table names are dynamically generated based on a provided guild (server) name.
    """

    def __init__(self):
        """
        Initializes the Database object.
        
        Loads environment variables from a .env file, which should contain the database credentials.
        Establishes a connection to the PostgreSQL database and creates a cursor for executing queries.
        """

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
        """
        Creates a connection to the PostgreSQL database using the provided credentials.
        
        :return: A psycopg2 connection object if successful; otherwise, None.
        :rtype: psycopg2.extensions.connection or None
        """

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
        """
        Initializes the necessary tables for a specific guild.
        
        This method creates three tables:
          - {guild_name}_messages: Stores message-related information.
          - {guild_name}_members: Stores member-related information.
          - {guild_name}_deleted_messages: Stores references to deleted messages with a foreign key constraint
            linking back to the messages table.
        
        :param guild_name: The name of the guild for which the tables are created.
        :type guild_name: str
        """

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
        
        TABLE_INIT_DELETED_MESSAGES_QUERY = f"""
            CREATE TABLE IF NOT EXISTS {guild_name}_deleted_messages
            (
                id SERIAL PRIMARY KEY,
                message_id BIGINT UNIQUE NOT NULL,
                CONSTRAINT fk_message
                    FOREIGN KEY (message_id)
                        REFERENCES {guild_name}_messages(message_id)
                        ON DELETE CASCADE
            );
            """
        try:
                
            self.cursor.execute(TABLE_INIT_MESSAGES_QUERY)
            self.cursor.execute(TABLE_INIT_MEMBERS_QUERY)
            self.cursor.execute(TABLE_INIT_DELETED_MESSAGES_QUERY)
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

    async def get_message_by_id(self, message_id: int, guild_name: str) -> list:
        """
        Retrieves a message record from the messages table based on its message_id.
        
        :param message_id: The unique identifier for the message.
        :type message_id: int
        :param guild_name: The guild name from which to retrieve the message; it determines the table name.
        :type guild_name: str
        :return: A list of tuples, each representing a matching message record.
        :rtype: list
        """

        table_messages_name = f'{guild_name}_messages'

        SELECT_BY_ID_QUERY = sql.SQL("SELECT * FROM {} WHERE message_id = %s").format(sql.Identifier(table_messages_name))

        result = []

        try:
            self.cursor.execute(SELECT_BY_ID_QUERY, (message_id,))
            result = self.cursor.fetchall()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

        return result

    async def add_deleted_message(self, message: discord.Message):
        """
        Adds a record to the deleted messages table based on the provided Discord message.
        
        The method extracts the message ID from the provided Discord message and inserts it into
        the deleted messages table for the specified guild.
        
        :param message: The Discord message object that was deleted.
        :type message: discord.Message
        """
        table_deleted_name = f"{message.guild.name}_deleted_messages"

        ADD_QUERY = sql.SQL("""INSERT INTO {} (message_id) VALUES (%s)""").format(sql.Identifier(table_deleted_name))

        try:
            self.cursor.execute(ADD_QUERY, (message.id,))
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()


    
    async def add_message_to_database(self,message: discord.Message, timestamp: str):
        """
        Inserts a new message record into the messages table.
        
        :param message: message object to be add to database.
        :type message: discord.Message
        :param timestamp: The timestamp indicating when the message was sent.
        :type timestamp: str
        :param guild_name: The guild name, which is used to derive the table name.
        """
        
        table_name = f"{message.guild.name}_messages"
        ADD_MESSAGE_QUERY = sql.SQL("""
            INSERT INTO {} (message_id, user_id, timestamp, guild_name, channel_name, content)
            VALUES (%s,%s,%s,%s,%s,%s)
            """).format(sql.Identifier(table_name))
        
        data = (message.id, message.author.id, timestamp, message.guild.name, message.channel.name, message.content)

        try: 
            self.cursor.execute(ADD_MESSAGE_QUERY,data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()
        
        
    async def add_member_to_database(self, member: discord.Member,
                                     present: bool,
                                     banned: bool):
        """
        Inserts a new member record into the members table for a specific guild.
        
        If a member with the same user_id already exists (based on a conflict), the insert is ignored.
        
        :param member: member entity to be added to database.
        :type member: discord.Member
        :param present: Whether the member is currently present.
        :type present: bool
        :param banned: Whether the member is banned.
        :type banned: bool
        """

        
        table_name = f"{member.guild.name}_members"

        # Compose the query to match guild
        ADD_MEMBER_QUERY = sql.SQL("""
            INSERT INTO {} (user_id, username, present, banned)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """).format(sql.Identifier(table_name))
        
        data = (member.id, member.global_name, present, banned,)

        try:
            self.cursor.execute(ADD_MEMBER_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()

    async def get_all_messages(self, guild_name: str) -> list:
        """
        Retrieves all message records from the messages table for a specific guild.
        
        :param guild_name: The guild name which is used to determine the messages table name.
        :type guild_name: str
        :return: A list of tuples representing all messages.
        :rtype: list
        """
        GET_ALL_MESSAGES_QUERY = f"""
            SELECT * FROM {guild_name}_messages
            """
        
        self.cursor.execute(GET_ALL_MESSAGES_QUERY)
        records = self.cursor.fetchall()

        return records

    async def get_messages_by_username(self, guild_name:str, username: str) -> list:
        """
        Retrieves messages posted by a user by first determining the user's ID from the members table
        and then querying the messages table.
        
        :param guild_name: The guild name which is used to determine both members and messages table names.
        :type guild_name: str
        :param username: The username of the member whose messages should be retrieved.
        :type username: str
        :return: A list of tuples representing the messages posted by the user.
        :rtype: list
        """
        #format query to match actual guild
        user_table_name = f"{guild_name}_members"
        GET_USER_ID_QUERY = sql.SQL("SELECT * FROM {} WHERE username = %s").format(sql.Identifier(user_table_name))
        
        user_id = 0
        try:
            self.cursor.execute(GET_USER_ID_QUERY, (username,))
            response = self.cursor.fetchall()

            #gets user id from response
            user_id = int(response[0][1])
        except Exception as e:
            print(f"error:  {e}")
            self.connection.rollback()

        #again format query based of guild
        messages_table_name = f"{guild_name}_messages"
        GET_MESSAGES_QUERY = sql.SQL("SELECT * FROM {} WHERE user_id = %s").format(sql.Identifier(messages_table_name))
        records = []
        try:
            self.cursor.execute(GET_MESSAGES_QUERY, (user_id,))
            records = self.cursor.fetchall()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()

        return records





