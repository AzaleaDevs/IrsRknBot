import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def random_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = random.randint(1, 100)
    await update.message.reply_text(f"🎲 Tu número aleatorio es: {n}")

def get_handler():
    return CommandHandler("random", random_cmd)
