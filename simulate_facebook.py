# simulate_facebook.py
import requests
import json

WEBHOOK_URL = "https://faceautomation.onrender.com/webhook"  # Replace with your webhook URL if remote

# Simulate a message event
fake_event = {
    "object": "page",
    "entry": [
        {
            "messaging": [
                {
                    "sender": {"id": "1234567890123456"},
                    "recipient": {"id": "604893402700631"},
                    "timestamp": 1234567890,
                    "message": {"text": "Hello! This is a test message from the bot."}
                }
            ]
        }
    ]
}

response = requests.post(WEBHOOK_URL, json=fake_event)
print("Status code:", response.status_code)
print("Response:", response.text)
