# config.py — keep this out of git if you're paranoid
# But on Railway you can just upload it directly

TELEGRAM_CONFIG = {
    "bot_token": "8618098753:AAGfuO5YDTv_0WjSkbuxJhMrVZseo9bFogg",
    "chat_id": "-1004294003714"
}

# Optional: rate limiting to avoid duplicate alerts from pre-fetching
RATE_LIMIT_SECONDS = 60  # Only one alert per IP per campaign per minute

# Optional: filter out known bots and scanners
IGNORE_USER_AGENTS = [
    "Googlebot",
    "AhrefsBot",
    "SemrushBot",
    "Bytespider",
    "PetalBot"
]
