import os
import csv
import psycopg2
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

def init_yolo_table():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        query = """
        CREATE TABLE IF NOT EXISTS raw.yolo_detections (
            id SERIAL PRIMARY KEY,
            channel_name TEXT,
            message_id BIGINT,
            image_path TEXT,
            detected_class TEXT,
            confidence_score FLOAT,
            image_category TEXT,
            all_detections TEXT,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(channel_name, message_id)
        );
        """
        cur.execute(query)
        conn.commit()
        logger.info("Initialized raw.yolo_detections table.")
    except Exception as e:
        logger.error(f"Error initializing table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def load_yolo_csv(csv_path):
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            for row in rows:
                insert_query = """
                INSERT INTO raw.yolo_detections
                (channel_name, message_id, image_path, detected_class, confidence_score, image_category, all_detections)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (channel_name, message_id) DO UPDATE SET
                    detected_class = EXCLUDED.detected_class,
                    confidence_score = EXCLUDED.confidence_score,
                    image_category = EXCLUDED.image_category,
                    all_detections = EXCLUDED.all_detections,
                    ingested_at = CURRENT_TIMESTAMP;
                """
                cur.execute(insert_query, (
                    row['channel_name'],
                    row['message_id'],
                    row['image_path'],
                    row['detected_class'],
                    float(row['confidence_score']),
                    row['image_category'],
                    row['all_detections']
                ))
            
            conn.commit()
            logger.info(f"Loaded {len(rows)} detections into database.")
            
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_yolo_table()
    load_yolo_csv("data/yolo_detections.csv")
