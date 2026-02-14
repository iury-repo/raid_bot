import os
import discord 
import logging

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from discord.ext import commands, tasks
from collections import defaultdict
from flask import Flask
from threading import Thread

# Discord token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Scheduler assíncrono
scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# API endpoint
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Lista de horários para enviar mensagens
SPAWNS = [
    ("Gorgon", 1, 0), ("Gorgon", 2, 0), ("Gorgon", 3, 0), ("Gorgon", 4, 0), ("Gorgon", 5, 0),

    ("Ice Queen", 1, 45), ("Ice Queen", 3, 45), ("Ice Queen", 5, 45),
    ("Ice Queen", 12, 45), ("Ice Queen", 16, 45), ("Ice Queen", 20, 55),

    ("White Wizard", 8, 45), ("White Wizard", 12, 45),
    ("White Wizard", 16, 45), ("White Wizard", 21, 6), ("White Wizard", 0, 45),

    ("Dourados", 0, 0), ("Dourados", 4, 0), ("Dourados", 8, 0),
    ("Dourados", 12, 0), ("Dourados", 16, 0),

    ("Red Dragon", 8, 35), ("Red Dragon", 12, 35),
    ("Red Dragon", 16, 35), ("Red Dragon", 21, 6), ("Red Dragon", 0, 35),

    ("Skeleton King", 8, 25), ("Skeleton King", 12, 25),
    ("Skeleton King", 16, 25), ("Skeleton King", 21, 6), ("Skeleton King", 0, 25),
]

def adjust(hour, minute, offset=5):
    t = datetime(2000, 1, 1, hour, minute) - timedelta(minutes=offset)
    return t.hour, t.minute

alerts = defaultdict(list)

for boss, h, m in SPAWNS:
    ah, am = adjust(h, m, 5)  # 5 min antes
    alerts[(ah, am)].append(boss)

# ---------------------------------------------------------------

async def send_alert(bosses):
    channel = await bot.fetch_channel(533005103855304706)

    msg = "⚔️ Bosses spawnando em 5 minutos @everyone:\n"
    msg += "\n".join(f"• {b}" for b in bosses)

    await channel.send(msg, allowed_mentions=discord.AllowedMentions(everyone=True))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    if not scheduler.running:
        for (hour, minute), bosses in alerts.items():
            scheduler.add_job(
            send_alert,
            "cron",
            hour=hour,
            minute=minute,
            args=[bosses],
            id=f"alert_{hour}_{minute}",
            replace_existing=True
            )
        
        scheduler.start()

keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)