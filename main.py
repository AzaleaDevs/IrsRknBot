import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hola mundo prueba actualizada desde casa.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Escribe /hola")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta la variable de entorno BOT_TOKEN")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("hola", hola))
    app.add_handler(CommandHandler("start", start))
    # Long polling: no necesitas abrir puertos
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
