# webhook.py
import os
import json
import logging
from flask import Flask, request, Response
import requests

# ---------------------
# Flask App Setup
# ---------------------
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# Tokens
# ---------------------
PAGE_ACCESS_TOKEN = "EAHJTYAULctYBPcUwWzuDz7NrbC9gyFREogcTnAWoKuECFQTab4GcvnJWk0n0weADKloft2rFXVl6VvZA5tAH6wH9mZCZB2QUzaSznXBOvOZCBAqh2k2ut2ERo151Y18dSH9dt9Hgx7ETIThFtyLO9HmTiVHRbZAMCDdh18idUe6Uhm18WgIw4WuilbpJVQSpaqe3zEfzFtwZDZD"
VERIFY_TOKEN = "123darcscar"

# ---------------------
# Config
# ---------------------
FOODPANDA_URL = "https://www.foodpanda.ph/restaurant/locg/pedros-old-manila-rd"
MENU_URL = "https://darcscar.github.io/menu.pdf"
PHONE_NUMBER = "0424215968"
PAGE_NAME = "Pedro's Classic and Asian Cuisine"
FB_GRAPH = "https://graph.facebook.com/v19.0"

# ---------------------
# Helpers
# ---------------------
def call_send_api(psid, message_data):
    """Send a message to a user via Send API."""
    url = f"{FB_GRAPH}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": message_data,
    }
    try:
        r = requests.post(url, params=params, json=payload, timeout=20)
        r.raise_for_status()
        logger.info(f"Sent message to PSID {psid}: {message_data}")
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Send API error: {e}")
        return None

# ---------------------
# Menu Messages
# ---------------------
def send_vertical_menu(psid):
    """Sends a vertical menu using Generic Template."""
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "📋 View Menu",
                        "subtitle": "See all dishes",
                        "buttons": [{"type": "postback", "title": "Open Menu", "payload": "Q_VIEW_MENU"}],
                    },
                    {
                        "title": "🛵 Order on Foodpanda",
                        "subtitle": "Order online",
                        "buttons": [{"type": "web_url", "title": "Open Foodpanda", "url": FOODPANDA_URL}],
                    },
                    {
                        "title": "🍴 Advance Order",
                        "subtitle": "Schedule in advance",
                        "buttons": [{"type": "postback", "title": "Order Ahead", "payload": "Q_ADVANCE_ORDER"}],
                    },
                    {
                        "title": "📞 Contact Us",
                        "subtitle": f"Reach us at {PHONE_NUMBER}",
                        "buttons": [{"type": "postback", "title": "Call Us", "payload": "Q_CONTACT"}],
                    },
                ]
            }
        }
    }
    return call_send_api(psid, msg)

def send_menu(psid):
    msg = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "📋 Here’s our full menu:",
                "buttons": [{"type": "web_url", "title": "Open Menu", "url": MENU_URL}],
            },
        }
    }
    return call_send_api(psid, msg)

def send_contact_info(psid):
    text = f"📞 Contact us at {PHONE_NUMBER}."
    return call_send_api(psid, {"text": text})

def send_advance_order_info(psid):
    text = (
        "✅ We accept advance orders!\n\n"
        "• Foodpanda: schedule inside the app.\n"
        "• Dine-in/Pickup: reply with your order and preferred time."
    )
    return call_send_api(psid, {"text": text})

# ---------------------
# Payload Router
# ---------------------
def handle_payload(psid, payload):
    if payload in {"Q_VIEW_MENU", "P_VIEW_MENU"}:
        send_menu(psid)
    elif payload in {"Q_FOODPANDA", "P_FOODPANDA"}:
        call_send_api(psid, {"text": f"Order here: {FOODPANDA_URL}"})
    elif payload in {"Q_ADVANCE_ORDER", "P_ADVANCE_ORDER"}:
        send_advance_order_info(psid)
    elif payload in {"Q_CONTACT", "P_CONTACT"}:
        send_contact_info(psid)
    else:
        send_vertical_menu(psid)

# ---------------------
# Webhook Routes
# ---------------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode", "")
        token = request.args.get("hub.verify_token", "")
        challenge = request.args.get("hub.challenge", "")
        logger.info(f"Webhook verification request: mode={mode}, token={token}, challenge={challenge}")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(challenge, status=200, mimetype="text/plain")
        return Response("Forbidden", status=403)

    if request.method == "POST":
        data = request.get_json()
        logger.info(f"Incoming webhook event: {json.dumps(data, indent=2)}")

        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    psid = event.get("sender", {}).get("id")
                    if not psid:
                        continue
                    logger.info(f"User PSID: {psid}")

                    if "message" in event:
                        msg = event["message"]
                        if msg.get("quick_reply"):
                            handle_payload(psid, msg["quick_reply"].get("payload"))
                        elif "text" in msg:
                            send_vertical_menu(psid)
                    elif "postback" in event:
                        payload = event["postback"].get("payload")
                        handle_payload(psid, payload)
        return Response("EVENT_RECEIVED", status=200)

# ---------------------
# Run App
# ---------------------
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    logger.info(f"Starting Flask app on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
