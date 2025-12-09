# scripts/check_db.py
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()  # only needed if you store config in .env

USER = os.environ.get("DB_USER") or os.environ.get("user")
PASSWORD = os.environ.get("DB_PASSWORD") or os.environ.get("password")
HOST = os.environ.get("DB_HOST") or os.environ.get("host")
PORT = os.environ.get("DB_PORT") or os.environ.get("port")
DBNAME = os.environ.get("DB_NAME") or os.environ.get("dbname")

try:
    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        sslmode='require'  # if using Supabase, require SSL
    )
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    print("DB connected. Current time:", cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print("Failed to connect:", e)
