from feast import Entity, BigQuerySource, FeatureView, Field
from feast.types import Float32, Float64, Int64

driver = Entity(name="driver", join_keys=["driver_id"])
