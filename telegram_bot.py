#!/usr/bin/env python3
"""
Pro Access BD - Telegram License Generator Bot (@lovableprolicensekey_bot)
Zero-dependency Telegram Bot using Python standard library (urllib + json).

Bot Token: 8916890685:AAE9oHnAo2VrxaJjcvMJazB4vDD6kJbdwyE
"""

import os
import sys
import time
import json
import logging
import urllib.request
import urllib.parse
import ssl
from generate_license import generate_key

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8916890685:AAE9oHnAo2VrxaJjcvMJazB4vDD6kJbdwyE")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Admin Telegram User IDs (integer list). If empty [], ANYONE can generate keys.
# Example: ADMIN_IDS = [123456789]
ADMIN_IDS = []

def make_api_request(method: str, data: dict = None) -> dict:
    """Sends a request to Telegram Bot API using standard library urllib."""
    url = API_URL + method
    ctx = ssl.create_default_context()
    
    if data:
        encoded_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={'Content-Type': 'application/json'}
        )
    else:
        req = urllib.request.Request(url)
        
    try:
        with urllib.request.urlopen(req, timeout=35, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logging.error(f"API Error ({method}): {e}")
        return {"ok": False, "error": str(e)}

def is_authorized(user_id: int) -> bool:
    if not ADMIN_IDS:
        return True
    return user_id in ADMIN_IDS

def send_message(chat_id: int, text: str, reply_to_message_id: int = None, reply_markup: dict = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return make_api_request("sendMessage", payload)

def answer_callback_query(callback_query_id: str, text: str = ""):
    return make_api_request("answerCallbackQuery", {
        "callback_query_id": callback_query_id,
        "text": text
    })

def handle_start(chat_id: int, message_id: int, user_id: int):
    if not is_authorized(user_id):
        send_message(chat_id, "⛔ <b>Access Denied</b>\nYou are not authorized to use this bot.", reply_to_message_id=message_id)
        return

    text = (
        "<b>🔑 Lovable Pro Extension License Generator Bot</b>\n\n"
        "Generate authentic license keys for the Lovable Pro extension.\n\n"
        "<b>Available Commands:</b>\n"
        "• <code>/gen</code> - Interactive Key Generator\n"
        "• <code>/gen lifetime user@email.com</code> - Quick Lifetime Key\n"
        "• <code>/gen 1year user@email.com</code> - Quick 1-Year Key\n"
        "• <code>/gen 1month user@email.com</code> - Quick 1-Month Key\n"
        "• <code>/gen 7d user@email.com</code> - Quick Custom Days Key\n"
        "• <code>/id</code> - Show your Telegram User ID\n"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "♾️ Lifetime Key", "callback_data": "gen_lifetime"},
                {"text": "📅 1 Year Key", "callback_data": "gen_1year"}
            ],
            [
                {"text": "🌙 1 Month Key", "callback_data": "gen_1month"},
                {"text": "⏳ 7 Days Key", "callback_data": "gen_7d"}
            ]
        ]
    }
    send_message(chat_id, text, reply_to_message_id=message_id, reply_markup=keyboard)

def handle_gen_cmd(chat_id: int, message_id: int, user_id: int, full_text: str):
    if not is_authorized(user_id):
        send_message(chat_id, "⛔ <b>Access Denied</b>\nYou are not authorized to generate keys.", reply_to_message_id=message_id)
        return

    parts = full_text.split()
    args = parts[1:]
    
    if not args:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "♾️ Lifetime", "callback_data": "gen_lifetime"},
                    {"text": "📅 1 Year", "callback_data": "gen_1year"}
                ],
                [
                    {"text": "🌙 1 Month", "callback_data": "gen_1month"},
                    {"text": "⏳ 7 Days", "callback_data": "gen_7d"}
                ]
            ]
        }
        send_message(chat_id, "<b>Select License Duration:</b>", reply_to_message_id=message_id, reply_markup=keyboard)
        return

    l_type = args[0].lower()
    email = args[1] if len(args) > 1 else f"user_{user_id}@tg"

    try:
        key = generate_key(license_type=l_type, email=email)
        reply = (
            "✅ <b>License Key Generated Successfully!</b>\n\n"
            f"👤 <b>User:</b> <code>{email}</code>\n"
            f"🏷️ <b>Type:</b> <code>{l_type.capitalize()}</code>\n\n"
            f"🔑 <b>Key:</b>\n<code>{key}</code>\n\n"
            "<i>Tap key above to copy to clipboard!</i>"
        )
        send_message(chat_id, reply, reply_to_message_id=message_id)
    except Exception as e:
        send_message(chat_id, f"❌ Error generating key: {str(e)}", reply_to_message_id=message_id)

def handle_callback(callback_query: dict):
    cb_id = callback_query["id"]
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_id = callback_query.get("from", {}).get("id")

    if not is_authorized(user_id):
        answer_callback_query(cb_id, "⛔ Access Denied")
        return

    if data.startswith("gen_"):
        l_type = data.replace("gen_", "")
        email = f"user_{user_id}@telegram"
        try:
            key = generate_key(license_type=l_type, email=email)
            answer_callback_query(cb_id, "Key Generated!")
            reply = (
                "✅ <b>License Key Generated!</b>\n\n"
                f"👤 <b>User:</b> <code>{email}</code>\n"
                f"🏷️ <b>Type:</b> <code>{l_type.capitalize()}</code>\n\n"
                f"🔑 <b>Key:</b>\n<code>{key}</code>\n\n"
                "<i>Tap key above to copy!</i>"
            )
            send_message(chat_id, reply)
        except Exception as e:
            answer_callback_query(cb_id, f"Error: {str(e)}")

def process_update(update: dict):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]
        user_id = msg.get("from", {}).get("id", 0)
        text = msg.get("text", "").strip()

        if text.startswith("/start") or text.startswith("/help"):
            handle_start(chat_id, message_id, user_id)
        elif text.startswith("/gen") or text.startswith("/key") or text.startswith("/license"):
            handle_gen_cmd(chat_id, message_id, user_id, text)
        elif text.startswith("/id"):
            send_message(chat_id, f"🆔 Your Telegram ID: <code>{user_id}</code>", reply_to_message_id=message_id)

    elif "callback_query" in update:
        handle_callback(update["callback_query"])

def run_bot():
    logging.info("Starting Telegram License Generator Bot...")
    bot_info = make_api_request("getMe")
    if bot_info.get("ok"):
        res = bot_info["result"]
        logging.info(f"Bot connected: @{res.get('username')} ({res.get('first_name')})")
    else:
        logging.error(f"Failed to connect bot: {bot_info}")
        return

    offset = 0
    while True:
        try:
            updates = make_api_request("getUpdates", {"offset": offset, "timeout": 20})
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    process_update(update)
            else:
                time.sleep(3)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user.")
            break
        except Exception as e:
            logging.error(f"Error in polling loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
