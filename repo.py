from feast import Entity, BigQuerySource
from feast.types import Float32, Float64, Int64

driver = Entity(name="driver", join_keys=["driver_id"])

my_bigquery_source = BigQuerySource(
    table="fs-course-feast.feast.driver-stats",
    timestamp_field="event_timestamp"
)

driver_stats_fv = FeatureView(
    name="driver_hourly_stats_bq",
    entities=[driver], 
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64, description="Average daily trips"),
    ],
    online=True,
    source=my_bigquery_source,
    tags={"team": "driver_performance"},
)
