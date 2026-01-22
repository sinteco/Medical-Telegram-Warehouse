from dagster import Definitions, load_assets_from_modules, define_asset_job, ScheduleDefinition
from . import assets

all_assets = load_assets_from_modules([assets])

# Define a job that materializes all assets
pipeline_job = define_asset_job(
    name="medical_pipeline_job",
    selection=all_assets
)

# Schedule: Run daily at midnight
daily_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="0 0 * * *",  # Daily at midnight
)

defs = Definitions(
    assets=all_assets,
    jobs=[pipeline_job],
    schedules=[daily_schedule],
)
