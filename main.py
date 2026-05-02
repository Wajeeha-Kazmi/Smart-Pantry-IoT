from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timezone

app = Flask(__name__)

# --- InfluxDB setup ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "X-Wda8HF7ecWqW3b_MFwgKVS--13GmO8tEu2NmAxmntMszSn4XBEdzfCGrW-M3RsQlT8yHk3V2UeHqKI6l-iZA=="
INFLUX_ORG = "my-org"
INFLUX_BUCKET = "smart_pantry"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

# --- MQTT setup ---
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883)
mqtt_client.loop_start()

# --- Flask route for ESP32 HTTP POST ---
@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data:
        return "Invalid JSON", 400

    weight = float(data.get("weight", 0))
    light  = int(data.get("light", 0))
    timestamp = int(data.get("timestamp", datetime.now().timestamp()))

    # Write to InfluxDB
    point = (
        Point("pantry")
        .field("weight", weight)
        .field("light", light)
        .time(datetime.fromtimestamp(timestamp, tz=timezone.utc), WritePrecision.NS)
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    # Publish MQTT event if necessary
    if light > 500:
        mqtt_client.publish("smartpantry/open", "Container opened")
    if weight < 100:
        mqtt_client.publish("smartpantry/lowstock", "1")

    return jsonify({"status":"ok"}), 200

# --- Run Flask server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
