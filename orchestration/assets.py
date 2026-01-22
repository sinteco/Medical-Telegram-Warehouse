import os
import subprocess
from dagster import asset, Output, MetadataValue

@asset(description="Scrape Telegram data")
def telegram_raw_data():
    """
    Runs the Telegram scraper to download messages and images.
    """
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    return Output(
        value="Scraping completed",
        metadata={
            "logs": MetadataValue.md(result.stdout)
        }
    )

@asset(deps=[telegram_raw_data], description="Load raw messages to PostgreSQL")
def postgres_raw_data():
    """
    Loads scraped JSON data into the raw.telegram_messages table.
    """
    # Initialize DB first in case it's fresh
    subprocess.run(["python", "scripts/init_db.py"], check=True)
    
    result = subprocess.run(["python", "scripts/load_data.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Load failed: {result.stderr}")
        
    return Output(
        value="Data loaded",
        metadata={
            "logs": MetadataValue.md(result.stdout)
        }
    )

@asset(deps=[telegram_raw_data], description="Run YOLO Object Detection and Load Results")
def yolo_results():
    """
    Runs YOLO detection on downloaded images and loads results to DB.
    """
    # Run Detection
    res_detect = subprocess.run(["python", "src/yolo_detect.py"], capture_output=True, text=True)
    if res_detect.returncode != 0:
        raise Exception(f"YOLO failed: {res_detect.stderr}")

    # Load Results
    res_load = subprocess.run(["python", "scripts/load_yolo.py"], capture_output=True, text=True)
    if res_load.returncode != 0:
        raise Exception(f"YOLO Load failed: {res_load.stderr}")

    return Output(
        value="YOLO Processing Completed",
        metadata={
            "detection_logs": MetadataValue.md(res_detect.stdout),
            "load_logs": MetadataValue.md(res_load.stdout)
        }
    )

@asset(deps=[postgres_raw_data, yolo_results], description="Run dbt transformations")
def dbt_transformations():
    """
    Runs `dbt build` to transform data into the star schema.
    """
    dbt_dir = "medical_warehouse"
    # Ensure deps are installed
    subprocess.run(["dbt", "deps"], cwd=dbt_dir, check=True)
    
    result = subprocess.run(["dbt", "build"], cwd=dbt_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"dbt build failed: {result.stderr}")
        
    return Output(
        value="dbt Models Built",
        metadata={
            "logs": MetadataValue.md(result.stdout)
        }
    )
