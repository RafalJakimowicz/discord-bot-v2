import psycopg2
import discord
from psycopg2 import OperationalError
from psycopg2 import sql
from dotenv import load_dotenv
from pathlib import Path
import os

class Logging_Database:
    """
    A class for managing PostgreSQL database operations related to a Discord bot's data.
    
    This class handles creating connections, initializing tables (messages, members, and deleted messages),
    and performing insert and query operations. The table names are dynamically generated based on a provided guild (server) name.
    """

    def __init__(self):
        """
        Initializes the Logging_Database object.
        
        Loads environment variables from a .env file, which contain the database credentials.
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

        self.members_queries = self.get_queries("src/database/sql/members_queries.sql")
        self.messages_queries = self.get_queries("src/database/sql/messages_queries.sql")

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
    
    def get_queries(self, filename: str) -> list[str]:
        '''
        gets queries from sql file
        '''

        with open(filename, 'r') as file:
            return file.read().split(';')
    
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

        TABLE_INIT_MESSAGES_QUERY = self.messages_queries[0]

        TABLE_INIT_MEMBERS_QUERY = self.members_queries[0]

        TABLE_INIT_DELETED_MESSAGES_QUERY = self.messages_queries[1]

        TABLE_INIT_EDITED_MESSAGES_QUERY = self.messages_queries[2]

        TABLE_JOINS_AND_LEAVES_INIT_QUERY = self.members_queries[1]
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

        SELECT_BY_ID_QUERY = self.messages_queries[3]

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
        Retrieves a member record from the messages table based on its user_id.
        
        :param member_id: The unique identifier for the member.
        :type member_id: int
        :return: A list of tuples, each representing a matching member record.
        :rtype: list
        """

        SELECT_BY_ID_QUERY = self.members_queries[2]

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

        ADD_QUERY = self.messages_queries[4]

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

        ADD_EDITED_MESSAGE_QUERY = self.messages_queries[5]

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

        ADD_MESSAGE_QUERY = self.messages_queries[6]
        
        data = (message.id, message.author.id, timestamp, message.guild.name, message.channel.name, message.content)

        try: 
            self.cursor.execute(ADD_MESSAGE_QUERY,data)
            self.connection.commit()
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()
             
    def add_member_to_database(self, member: discord.Member):
        """
        Inserts a new member record into the members table for a specific guild.
        
        If a member with the same user_id already exists (based on a conflict), the insert is ignored.
        
        :param member: member entity to be added to database.
        :type member: discord.Member
        """

        ADD_MEMBER_QUERY = self.members_queries[3]
        
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

        GET_ALL_MESSAGES_QUERY = self.messages_queries[7]
        
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

        GET_MESSAGES_QUERY = self.messages_queries[8]
        records = []
        try:
            self.cursor.execute(GET_MESSAGES_QUERY, (username,))
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

        ADD_RECORD_QUERY = self.members_queries[4]

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
        
        UPDATE_QUERY = self.members_queries[5]

        data = (after.global_name, after.id)

        try:
            self.cursor.execute(UPDATE_QUERY, data)
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

    async def get_all_statuses(self) -> list:
        """
        Gets all joins and leaves from database

        :return: list of all rows
        :rtype: list
        """

        GET_QUERY = self.members_queries[6]

        result = []

        try:
            self.cursor.execute(GET_QUERY)
            result = self.cursor.fetchall()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

        return result
    
    async def get_all_members(self) -> list:
        """
        Gets all members from database

        :return: list of all rows
        :rtype: list
        """

        GET_QUERY = self.members_queries[7]

        result = []

        try:
            self.cursor.execute(GET_QUERY)
            result = self.cursor.fetchall()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

        return result



