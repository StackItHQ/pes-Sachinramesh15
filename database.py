import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
from decimal import Decimal
from datetime import date

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


@contextmanager
def get_db_connection():
    """Context manager to connect to the PostgreSQL database using psycopg2."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def create_table():
    """Create a table in the database with lead_id as the primary key."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id INT PRIMARY KEY,  
                    client_name VARCHAR(255),
                    lead_status VARCHAR(50),
                    assigned_sales_rep VARCHAR(100),
                    expected_value NUMERIC,
                    close_date DATE
                );
            """)


def insert_data(values):
    """Insert or update data in the PostgreSQL database based on lead_id."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO leads (lead_id, client_name, lead_status, assigned_sales_rep, expected_value, close_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (lead_id)  -- Handle conflict based on lead_id
                DO UPDATE SET
                    client_name = EXCLUDED.client_name,
                    lead_status = EXCLUDED.lead_status,
                    assigned_sales_rep = EXCLUDED.assigned_sales_rep,
                    expected_value = EXCLUDED.expected_value,
                    close_date = EXCLUDED.close_date;
            """, values)


def convert_data_for_json(data):
    """Convert Decimal and date objects in the data to serializable formats."""
    return [
        [float(value) if isinstance(value, Decimal) else value.strftime(
            '%Y-%m-%d') if isinstance(value, date) else value for value in row]
        for row in data
    ]


def fetch_data():
    """Fetch data from the PostgreSQL database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM leads;")
            rows = cur.fetchall()
            return convert_data_for_json(rows)
