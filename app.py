import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client

app = Flask(__name__)
# API details aapke wahi rahenge
bot = Client("my_userbot", api_id=39965722, api_hash="e60871c8fe0fff37e2b299fbf839523a", session_string="...")

stats = {"total": 0, "sent": 0, "errors": 0, "logs": []}

async def run_bot_logic():
    print("Bot starting...")
    # 1. Purani requests fetch karo
    async for dialog in bot.get_dialogs():
        if dialog.chat.type in ["channel", "supergroup"]:
            try:
                async for request in bot.get_chat_join_requests(dialog.chat.id):
                    await handle_dm(request)
            except Exception as e:
                print(f"Error in {dialog.chat.title}: {e}")
    
    # 2. Listener start karo
    @bot.on_chat_join_request()
    async def new_request(client, request):
        await handle_dm(request)
    
    await bot.start()
    print("Bot is listening...")

async def handle_dm(request):
    stats["total"] += 1
    try:
        await bot.approve_chat_join_request(request.chat.id, request.from_user.id)
        # Saved messages check karo
        async for msg in bot.get_chat_history("me", limit=1):
            await bot.send_message(request.from_user.id, msg.text)
        stats["sent"] += 1
        stats["logs"].append(f"Sent to: {request.from_user.first_name}")
    except Exception as e:
        stats["errors"] += 1
        stats["logs"].append(f"Err: {str(e)[:20]}")

def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_logic())
    loop.run_forever()

@app.route('/')
def index():
    return f"Logs: <pre>{chr(10).join(stats['logs'][-20:])}</pre>"

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
