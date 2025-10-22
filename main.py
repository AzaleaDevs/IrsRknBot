import os
import importlib
import pkgutil
import handlers
from telegram.ext import Application

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def load_handlers(app: Application) -> None:
    """
    Carga automáticamente todos los módulos en handlers/*
    y, si exponen get_handler(), lo registra en la app.
    """
    for _, module_name, _ in pkgutil.iter_modules(handlers.__path__):
        module_fullname = f"{handlers.__name__}.{module_name}"
        try:
            module = importlib.import_module(module_fullname)
            if hasattr(module, "get_handler"):
                handler = module.get_handler()
                app.add_handler(handler)
                print(f"✅ Handler cargado: {module_fullname}")
            else:
                print(f"ℹ️  {module_fullname} no define get_handler(), omitido.")
        except Exception as e:
            print(f"❌ Error cargando {module_fullname}: {e}")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta la variable de entorno BOT_TOKEN")

    app = Application.builder().token(BOT_TOKEN).build()
    load_handlers(app)

    print("🤖 Bot iniciado con carga dinámica de comandos…")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
