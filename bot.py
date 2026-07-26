import discord
import requests
import json
import os
import threading
from flask import Flask

# ===== НАСТРОЙКИ =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FOLDER_ID = "b1gpjlgfcf3vrqaahjop"
API_KEY = "AQVN3v1Bv0-3o2qyoZH0ciVtGXFf32OsMTQb8rPg"
SYSTEM_PROMPT = "Ты — злой тролль. Отвечаешь язвительно, с сарказмом, можешь оскорблять в шутку."
# =====================

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def ask_yandex(prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['result']['alternatives'][0]['message']['text']
        else:
            return f"Ошибка API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

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
            await message.channel.send("Напиши что-нибудь после моего упоминания")
            return
        async with message.channel.typing():
            answer = ask_yandex(prompt)
            await message.channel.send(answer)

# ===== ВЕБ-СЕРВЕР ДЛЯ RENDER (исправлен) =====
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"

def run_web():
    # Получаем порт из переменной окружения Render или используем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    # Запускаем сервер на всех интерфейсах (0.0.0.0)
    app.run(host='0.0.0.0', port=port)

# Запускаем веб-сервер в отдельном потоке, чтобы не блокировать бота
web_thread = threading.Thread(target=run_web, daemon=True)
web_thread.start()
# =============================================

# Запускаем бота Discord
client.run(DISCORD_TOKEN)
