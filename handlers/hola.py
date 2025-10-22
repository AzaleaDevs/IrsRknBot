from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hola mundo")

def get_handler():
    return CommandHandler("hola", hola)
