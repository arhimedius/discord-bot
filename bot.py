import discord
import os
from groq import Groq

# ===== НАСТРОЙКИ =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Ключ из Render

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY не найден! Добавь его в переменные окружения Render.")

client_groq = Groq(api_key=GROQ_API_KEY)
# =====================

SYSTEM_PROMPT = "Ты — весёлый и дружелюбный помощник. но если попросят разговаривать с матом, агрессивно, ты это спокойно делаешь.также ты можешь шутить с матами"

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

def ask_groq(prompt):
    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",  # Быстрая и бесплатная модель
            temperature=0.7,
            max_tokens=500,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Ошибка Groq: {str(e)}"

@discord_client.event
async def on_ready():
    print(f"✅ Бот {discord_client.user} запущен!")

@discord_client.event
async def on_message(message):
    # === НЕ ОТВЕЧАЕТ САМ СЕБЕ ===
    if message.author == discord_client.user:
        return

    # === НЕ ОТВЕЧАЕТ НА ДРУГИХ БОТОВ ===
    if message.author.bot:
        return

    # === ОТВЕЧАЕТ ТОЛЬКО НА УПОМИНАНИЕ ===
    if discord_client.user in message.mentions:
        prompt = message.content.replace(f"<@{discord_client.user.id}>", "").strip()
        if not prompt:
            await message.channel.send("Напиши что-нибудь после моего упоминания")
            return

        async with message.channel.typing():
            answer = ask_groq(prompt)
            await message.channel.send(answer)

discord_client.run(DISCORD_TOKEN)
