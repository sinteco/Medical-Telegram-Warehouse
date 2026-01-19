-- Ensure no messages have a date in the future (relative to run time)
select *
from "medical_warehouse"."dwh"."stg_telegram"
where message_date > now()