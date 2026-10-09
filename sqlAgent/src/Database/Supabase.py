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

# def execute_sql_query(sql_query: str) -> str:
#     with engine.begin() as connection:
#         result = connection.execute(text(sql_query))
#         if result.returns_rows:
#             return json.dumps(
#                 [dict(row) for row in result.mappings().all()],
#                 default=str,
#             )
#         return json.dumps({"rows_affected": result.rowcount})