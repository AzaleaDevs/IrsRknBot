import os
import importlib
import pkgutil
import handlers
from telegram.ext import Application
from lib.db import init_db, DEFAULT_DB_PATH

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def load_handlers(app: Application):
    for _, module_name, _ in pkgutil.iter_modules(handlers.__path__):
        module_fullname = f"{handlers.__name__}.{module_name}"
        try:
            module = importlib.import_module(module_fullname)
            if hasattr(module, "get_handler"):
                app.add_handler(module.get_handler())
                print(f"✅ Handler cargado: {module_fullname}")
            else:
                print(f"ℹ️  {module_fullname} no define get_handler(), omitido.")
        except Exception as e:
            print(f"❌ Error cargando {module_fullname}: {e}")

async def on_startup(app: Application):
    await init_db(DEFAULT_DB_PATH)                   # ← crea la BD y tabla FACTURAS
    app.bot_data["DB_PATH"] = DEFAULT_DB_PATH        # ← por si la usan los handlers

def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta la variable de entorno BOT_TOKEN")
    app = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()
    load_handlers(app)
    print("🤖 Bot iniciado con base de datos SQLite…")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
