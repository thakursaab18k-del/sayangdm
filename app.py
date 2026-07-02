import os
import threading
from flask import Flask
from pyrogram import Client
from pyrogram.types import ChatJoinRequest

app = Flask(__name__)

# Credentials (Fixed)
API_ID = 39965722
API_HASH = "e60871c8fe0fff37e2b299fbf839523a"
SESSION_STRING = "BQHLIOIAq4r4xq8OeFmOENuJkV2hao-omYBLUEd0WQPmoGN-vjfTUkk8p8wsZoGxBKiajjouNsZjbELrjotHNbHYImMW3qvG8ECDteJnBuCJptW3nytJO6vLXqBqf__CGGOPeqh-XEYe3vnSsjOhgw0evOq6_u3997eMy0xylEJWuBSshuP_zNx8vqf3jlZFArYVflX_0yYKxOuohH3Vi8W52r2yfvAdnfwqV5ovv8rJroU1BXRcWqg6KrIabHa0qzyu6jOEEuQyYBVvI0684fwJo6qDwfrINzrO0brivuLN34oCSTtew2iXpWbetOcHp-I3J5mtGrbU0BrT-8FRXU9lDdVBuwAAAABDtEAWAA"

# Stats
stats = {"total": 0, "sent": 0, "skipped": 0, "logs": []}

bot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_chat_join_request()
async def handler(client, request: ChatJoinRequest):
    allowed_channels = [int(id.strip()) for id in os.environ.get("CHANNEL_IDS", "").split(",") if id.strip()]
    
    if request.chat.id not in allowed_channels:
        return

    stats["total"] += 1
    try:
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
        async for message in client.get_chat_history("me", limit=1):
            await client.send_message(request.from_user.id, message.text)
        stats["sent"] += 1
        stats["logs"].append(f"Sent DM to: {request.from_user.first_name}")
    except Exception as e:
        stats["skipped"] += 1
        stats["logs"].append(f"Error: {e}")

# Inline Dashboard
@app.route('/')
def index():
    return f"""
    <html>
    <head><meta http-equiv="refresh" content="3">
    <style>body{{background:#121212;color:white;font-family:sans-serif;padding:20px;}}
    .card{{background:#1e1e1e;padding:20px;border-radius:10px;display:inline-block;margin:10px;}}
    pre{{background:#000;color:#0f0;padding:15px;height:300px;overflow-y:auto;}}</style></head>
    <body><h1>Telegram Auto-DM System</h1>
    <div class='card'>TOTAL: {stats['total']}</div>
    <div class='card'>SENT: {stats['sent']}</div>
    <div class='card'>SKIPPED: {stats['skipped']}</div>
    <h3>Live Logs:</h3><pre>{chr(10).join(stats['logs'][-20:])}</pre></body></html>
    """

def run_bot(): bot.run()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
