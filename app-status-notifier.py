import psutil
import time
import requests
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CONFIG_FILE = "config.json"
DEFAULT_INTERVAL = 5


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    process_name = input("Enter process name to monitor: ").strip().lower()

    config = {
        "process_name": process_name,
        "check_interval": DEFAULT_INTERVAL
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    return config


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data, timeout=10)


config = load_config()
PROCESS_NAME = config["process_name"]
CHECK_INTERVAL = config["check_interval"]

print(f"Monitoring process: {PROCESS_NAME}")

last_count = 0

while True:
    current_count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and PROCESS_NAME in proc.info['name'].lower():
                current_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if last_count > 0 and current_count < last_count:
        send_telegram_message(
            f"Your application has stopped.: {PROCESS_NAME}\n"
            f"Remaining instances: {current_count}"
        )

    last_count = current_count
    time.sleep(CHECK_INTERVAL)
