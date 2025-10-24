import io
import math
import traceback
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HELP = (
    "Uso: /radar <categoria1> <valor1> <categoria2> <valor2> ...\n"
    "Ejemplo: /radar fuerza 8 agilidad 6 inteligencia 9 carisma 7 resistencia 5\n"
    "Notas: Los valores deben estar entre 0 y 10."
)

def _parse_args(text: str):
    """Extrae pares (categoria, valor) del texto."""
    parts = text.split()
    if parts and parts[0].startswith("/radar"):
        parts = parts[1:]

    if len(parts) < 2 or len(parts) % 2 != 0:
        raise ValueError("Formato inválido. Debes enviar pares <categoria valor>.")

    labels, values = [], []
    for i in range(0, len(parts), 2):
        label = parts[i]
        try:
            val = float(parts[i + 1].replace(",", "."))
        except ValueError:
            raise ValueError(f"El valor '{parts[i + 1]}' no es numérico.")
        if val < 0 or val > 10:
            raise ValueError(f"El valor de '{label}' debe estar entre 0 y 10.")
        labels.append(label.capitalize())
        values.append(val)

    return labels, values

async def radar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    try:
        text = msg.text or ""
        labels, values = _parse_args(text)
        n = len(values)

        # Cerrar el polígono
        values += values[:1]
        angles = [n / float(n) * 2 * math.pi for n in range(len(values))]
        # o mejor aún:
        angles = [i / float(n) * 2 * math.pi for i in range(n)]
        angles += angles[:1]

        fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(6, 6), dpi=150)
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)

        plt.xticks(angles[:-1], labels)
        ax.set_rlabel_position(0)
        plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"], color="gray", size=8)
        plt.ylim(0, 10)

        ax.plot(angles, values, linewidth=2, linestyle="solid", color="purple")
        ax.fill(angles, values, "violet", alpha=0.25)

        plt.title("🌐 Gráfico de Radar", size=14, weight="bold", pad=20)

        buf = io.BytesIO()
        plt.tight_layout(pad=3)
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        buf.name = "radar.png"

        await msg.reply_photo(photo=buf, caption="📊 Radar de atributos")
        buf.close()

    except ValueError as e:
        await msg.reply_text(f"⚠️ {e}\n\n{HELP}")
    except Exception:
        print("[radar] Excepción:\n" + traceback.format_exc())
        await msg.reply_text("❌ Error generando el radar.\n\n" + HELP)

def get_handler():
    return CommandHandler("radar", radar)
