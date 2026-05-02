import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
from sklearn.linear_model import LinearRegression

# InfluxDB settings
client = InfluxDBClient(
    url="http://localhost:8086",
    token="X-Wda8HF7ecWqW3b_MFwgKVS--13GmO8tEu2NmAxmntMszSn4XBEdzfCGrW-M3RsQlT8yHk3V2UeHqKI6l-iZA==",
    org="my-org"  
)
query_api = client.query_api()
write_api = client.write_api()

# Flux query with pivot() to get weight data for the last 7 days
query = '''
from(bucket:"smart_pantry")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "pantry" and r._field == "weight")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

# Query data as dataframe
result = query_api.query_data_frame(org="my-org", query=query)

if not result.empty:
    result["_time"] = pd.to_datetime(result["_time"])
    result = result.sort_values("_time")
    # Convert _time to Unix timestamp (seconds)
    result["timestamp"] = result["_time"].astype(int) // 10**9

    X = result[["timestamp"]]
    y = result["weight"]

    # Fit linear regression model
    model = LinearRegression().fit(X, y)

    # Calculate depletion timestamp:
    # depletion_ts = current_time + (current_weight / abs(rate_of_weight_change))
    depletion_ts = int((y.iloc[-1] / -model.coef_[0]) + X.iloc[-1].values[0])
    depletion_date = datetime.fromtimestamp(depletion_ts)
    print(f"Forecast depletion date: {depletion_date}")

    # Write forecast to InfluxDB with a proper timestamp 
    forecast_point = (
        Point("forecast")
        .field("depletion_ts", depletion_ts)
        .time(datetime.utcnow(), WritePrecision.NS)  # timestamp of write
    )
    write_api.write(bucket="smart_pantry", org="my-org", record=forecast_point)
else:
    print("No data found in InfluxDB.")

client.close()
