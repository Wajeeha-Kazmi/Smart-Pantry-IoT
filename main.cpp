#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include "HX711.h"
#include <WebServer.h>
#include <time.h>

// ===== WiFi credentials =====
const char* ssid = "Fireheart";
const char* password = "Bloodbath000";

// ===== Server Endpoints =====
const char* httpEndpoint = "http://192.168.137.1:5000/data"; // Python proxy Flask server
const char* mqttServer   = "192.168.137.1";                  // Mosquitto broker

// ===== Pins =====
#define LOADCELL_DOUT_PIN 18
#define LOADCELL_SCK_PIN 19
#define LIGHT_SENSOR_PIN 34
#define LIGHT_THRESHOLD 500

// ===== Objects =====
HX711 scale;
WiFiClient espClient;
PubSubClient mqttClient(espClient);
WebServer server(80);

// ===== Functions =====
float readWeightSensor() {
  if (scale.is_ready()) return scale.get_units(10);
  Serial.println("HX711 not ready");
  return 0.0;
}

int readLightSensor() {
  return analogRead(LIGHT_SENSOR_PIN);
}

void sendMQTTEvent(const char* topic, const char* message) {
  if (mqttClient.connected()) {
    mqttClient.publish(topic, message);
    Serial.printf("MQTT published [%s]: %s\n", topic, message);
  } else {
    Serial.println("MQTT not connected!");
  }
}

void sendHTTPData(float weight, int light) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, cannot send HTTP!");
    return;
  }

  HTTPClient http;
  http.begin(httpEndpoint);
  http.addHeader("Content-Type", "application/json");

  time_t now = time(nullptr);
  String payload = "{\"sensor\":\"pantry\",\"weight\":" + String(weight) +
                   ",\"light\":" + String(light) +
                   ",\"timestamp\":" + String((unsigned long)now) + "}";

  int code = http.POST(payload);
  if (code > 0) {
    Serial.printf("HTTP Response code: %d\n", code);
  } else {
    Serial.printf("HTTP failed: %s\n", http.errorToString(code).c_str());
  }

  http.end();
}

// ===== WoT handlers =====
void handleThingDescription() {
  String json = R"({
    "@context": "https://www.w3.org/2022/wot/td/v1.1",
    "title": "Smart Pantry Sensor",
    "properties": {
      "weight": {"type": "number","readOnly": true,"forms":[{"href":"/properties/weight"}]},
      "light":  {"type": "integer","readOnly": true,"forms":[{"href":"/properties/light"}]}
    }
  })";
  server.send(200, "application/td+json", json);
}

void handleWeight() {
  float w = readWeightSensor();
  server.send(200, "application/json", "{\"weight\": " + String(w) + "}");
}

void handleLight() {
  int l = readLightSensor();
  server.send(200, "application/json", "{\"light\": " + String(l) + "}");
}

// ===== Setup =====
void setup() {
  Serial.begin(115200);

  // HX711
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(1000.f);
  scale.tare();

  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());

  // NTP
  configTime(0,0,"pool.ntp.org");
  while (time(nullptr) < 100000) { delay(500); }

  // MQTT
  mqttClient.setServer(mqttServer, 1883);
  if (mqttClient.connect("ESP32Client")) Serial.println("MQTT connected!");
  else Serial.println("MQTT failed");

  // WebServer
  server.on("/thing-description", HTTP_GET, handleThingDescription);
  server.on("/properties/weight", HTTP_GET, handleWeight);
  server.on("/properties/light", HTTP_GET, handleLight);
  server.begin();
  Serial.println("Web Server started!");
}

// ===== Loop =====
void loop() {
  mqttClient.loop();
  server.handleClient();

  float weight = abs(readWeightSensor());
  int light = readLightSensor();

  sendHTTPData(weight, light);

  if (light > LIGHT_THRESHOLD) sendMQTTEvent("smartpantry/open","Container opened");
  if (weight < 100.0) sendMQTTEvent("smartpantry/lowstock","1");

  delay(1000);
}
