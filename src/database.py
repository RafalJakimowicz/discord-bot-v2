import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
from pathlib import Path
import os

class Database:
    def __init__(self):
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        self.database_host = os.getenv('DATABASE_HOST')
        self.database_name = os.getenv('DATABASE_NAME')
        self.database_user = os.getenv('DATABASE_USER')
        self.database_password = os.getenv('DATABASE_PASSWORD')
        pass

    def create_connection(self):
        connection = None
        try:
            connection = psycopg2.connect(
                host=self.database_host,
                database=self.database_name,
                user=self.database_user,
                password=self.database_password
            )
            print("Connected to DB!")
        except OperationalError as e:
            print(f"Error {e}")

        return connection

