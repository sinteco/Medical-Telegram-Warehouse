import os
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Configuration
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
PHONE = os.getenv('TG_PHONE')

CHANNELS = [
    'CheMed123',
    'lobelia4cosmetics',
    'tikvahpharma'
]

# Create directories
os.makedirs('logs', exist_ok=True)
logger.add("logs/scraper.log", rotation="1 day")

async def scrape_channel(client, channel_name):
    logger.info(f"Scraping channel: {channel_name}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    data_dir = f"data/raw/telegram_messages/{today}"
    image_dir = f"data/raw/images/{channel_name}"
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    
    extracted_data = []
    
    try:
        entity = await client.get_entity(channel_name)
        async for message in client.iter_messages(entity, limit=None):
            msg_data = {
                'message_id': message.id,
                'channel_name': channel_name,
                'message_date': message.date.isoformat(),
                'message_text': message.text,
                'has_media': bool(message.media),
                'image_path': None,
                'views': message.views,
                'forwards': message.forwards
            }
            
            if message.media and isinstance(message.media, MessageMediaPhoto):
                image_filename = f"{message.id}.jpg"
                image_path = os.path.join(image_dir, image_filename)
                
                # Check if image already exists to avoid re-downloading
                if not os.path.exists(image_path):
                    logger.info(f"Downloading image for message {message.id}")
                    await client.download_media(message, file=image_path)
                    msg_data['image_path'] = image_path
                else:
                    msg_data['image_path'] = image_path

            extracted_data.append(msg_data)
            
        # Save to JSON
        output_file = os.path.join(data_dir, f"{channel_name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Successfully scraped {len(extracted_data)} messages from {channel_name}")

    except Exception as e:
        logger.error(f"Error scraping {channel_name}: {e}")

async def main():
    async with TelegramClient('medical_scraper', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == '__main__':
    if not API_ID or not API_HASH:
        logger.error("API_ID or API_HASH not found in .env")
        exit(1)
        
    logger.info("Starting Telegram Scraper")
    # For running in an event loop
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
