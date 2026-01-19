-- Ensure all view counts are non-negative
select *
from {{ ref('stg_telegram') }}
where views < 0
