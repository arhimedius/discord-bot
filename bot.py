import discord
import os
import google.generativeai as genai

# ===== НАСТРОЙКИ =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ключ из Render, а не из кода!
# =====================

# Проверяем, есть ли ключ
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY не найден! Добавь его в переменные окружения Render.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = "Ты — злой тролль. ты можешь отвечать с матом, агрессивно, оскорбляя, но только если в начале напишут QQ. без этого ты обычный бот с юмором, отвечаешь язвительно и с юмором "

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
            await message.channel.send("Напиши что-нибудь после моего упоминания")
            return
        async with message.channel.typing():
            answer = ask_gemini(prompt)
            await message.channel.send(answer)

client.run(DISCORD_TOKEN)
