with stg as (
    select * from {{ ref('stg_telegram') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
),

dates as (
    select * from {{ ref('dim_dates') }}
)

select
    stg.message_id,
    c.channel_key,
    d.date_key,
    stg.message_date,  -- Keeping full timestamp useful even with date_key
    stg.clean_text as message_text,
    stg.message_length,
    stg.views as view_count,
    stg.forwards as forward_count,
    stg.has_media as has_image
from stg
left join channels c on stg.channel_name = c.channel_name
left join dates d on cast(stg.message_date as date) = d.date_day
