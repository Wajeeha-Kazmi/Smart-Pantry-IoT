from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# --- Configuration ---
TELEGRAM_BOT_TOKEN = "7879559289:AAG5Oodfp_wXtXaex12yX_EN-1HqTgEPAjs"
ESP32_IP = "192.168.137.39"
LOW_STOCK_THRESHOLD = 100.0
LIGHT_THRESHOLD = 500  

# --- Functions ---
def get_sensor_data():
    try:
        weight = requests.get(f"http://{ESP32_IP}/properties/weight").json().get("weight", 0)
        light = requests.get(f"http://{ESP32_IP}/properties/light").json().get("light", 0)
        return weight, light
    except:
        return 0, 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Smart Pantry Bot 🏠\n\nCommands:\n/status - Check sensor values\n/threshold <number> - Set low-stock alert"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weight, light = get_sensor_data()
    
    # Convert light value to container status
    container_status = "Open" if light > LIGHT_THRESHOLD else "Close"
    
    await update.message.reply_text(
        f"Weight: {weight} g\ncontainer: {container_status}\nLow-stock threshold: {LOW_STOCK_THRESHOLD} g\n(Light: {light})"
    )
    
    if weight < LOW_STOCK_THRESHOLD:
        await update.message.reply_text(f"🚨 LOW STOCK! Weight ({weight} g) below threshold!")

async def threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global LOW_STOCK_THRESHOLD
    try:
        LOW_STOCK_THRESHOLD = float(context.args[0])
        await update.message.reply_text(f"✅ Low-stock threshold set to {LOW_STOCK_THRESHOLD} g")
    except:
        await update.message.reply_text("Usage: /threshold <number>")

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("threshold", threshold))
    
    print("Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
