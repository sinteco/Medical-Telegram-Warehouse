with detections as (
    select * from {{ source('telegram', 'yolo_detections') }}
),

messages as (
    select * from {{ ref('fct_messages') }}
),

dates as (
    select * from {{ ref('dim_dates') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
)

select
    d.message_id,
    m.channel_key,
    m.date_key,
    d.image_path,
    d.detected_class,
    d.confidence_score,
    d.image_category,
    d.all_detections
from detections d
join messages m on d.message_id = m.message_id
-- We join on message_id assuming uniqueness per channel might be needed, 
-- but given our schema fct_messages has message_id. 
-- Note: If message_id is not unique across channels, we should join on (channel_name, message_id).
-- But fct_messages uses surrogate keys. 
-- Let's assume unique extraction or refine join if needed.
-- Correct join needs channel context. 
-- Since 'raw.yolo_detections' has channel_name, we can join to dim_channel first to get key.
join channels c on d.channel_name = c.channel_name
and c.channel_key = m.channel_key
