import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "medical_warehouse"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", "5432")
    )

def load_json_to_db(json_file_path):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for msg in data:
            # Handle potential missing keys or types
            msg_date = datetime.fromisoformat(msg['message_date']) if msg.get('message_date') else None
            
            insert_query = """
            INSERT INTO raw_telegram_data 
            (channel_name, message_id, message_date, message_text, has_media, image_path, views, forwards, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (channel_name, message_id) DO UPDATE SET
                views = EXCLUDED.views,
                forwards = EXCLUDED.forwards,
                message_text = EXCLUDED.message_text,
                image_path = EXCLUDED.image_path,
                ingested_at = CURRENT_TIMESTAMP;
            """
            
            cur.execute(insert_query, (
                msg.get('channel_name'),
                msg.get('message_id'),
                msg_date,
                msg.get('message_text'),
                msg.get('has_media'),
                msg.get('image_path'),
                msg.get('views'),
                msg.get('forwards'),
                json.dumps(msg)
            ))
            
        conn.commit()
        logger.info(f"Loaded {len(data)} records from {json_file_path}")
        
    except Exception as e:
        logger.error(f"Error loading {json_file_path}: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    base_path = "data/raw/telegram_messages"
    if not os.path.exists(base_path):
        logger.error(f"Data path {base_path} does not exist.")
        return

    # Walk through the directory structure
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                logger.info(f"Processing {full_path}")
                load_json_to_db(full_path)

if __name__ == "__main__":
    main()
