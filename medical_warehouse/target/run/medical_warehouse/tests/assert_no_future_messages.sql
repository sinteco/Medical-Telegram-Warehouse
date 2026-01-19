
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Ensure no messages have a date in the future (relative to run time)
select *
from "medical_warehouse"."dwh"."stg_telegram"
where message_date > now()
  
  
      
    ) dbt_internal_test