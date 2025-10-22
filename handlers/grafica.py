import io
import re
import traceback
from typing import List, Tuple
from telegram import Update               # ⬅️ SIN FSInputFile
from telegram.ext import ContextTypes, CommandHandler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ... (resto del archivo igual que lo tenías)

async def grafica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.effective_message
    try:
        text = msg.text or ""
        print(f"[grafica] Mensaje recibido: {text}")

        triples = _parse_triples(text)
        print(f"[grafica] Triples parseados: {triples}")

        values = [v for v, _, _ in triples]
        labels = [lbl for _, _, lbl in triples]
        total = sum(values)
        if total <= 0:
            await msg.reply_text("⚠️ La suma de los valores debe ser mayor que 0.")
            return

        colors = [COLOR_MAP.get(c, None) for _, c, _ in triples]

        fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
        ax.pie(values, labels=labels, autopct=lambda p: f"{p:.1f}%", startangle=90,
               colors=colors if any(colors) else None)
        ax.axis("equal")

        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        buf.name = "grafica.png"          # ⬅️ nombre de archivo para Telegram

        await msg.reply_photo(
            photo=buf,                    # ⬅️ enviar el buffer directamente
            caption="📊 Gráfico de sectores",
        )
        print("[grafica] Imagen enviada correctamente.")

    except ValueError as e:
        print(f"[grafica] Error de validación: {e}")
        await msg.reply_text(f"⚠️ {e}\n\n{HELP_TEXT}")
    except Exception as e:
        print("[grafica] Excepción no controlada:\n" + traceback.format_exc())
        await msg.reply_text("❌ Hubo un error generando la gráfica. Revisa el formato o los logs del bot.")

def get_handler():
    return CommandHandler("grafica", grafica)
