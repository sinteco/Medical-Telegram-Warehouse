import os
import csv
import torch
from ultralytics import YOLO
from loguru import logger
from glob import glob
from pathlib import Path

# Initialize YOLO model
# Using yolov8n (nano) for speed on local machine
try:
    model = YOLO('yolov8n.pt')
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    exit(1)

DATA_DIR = Path("data/raw/images")
OUTPUT_FILE = Path("data/yolo_detections.csv")

def classify_image(detections):
    """
    Classify image based on detected objects.
    Logic:
    - Promotional: Person + (bottle OR cup OR bowl OR box)
    - Product Display: (bottle OR cup OR bowl OR box), NO person
    - Lifestyle: Person, NO product-like objects
    - Other: No person, no product-like objects
    """
    labels = [d['class_name'] for d in detections]
    
    has_person = 'person' in labels
    
    # Common objects that might represent medical products/packaging
    product_objects = {'bottle', 'cup', 'bowl', 'box', 'suitcase', 'backpack', 'handbag'}
    has_product = any(obj in labels for obj in product_objects)
    
    if has_person and has_product:
        return 'promotional'
    elif has_product and not has_person:
        return 'product_display'
    elif has_person and not has_product:
        return 'lifestyle'
    else:
        return 'other'

def process_images():
    # Find all jpg images recursively
    image_paths = glob(str(DATA_DIR / "**/*.jpg"), recursive=True)
    
    if not image_paths:
        logger.warning(f"No images found in {DATA_DIR}")
        return

    logger.info(f"Found {len(image_paths)} images to process...")
    
    results_data = []
    
    for i, img_path in enumerate(image_paths):
        try:
            # Extract metadata from path
            # Structure: data/raw/images/{channel_name}/{message_id}.jpg
            path_obj = Path(img_path)
            message_id = path_obj.stem
            channel_name = path_obj.parent.name
            
            # Run inference
            results = model(img_path, verbose=False)[0]
            
            detections = []
            for box in results.boxes:
                start_class_id = int(box.cls[0])
                class_name = model.names[start_class_id]
                conf = float(box.conf[0])
                
                detections.append({
                    'class_name': class_name,
                    'confidence': conf
                })
            
            # Determine primary classification
            image_category = classify_image(detections)
            
            # For reporting, we might want the primary object or just the category.
            # We'll store the category and the raw detections (as a string repr for simplicity in CSV)
            # In a real DB, we might normalize detections into a separate table, 
            # but per requirements "detected_class" usually implies the most relevant one or we rely on the category.
            # Let's pick the highest confidence object as 'detected_class' if any exists.
            
            best_detection = max(detections, key=lambda x: x['confidence']) if detections else None
            primary_class = best_detection['class_name'] if best_detection else 'none'
            primary_conf = best_detection['confidence'] if best_detection else 0.0
            
            results_data.append({
                'channel_name': channel_name,
                'message_id': message_id,
                'image_path': str(img_path),
                'detected_class': primary_class,
                'confidence_score': primary_conf,
                'image_category': image_category,
                'all_detections': str([d['class_name'] for d in detections])
            })
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(image_paths)} images")
                
        except Exception as e:
            logger.error(f"Error processing {img_path}: {e}")

    # Save to CSV
    if results_data:
        keys = results_data[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results_data)
        logger.info(f"Saved results to {OUTPUT_FILE}")
    else:
        logger.warning("No results generated.")

if __name__ == "__main__":
    process_images()
