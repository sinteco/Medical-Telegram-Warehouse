-- Ideally we would use dbt_date package, but for simplicity/universality we'll generate dates here.
-- Generating a range of dates covering likely data periods (e.g., 2020-2030)

with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2030-01-01' as date)"
    ) }}
)

select
    date_day,
    {{ dbt_utils.generate_surrogate_key(['date_day']) }} as date_key,
    to_char(date_day, 'Day') as day_name,
    extract(isodow from date_day) as day_of_week,
    extract(day from date_day) as day_of_month,
    to_char(date_day, 'Month') as month_name,
    extract(month from date_day) as month_of_year,
    extract(quarter from date_day) as quarter,
    extract(year from date_day) as year,
    case when extract(isodow from date_day) in (6, 7) then true else false end as is_weekend
from date_spine
