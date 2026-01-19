-- Ensure all view counts are non-negative
select *
from "medical_warehouse"."dwh"."stg_telegram"
where views < 0