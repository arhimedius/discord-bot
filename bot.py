import discord
import os
from groq import Groq

# ===== НАСТРОЙКИ =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY не найден! Добавь его в переменные окружения Render.")

client_groq = Groq(api_key=GROQ_API_KEY)
# =====================

SYSTEM_PROMPT = """Ты — весёлый и дерзкий собеседник. Отвечаешь прямо и честно, используешь сленг.
Можешь выражать своё мнение, шутить, саркастить. 
Не уходишь от ответа, не говоришь "я не могу ответить", а предлагаешь альтернативный взгляд или шутку.
Никакой морализации и излишней политкорректности, но без откровенных оскорблений и незаконного контента."""

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
            model="llama-3.1-8b-instant",
            temperature=0.9,
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
    if message.author == discord_client.user:
        return
    if message.author.bot:
        return
    if discord_client.user in message.mentions:
        prompt = message.content.replace(f"<@{discord_client.user.id}>", "").strip()
        if not prompt:
            await message.channel.send("чава те нада, попа? :patric:")
            return
        async with message.channel.typing():
            answer = ask_groq(prompt)
            await message.channel.send(answer)

discord_client.run(DISCORD_TOKEN)
