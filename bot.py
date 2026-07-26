import discord
import requests
import json
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FOLDER_ID = "b1gpjlgfcf3vrqaahjop"
API_KEY = "AQVN3v1Bv0-3o2qyoZH0ciVtGXFf32OsMTQb8rPg"

SYSTEM_PROMPT = "Ты — злой тролль. Ты можешь материться если взбесишься, или же даже оскорблять или шутить"

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
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
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
            return f"Ошибка API: {response.status_code}"
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

client.run(DISCORD_TOKEN)
