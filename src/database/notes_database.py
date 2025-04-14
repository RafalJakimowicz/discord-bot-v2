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
    """
    Struct type, Note object have all information of note inside 

    :param note_id: id of note rn 6 digit
    :type note_id: int
    :param title: title on note 
    :type title: str
    :param content: all of text inside the note
    :type content: str
    :param creation_date: time of creating note formatted as string
    :type creation_date: str
    :param author_id: id of author of note
    :type author_id: int
    :param members_ids: list of all members to be part of note
    :type members_ids: list[int]
    """
    note_id: int
    title: str
    content: str
    creation_date: str
    author_id: int
    members_ids: list[int]

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

        self.queries = self.load_queries("src/database/sql/notes_queries.sql")

        self.init_tables()


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
        """
        loads queries from .sql file

        """
        queries = []
        with open(filename, 'r') as file:
            queries = file.read().split(';')

        return queries
    
    def init_tables(self):   
        """
        Inits tables for notes

        """   
        try:
            self.cursor.execute(self.queries[0])
            self.cursor.execute(self.queries[1])
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.commit()

    async def add_note(self, note: Note):
        """
        Ads note object to database, and ads every additional user to table to be written in note

        :param note: Note object to be added to db
        :type note: Note
        """
        try:
            params = (
                note.note_id,
                note.author_id,
                note.title,
                note.content,
                note.creation_date
            )
            self.cursor.execute(self.queries[2], params)

            #adding author of note
            self.cursor.execute(self.queries[3], (note.author_id, note.note_id))

            #adding rest of members in note
            for member in note.members_ids:
                if member:
                    self.cursor.execute(self.queries[3], (member, note.note_id))
            self.connection.commit()
        except Exception as e:
            print("error: " + str(e))
            self.connection.commit()

    async def get_all_member_notes(self, member: discord.Member) -> list[Note]:
        """
        gets all roles from members that use this commmand

        :param member:
        :type member: discord.Member
        :returns: list of notes belonging to member
        :rtype: list[Note]
        """
        notes = []
        notes_ids = []

        try:
            self.cursor.execute(self.queries[5], (member.id,))
            notes_ids = self.cursor.fetchall()
            for id_tuple in notes_ids:
                nid = id_tuple[2]
                print(f"nid: {nid}")
                notes.append(await self.get_note_by_id(nid))
        except Exception as e:
            print("error: " + __name__ + str(e))
            self.connection.rollback()

        return notes
    
    async def get_note_by_id(self, id: int) -> Note:
        """
        gets note nad all members of this note

        :param id: note id
        :type id: int
        """
        try:
            #get note 
            self.cursor.execute(self.queries[4], (id,))
            note = self.cursor.fetchone()

            #gets members of note
            self.cursor.execute(self.queries[6], (id,))
            note_members = self.cursor.fetchall()
            members_ids = []
            #adds members ids to list
            for m in note_members:
                members_ids.append(m[1])

            #create note object to be returned
            note_obj = Note(
                note_id=note[1],
                author_id=note[2],
                title=note[3],
                content=note[4],
                creation_date=note[5],
                members_ids=members_ids
            )

            return note_obj
        except Exception as e:
            print("error: "  + str(e))
            self.connection.rollback()