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
    
    def init_table(self):
        """
        Initializes the necessary tables for a specific guild.
        
        This method creates three tables:
          - messages: Stores message-related information.
          - members: Stores member-related information.
          - deleted_messages: Stores references to deleted messages with a foreign key constraint
            linking back to the messages table.
          - edited_messages: Stores reference to message and stores before and after edit content
        
        :param guild_name: The name of the guild for which the tables are created.
        :type guild_name: str
        """

        TABLE_INIT_MESSAGES_QUERY = f"""
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
        
        TABLE_INIT_MEMBERS_QUERY = f"""
            CREATE TABLE IF NOT EXISTS members
            (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username TEXT
            );
            """
        
        TABLE_INIT_DELETED_MESSAGES_QUERY = f"""
            CREATE TABLE IF NOT EXISTS deleted_messages
            (
                id SERIAL PRIMARY KEY,
                message_id BIGINT UNIQUE NOT NULL,
                CONSTRAINT fk_message
                    FOREIGN KEY (message_id)
                        REFERENCES messages(message_id)
                        ON DELETE CASCADE
            );
            """
        
        TABLE_INIT_EDITED_MESSAGES_QUERY = f"""
            CREATE TABLE IF NOT EXISTS edited_messages
            (
                id SERIAL PRIMARY KEY,
                message_id BIGINT NOT NULL,
                before_content TEXT,
                after_content TEXT,
                CONSTRAINT fk_message
                    FOREIGN KEY (message_id)
                        REFERENCES messages(message_id)
                        ON DELETE CASCADE
            );
            """
        
        TABLE_JOINS_AND_LEAVES_INIT_QUERY = """
            CREATE TABLE IF NOT EXISTS member_joins_leaves
            (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                time_stamp TEXT,
                is_join BOOL,
                is_leave BOOL,
                CONSTRAINT fk_members
                    FOREIGN KEY (user_id)
                        REFERENCES members(user_id)
                        ON DELETE CASCADE
            );
            """
        try:
                
            self.cursor.execute(TABLE_INIT_MESSAGES_QUERY)
            self.cursor.execute(TABLE_INIT_MEMBERS_QUERY)
            self.cursor.execute(TABLE_INIT_DELETED_MESSAGES_QUERY)
            self.cursor.execute(TABLE_INIT_EDITED_MESSAGES_QUERY)
            self.cursor.execute(TABLE_JOINS_AND_LEAVES_INIT_QUERY)
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

    async def get_message_by_id(self, message_id: int) -> list:
        """
        Retrieves a message record from the messages table based on its message_id.
        
        :param message_id: The unique identifier for the message.
        :type message_id: int
        :return: A list of tuples, each representing a matching message record.
        :rtype: list
        """

        table_messages_name = f'messages'

        SELECT_BY_ID_QUERY = sql.SQL("SELECT * FROM {} WHERE message_id = %s").format(sql.Identifier(table_messages_name))

        result = []

        try:
            self.cursor.execute(SELECT_BY_ID_QUERY, (message_id,))
            result = self.cursor.fetchall()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

        return result
    
    async def get_member_by_id(self, memeber_id: int) -> list:
        """
        Retrieves a member record from the messages table based on its member_id.
        
        :param member_id: The unique identifier for the member.
        :type member_id: int
        :return: A list of tuples, each representing a matching member record.
        :rtype: list
        """

        table_messages_name = f'members'

        SELECT_BY_ID_QUERY = sql.SQL("SELECT * FROM {} WHERE message_id = %s").format(sql.Identifier(table_messages_name))

        result = []

        try:
            self.cursor.execute(SELECT_BY_ID_QUERY, (memeber_id,))
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
        table_deleted_name = f"deleted_messages"

        ADD_QUERY = sql.SQL("""INSERT INTO {} (message_id) VALUES (%s)""").format(sql.Identifier(table_deleted_name))

        try:
            self.cursor.execute(ADD_QUERY, (message.id,))
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

    async def add_edited_message_to_database(self, before: discord.Message, after: discord.Message):
        """
        Inserts a edited message record into the edited_messages table.
        
        :param before: before message object to be add to database.
        :type before: discord.Message
        :param after: after message object to be added to database
        :type after: discord.Message
        """

        table_name = f"edited_messages"
        ADD_EDITED_MESSAGE_QUERY = sql.SQL("""
            INSERT INTO {} (message_id, before_content, after_content)
            VALUES (%s,%s,%s)
        """).format(sql.Identifier(table_name))

        try:
            self.cursor.execute(ADD_EDITED_MESSAGE_QUERY, (before.id, before.content, after.content))
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
        """
        
        table_name = f"messages"
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
             
    async def add_member_to_database(self, member: discord.Member):
        """
        Inserts a new member record into the members table for a specific guild.
        
        If a member with the same user_id already exists (based on a conflict), the insert is ignored.
        
        :param member: member entity to be added to database.
        :type member: discord.Member
        """

        # Compose the query to match guild
        ADD_MEMBER_QUERY = """
            INSERT INTO members (user_id, username)
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
                DO UPDATE SET
                username = EXCLUDED.username
                
        """
        
        data = (member.id, member.global_name)

        try:
            self.cursor.execute(ADD_MEMBER_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()

    async def get_all_messages(self) -> list:
        """
        Retrieves all message records from the messages table for a specific guild.
        
        :return: A list of tuples representing all messages.
        :rtype: list
        """
        GET_ALL_MESSAGES_QUERY = f"""
            SELECT * FROM messages
            """
        
        self.cursor.execute(GET_ALL_MESSAGES_QUERY)
        records = self.cursor.fetchall()

        return records

    async def get_messages_by_username(self, username: str) -> list:
        """
        Retrieves messages posted by a user by first determining the user's ID from the members table
        and then querying the messages table.
        
        :param username: The username of the member whose messages should be retrieved.
        :type username: str
        :return: A list of tuples representing the messages posted by the user.
        :rtype: list
        """
        user_table_name = f"members"
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

        messages_table_name = f"messages"
        GET_MESSAGES_QUERY = sql.SQL("SELECT * FROM {} WHERE user_id = %s").format(sql.Identifier(messages_table_name))
        records = []
        try:
            self.cursor.execute(GET_MESSAGES_QUERY, (user_id,))
            records = self.cursor.fetchall()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()

        return records

    async def track_member_joins_and_leaves(self, member: discord.Member, join: bool, leave: bool, timestamp: str):
        """
        Inserts record that is tracking that member joins or leaves guid
        
        :param member: member that changes state of being in guild.
        :type member: discord.Member
        :param join: if user joining rn to guild
        :type join: bool
        :param leave: if user leaving guild rn
        :type leave: bool
        :param timestamp: time of this action
        :type timestamp: str
        """


        table_name = f"member_joins_leaves"
        ADD_RECORD_QUERY = sql.SQL("INSER INTO {} (user_id, time_stamp, is_join, is_leave) VALUES (%s, %s, %s, %s)").format(sql.Identifier(table_name))

        try:
            self.cursor.execute(ADD_RECORD_QUERY, (member.id, timestamp, join, leave))
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

    async def update_user(self, before: discord.Member, after: discord.Member):
        """
        Updates username of user in database

        :param before: user instance before change
        :type before: discord.Memeber
        :param after: user instamce after update
        :type after: discord.Member
        """
        if(before.id != after.id):
            raise Exception("User id do not match!")
        table_name = "members"

        UPDATE_QUERY = sql.SQL("UPDATE {} SET username = %s WHERE user_id = %s").format(sql.Identifier(table_name))

        data = (after.global_name, after.id)

        try:
            self.cursor.execute(UPDATE_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()




