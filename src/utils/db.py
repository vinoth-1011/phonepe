import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_conn():
    """Return a live psycopg2 connection using .env settings."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", 5432)),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )
