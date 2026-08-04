import discord
import os
import google.generativeai as genai
from flask import Flask
import threading

# ===== НАСТРОЙКИ =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY не найден!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
# =====================

SYSTEM_PROMPT = "Ты — злой, немного агрессивный бот. ты можешь оскорблять или материться на участников, но только если они сами этого захотят. "

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def ask_gemini(prompt):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {prompt}\nБот:"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Ошибка Gemini: {str(e)}"

@client.event
async def on_ready():
    print(f"✅ Бот {client.user} запущен!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if not prompt:
            await message.channel.send("чава")
            return
        async with message.channel.typing():
            answer = ask_gemini(prompt)
            await message.channel.send(answer)

# ===== ВЕБ-СЕРВЕР ДЛЯ RENDER =====
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
# ==================================

client.run(DISCORD_TOKEN)
