
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Ensure all view counts are non-negative
select *
from "medical_warehouse"."dwh"."stg_telegram"
where views < 0
  
  
      
    ) dbt_internal_test