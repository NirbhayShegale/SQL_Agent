import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def QueryExecuter():

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products")
        )

        for row in result:
            print(row)