
  create view "medical_warehouse"."dwh"."stg_telegram__dbt_tmp"
    
    
  as (
    with source as (
    select * from "medical_warehouse"."raw"."telegram_messages"
),

renamed as (
    select
        id as raw_id,
        channel_name,
        message_id,
        message_date,
        message_text,
        coalesce(message_text, '') as clean_text,
        length(coalesce(message_text, '')) as message_length,
        has_media,
        image_path,
        views,
        forwards,
        ingested_at
    from source
    where message_date is not null
)

select * from renamed
  );