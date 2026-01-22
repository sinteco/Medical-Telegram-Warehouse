from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from . import database, schemas

app = FastAPI(title="Medical Data Warehouse API", description="API for accessing medical telegram data analytics.")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Medical Data Warehouse API. Visit /docs for documentation."}

@app.get("/health", tags=["Root"])
async def health_check():
    return {"status": "ok"}

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct], tags=["Analytics"])
async def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the most frequently mentioned terms/products across all channels.
    Note: A real implementation would use NLP extraction. 
    Here we use a simple naive split on the message text for demonstration 
    or query pre-calculated top terms if available.
    For this task, we will do a simple word count on the fly (not efficient for large data) 
    or assume we are just listing messages for now? 
    
    Actually, the requirement says "most frequently mentioned terms".
    Let's implement a simple SQL based word frequency if possible, or just return random/mock if NLP is out of scope.
    Constraint: "postgres" and "dbt".
    Let's try to query the fct_messages and do a simple split. 
    Warning: This is slow in SQL. Ideally dbt does this. 
    Let's assume we are returning the top longest words > 5 chars as a proxy for "products".
    """
    try:
        # Simple heuristic: Split text, filter small words, count.
        # This is a bit heavy for an API endpoint without a pre-calc table, but fits the 'dwh' query requirement.
        query = text("""
            SELECT 
                word, 
                count(*) as frequency 
            FROM (
                SELECT regexp_split_to_table(lower(message_text), '\s+') as word 
                FROM dwh.fct_messages 
                WHERE message_text IS NOT NULL
            ) t
            WHERE length(word) > 4
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).fetchall()
        return [{"term": row[0], "frequency": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity], tags=["Analytics"])
async def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns posting activity (daily count) for a specific channel.
    """
    try:
        query = text("""
            SELECT 
                to_char(d.date_day, 'YYYY-MM-DD') as date_str,
                count(f.message_id) as post_count,
                coalesce(sum(f.view_count), 0) as total_views
            FROM dwh.fct_messages f
            JOIN dwh.dim_channels c ON f.channel_key = c.channel_key
            JOIN dwh.dim_dates d ON f.date_key = d.date_key
            WHERE c.channel_name = :channel_name
            GROUP BY 1
            ORDER BY 1
        """)
        result = db.execute(query, {"channel_name": channel_name}).fetchall()
        
        if not result:
            # Check if channel exists to return 404
            check = db.execute(text("SELECT 1 FROM dwh.dim_channels WHERE channel_name = :name"), {"name": channel_name}).fetchone()
            if not check:
                raise HTTPException(status_code=404, detail="Channel not found")
            return []
            
        return [
            {"date": row[0], "post_count": row[1], "total_views": row[2]} 
            for row in result
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/messages", response_model=List[schemas.MessageSearch], tags=["Search"])
async def search_messages(query: str = Query(..., min_length=3), limit: int = 20, db: Session = Depends(get_db)):
    """
    Searches for messages containing a specific keyword.
    """
    try:
        sql = text("""
            SELECT 
                f.message_id,
                c.channel_name,
                f.message_date,
                f.message_text,
                f.view_count
            FROM dwh.fct_messages f
            JOIN dwh.dim_channels c ON f.channel_key = c.channel_key
            WHERE f.message_text ILIKE :search_term
            ORDER BY f.message_date DESC
            LIMIT :limit
        """)
        # Add wildcards for ILIKE
        search_term = f"%{query}%"
        result = db.execute(sql, {"search_term": search_term, "limit": limit}).fetchall()
        
        return [
            {
                "message_id": row[0],
                "channel_name": row[1],
                "date": row[2],
                "text": row[3],
                "views": row[4]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStats], tags=["Analytics"])
async def get_visual_stats(db: Session = Depends(get_db)):
    """
    Returns statistics about image usage across channels (from YOLO detections).
    """
    try:
        # If fct_image_detections exists, use it. Otherwise fallback or handle error.
        # We assume fct_image_detections exists in dwh schema.
        sql = text("""
            SELECT 
                image_category,
                count(*) as count
            FROM dwh.fct_image_detections
            GROUP BY 1
            ORDER BY 2 DESC
        """)
        
        # Calculate total for percentage
        result = db.execute(sql).fetchall()
        total = sum(row[1] for row in result)
        
        stats = []
        for row in result:
            count = row[1]
            percentage = (count / total * 100) if total > 0 else 0
            stats.append({
                "image_category": row[0],
                "count": count,
                "percentage": round(percentage, 2)
            })
            
        return stats
    except Exception as e:
        # Graceful fallback if table doesn't exist yet (Task 4 dependency)
        if "relation" in str(e) and "does not exist" in str(e):
             return []
        raise HTTPException(status_code=500, detail=str(e))
