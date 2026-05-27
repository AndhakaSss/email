import time
from flask import Flask, request
from datetime import datetime
import requests
from config import TELEGRAM_CONFIG, RATE_LIMIT_SECONDS, IGNORE_USER_AGENTS

app = Flask(__name__)

# Simple in-memory rate limiter (resets on Railway restart — fine for this)
rate_cache = {}

def should_alert(ip, campaign_id):
    key = f"{ip}:{campaign_id}"
    now = time.time()
    if key in rate_cache:
        if now - rate_cache[key] < RATE_LIMIT_SECONDS:
            return False
    rate_cache[key] = now
    return True

def send_telegram_alert(ip, user_agent, campaign_id):
    bot_token = TELEGRAM_CONFIG["bot_token"]
    chat_id = TELEGRAM_CONFIG["chat_id"]
    
    message = (
        f"🚨 *EMAIL OPENED* 🚨\n"
        f"📁 Campaign: `{campaign_id}`\n"
        f"⏰ Time: `{datetime.utcnow().isoformat()}`\n"
        f"🌐 IP: `{ip}`\n"
        f"📱 UA: `{user_agent[:80]}`"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, json=payload, timeout=2)
    except:
        pass  # Silent fail

@app.route('/pixel.png')
def pixel():
    campaign_id = request.args.get('c', 'unknown')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Filter out scanners
    for bot in IGNORE_USER_AGENTS:
        if bot.lower() in user_agent.lower():
            return b'', 204  # No content, don't log
    
    # Rate limit
    if not should_alert(ip, campaign_id):
        return b'', 204
    
    # Send notification
    send_telegram_alert(ip, user_agent, campaign_id)
    
    # 1x1 transparent GIF
    gif_data = bytes([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
        0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF,
        0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
        0x01, 0x00, 0x3B
    ])
    
    return gif_data, 200, {'Content-Type': 'image/gif'}

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)