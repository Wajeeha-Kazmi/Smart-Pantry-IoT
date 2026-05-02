# 🥫 Smart Pantry — IoT Inventory Tracker

Smart Pantry is a low-cost IoT system designed to monitor kitchen food stock levels in real time, eliminating the need for manual inventory tracking. Built on an ESP32 microcontroller, the system uses weight and light sensors to detect when pantry items are accessed and how much is consumed over time.

---

## 📌 Overview

In many households, pantry management is done manually or not at all — leading to overbuying, running out of essentials, or wasting food. Smart Pantry addresses this by leveraging minimal hardware to provide meaningful insights into consumption habits, with no user input required.

---

## ⚙️ How It Works

The ESP32 continuously reads sensor data and serves it through a built-in lightweight web server via HTTP. Asynchronous events — such as low-stock alerts and container access detection — are transmitted using the MQTT protocol, which also allows remote configuration of alert thresholds.

A Python-based data proxy running on a local machine collects sensor readings via HTTP and MQTT, forwarding all data to an InfluxDB time-series database. A separate Python data analysis module processes historical consumption data to forecast when a product will run out, storing predictions back into InfluxDB. A Grafana dashboard provides real-time visualisation of stock levels, alerts, and forecasts.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Hardware | ESP32, weight sensor, light sensor |
| Protocols | HTTP, MQTT |
| Data Proxy | Python |
| Database | InfluxDB (time-series) |
| Forecasting | Python (data analysis module) |
| Visualisation | Grafana |

---

## ✨ Key Features

- 📦 Real-time stock monitoring with automatic low-stock alerts
- 📈 Consumption forecasting based on historical usage rates
- 🔧 Configurable alert thresholds via MQTT
- 🌐 Lightweight web server embedded on microcontroller
- 📊 Grafana dashboard for live data visualisation
- 📉 System performance evaluation: network latency & forecast Mean Square Error (MSE)

---

## 🚀 Bonus Features

- **W3C Web of Things (WoT) Integration** — device modelled as a Web Thing and exposed via a Thing Description (TD), consumed by the data proxy for standardised data acquisition
- **Telegram Bot** — remote monitoring via chat: view real-time sensor values, review triggered alerts, and configure low-stock thresholds directly through Telegram

---

## 🏗️ System Architecture

```
[ESP32 + Sensors]
      |
   HTTP / MQTT
      |
[Python Data Proxy]
      |
  [InfluxDB]
    /     \
[Python    [Grafana
Forecasting  Dashboard]
 Module]
      |
  [InfluxDB]
```

---

## 📊 Performance Evaluation

The system was evaluated on:
1. **Mean Latency** — network latency of the data acquisition process (sensor → proxy)
2. **Mean Square Error (MSE)** — accuracy of the consumption forecasting module

---

## 👩‍💻 Author

**Wajeeha Kazmi**  
MSc Electronics Engineering for Intelligent Systems, Big Data & IoT  
University of Bologna, Italy  
[LinkedIn](https://www.linkedin.com/in/wajeeha-kazmi)
