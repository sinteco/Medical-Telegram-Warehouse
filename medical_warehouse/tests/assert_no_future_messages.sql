-- Ensure no messages have a date in the future (relative to run time)
select *
from {{ ref('stg_telegram') }}
where message_date > now()
