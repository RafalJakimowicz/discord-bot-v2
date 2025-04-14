import os
import psycopg2
import discord
from psycopg2 import OperationalError
from psycopg2 import sql
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Note:
    note_id: int
    title: str
    content: str
    creation_date: str
    author_id: discord.Member
    members: list[discord.Member]

class Notes_Database():
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

        self.queries = self.load_queries('sql\\notes_queries.sql')


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
            print(f"Connected to DB: {self.__class__.__name__}")
        except OperationalError as e:
            print(f"Error {e}")

        return connection
    
    def load_queries(self, filename: str):
        queries = []
        with open(filename, 'r') as file:
            queries = file.read().split(';')

        return queries
    
    def init_tables(self):      
        try:
            self.cursor.execute(self.queries[0])
            self.cursor.execute(self.queries[1])
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.commit()

    async def add_note(self, note: Note):
        try:
            params = (
                note.note_id,
                note.author_id,
                note.title,
                note.content,
                note.creation_date
            )
            self.cursor.execute(self.queries[2], params)
            for member in note.members:
                self.cursor.execute(self.queries[3], (member.id, note.note_id))
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.commit()

    async def get_all_member_notes(self, member: discord.Member) -> list:
        notes = []
        notes_ids = []

        try:
            self.cursor.execute(self.queries[5], (member.id,))
            notes_ids = self.cursor.fetchall()
            for nid in notes_ids:
                self.cursor.execute(self.queries[4], (nid[2],))
                notes.append(self.cursor.fetchone())
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()

        return notes
    
    async def get_note_by_id(self, id: int) -> tuple:
        try:
            self.cursor.execute(self.queries[4], (id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("error: " + str(e))
            self.connection.rollback()