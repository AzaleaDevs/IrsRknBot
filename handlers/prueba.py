from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def prueba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("esto es una prueba")

def get_handler():
    return CommandHandler("prueba", prueba)
