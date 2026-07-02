import asyncio, threading, os
from flask import Flask, render_template_string
from pyrogram import Client

app = Flask(__name__)

# APNE CREDENTIALS YAHAN PASTE KAREIN
bot = Client(
    "my_userbot", 
    api_id=39965722, 
    api_hash="e60871c8fe0fff37e2b299fbf839523a", 
    session_string="BQHLIOIAq4r4xq8OeFmOENuJkV2hao-omYBLUEd0WQPmoGN-vjfTUkk8p8wsZoGxBKiajjouNsZjbELrjotHNbHYImMW3qvG8ECDteJnBuCJptW3nytJO6vLXqBqf__CGGOPeqh-XEYe3vnSsjOhgw0evOq6_u3997eMy0xylEJWuBSshuP_zNx8vqf3jlZFArYVflX_0yYKxOuohH3Vi8W52r2yfvAdnfwqV5ovv8rJroU1BXRcWqg6KrIabHa0qzyu6jOEEuQyYBVvI0684fwJo6qDwfrINzrO0brivuLN34oCSTtew2iXpWbetOcHp-I3J5mtGrbU0BrT-8FRXU9lDdVBuwAAAABDtEAWAA"
)

stats = {"sent": 0, "errors": 0, "logs": []}

HTML = """
<!DOCTYPE html><html><head><title>Bot Dashboard</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<meta http-equiv="refresh" content="5"></head>
<body class="bg-dark text-light p-5">
    <h1 class="text-center mb-4">Telegram Auto-DM System</h1>
    <div class="row text-center">
        <div class="col-6"><div class="card bg-success text-white p-3"><h3>Sent</h3><h2>{{stats.sent}}</h2></div></div>
        <div class="col-6"><div class="card bg-danger text-white p-3"><h3>Errors</h3><h2>{{stats.errors}}</h2></div></div>
    </div>
    <h3 class="mt-4">Live Activity Logs:</h3>
    <pre class="bg-black text-success p-3" style="height: 300px; overflow-y: scroll;">{{logs}}</pre>
</body></html>
"""

async def handle_dm(request):
    try:
        # 1. Join Request Accept
        await bot.approve_chat_join_request(request.chat.id, request.from_user.id)
        
        # 2. Saved Messages se text uthao
        async for msg in bot.get_chat_history("me", limit=1):
            if msg.text:
                await bot.send_message(request.from_user.id, msg.text)
                stats["sent"] += 1
                stats["logs"].append(f"SUCCESS: {request.from_user.first_name}")
                break
    except Exception as e:
        stats["errors"] += 1
        stats["logs"].append(f"ERROR: {str(e)[:15]}")

async def run_bot():
    print("Bot is starting...")
    # Purani requests fetch karo
    async for dialog in bot.get_dialogs():
        if dialog.chat.type in ["channel", "supergroup"]:
            try:
                async for r in bot.get_chat_join_requests(dialog.chat.id):
                    await handle_dm(r)
            except: continue
    
    # Listener start karo
    @bot.on_chat_join_request()
    async def new_req(c, r): await handle_dm(r)
    await bot.start()
    print("Bot is now listening...")

@app.route('/')
def index():
    return render_template_string(HTML, stats=stats, logs="\n".join(stats["logs"][-20:]))

def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())
    loop.run_forever()

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
