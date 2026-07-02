import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client

app = Flask(__name__)

API_ID = 39965722
API_HASH = "e60871c8fe0fff37e2b299fbf839523a"
SESSION_STRING = "..." # Aapki wahi purani session string yaha rahegi

bot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
stats = {"total": 0, "sent": 0, "skipped": 0, "logs": []}

async def process_pending_requests():
    """Bot start hote hi saare channels ki pending requests check karega"""
    async for dialog in bot.get_dialogs():
        if dialog.chat.type in ["channel", "supergroup"]:
            try:
                async for request in bot.get_chat_join_requests(dialog.chat.id):
                    # Purani request process karein
                    await handle_dm(request)
                    await asyncio.sleep(2) # Spam se bachne ke liye gap
            except:
                continue

async def handle_dm(request):
    """DM bhejane ka common function"""
    stats["total"] += 1
    try:
        await bot.approve_chat_join_request(request.chat.id, request.from_user.id)
        async for message in bot.get_chat_history("me", limit=1):
            await bot.send_message(request.from_user.id, message.text)
        stats["sent"] += 1
        stats["logs"].append(f"Sent DM to: {request.from_user.first_name}")
    except Exception as e:
        stats["skipped"] += 1
        stats["logs"].append(f"Error: {e}")

@bot.on_chat_join_request()
async def on_new_request(client, request):
    await handle_dm(request)

@app.route('/')
def index():
    return f"<html><body><h1>Bot Status: Running</h1><pre>{chr(10).join(stats['logs'][-20:])}</pre></body></html>"

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Pehle purani requests process karein, phir listener chalaein
    loop.run_until_complete(process_pending_requests())
    bot.run()

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
