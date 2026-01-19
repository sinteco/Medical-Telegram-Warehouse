import os
import time
import psycopg2
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def get_db_connection():
    max_retries = 5
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "medical_warehouse"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                port=os.getenv("DB_PORT", "5432")
            )
            return conn
        except Exception as e:
            logger.warning(f"Database connection failed (attempt {i+1}/{max_retries}): {e}")
            time.sleep(2)
    raise Exception("Could not connect to database after multiple retries")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create raw table to store the JSON dump directly or parsed fields
    # Here we store parsed fields for easier dbt modeling, but raw JSON is also an option.
    # Given the requirements "Extract ... load into Data Lake ... load into Postgres ... dbt"
    # we'll store a raw representation.
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_telegram_data (
        id SERIAL PRIMARY KEY,
        channel_name TEXT,
        message_id BIGINT,
        message_date TIMESTAMP,
        message_text TEXT,
        has_media BOOLEAN,
        image_path TEXT,
        views INTEGER,
        forwards INTEGER,
        raw_json JSONB,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(channel_name, message_id)
    );
    """
    
    try:
        cur.execute(create_table_query)
        conn.commit()
        logger.info("Successfully created/verified 'raw_telegram_data' table.")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
