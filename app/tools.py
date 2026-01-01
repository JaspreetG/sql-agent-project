import os
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@db:5432/company_db")
engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

def get_schema():
    return db.get_table_info()

def run_query(query: str):
    try:
        clean_query = query.replace("```sql", "").replace("```", "").strip()
        return db.run(clean_query)
    except Exception as e:
        return f"ERROR: {str(e)}"