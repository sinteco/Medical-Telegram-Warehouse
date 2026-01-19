with stg as (
    select * from {{ ref('stg_telegram') }}
),

channel_stats as (
    select
        channel_name,
        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(*) as total_posts,
        avg(views) as avg_views
    from stg
    group by 1
)

select
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name,
    -- Simple mapping for channel type (stub logic, can be enhanced with seed data)
    case 
        when lower(channel_name) like '%pharma%' then 'Pharmaceutical'
        when lower(channel_name) like '%cosmetic%' then 'Cosmetics'
        else 'Medical'
    end as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from channel_stats
