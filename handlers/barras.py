import io
import re
import statistics
import traceback
from typing import List
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Backend headless (Docker)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HELP = (
    "Uso: /barras <n1> <n2> <n3> ... (valores entre 0 y 10)\n"
    "Ejemplo: /barras 6 8 3 7 10 3 5 7"
)

_num_re = re.compile(r"^[+-]?(\d+([.,]\d*)?|[.,]\d+)$")

def _is_num(tok: str) -> bool:
    return bool(_num_re.match(tok))

def _to_float(tok: str) -> float:
    return float(tok.replace(",", "."))

def _color_for(value: float) -> str:
    """Mapa de colores por tramo:
       0–1 rojo, 2–3 naranja, 4 amarillo, 5 verde, 6–7 azul, 8–9 violeta, 10 rosa.
       Se usa el valor redondeado al entero más cercano dentro [0,10].
    """
    v = max(0, min(10, round(value)))
    if 0 <= v <= 1:
        return "red"
    if 2 <= v <= 3:
        return "orange"
    if v == 4:
        return "yellow"
    if v == 5:
        return "green"
    if 6 <= v <= 7:
        return "blue"
    if 8 <= v <= 9:
        return "violet"
    return "pink"  # v == 10

async def barras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    try:
        text = msg.text or ""
        # Quitar el prefijo /barras y posible @MiBot
        parts = text.split()
        if not parts:
            await msg.reply_text(f"⚠️ Formato inválido.\n{HELP}")
            return
        if parts[0].startswith("/barras"):
            parts = parts[1:]

        if not parts:
            await msg.reply_text(f"⚠️ Faltan números.\n{HELP}")
            return

        # Parsear números (permite coma decimal)
        values: List[float] = []
        for p in parts:
            if not _is_num(p):
                await msg.reply_text(f"⚠️ '{p}' no es un número válido.\n{HELP}")
                return
            v = _to_float(p)
            # Clampear a 0..10 por si acaso
            if v < 0 or v > 10:
                await msg.reply_text("⚠️ Todos los valores deben estar entre 0 y 10.")
                return
            values.append(v)

        if not values:
            await msg.reply_text(f"⚠️ No se recibieron valores.\n{HELP}")
            return

        avg = statistics.fmean(values)

        # Preparar colores por barra
        colors = [_color_for(v) for v in values]

        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
        x = list(range(1, len(values) + 1))
        ax.bar(x, values, color=colors, edgecolor="black")
        ax.set_ylim(0, 10)
        ax.set_xlabel("Muestras")
        ax.set_ylabel("Nota")
        ax.set_title("Notas de exámenes (0–10)")
        ax.set_xticks(x)

        # Línea de media (opcional, ayuda visual)
        ax.axhline(avg, linestyle="--", linewidth=1, alpha=0.8)
        ax.text(
            0.99, avg / 10.0,
            f" media = {avg:.2f}",
            transform=ax.get_yaxis_transform(),
            ha="right", va="bottom"
        )

        # Texto de media debajo de la gráfica (debajo del área de dibujo)
        fig.text(0.5, 0.02, f"Media de todas las notas: {avg:.2f}", ha="center", va="center")

        # Exportar a PNG en memoria
        buf = io.BytesIO()
        plt.tight_layout(rect=(0, 0.05, 1, 1))  # deja espacio para el texto inferior
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        buf.name = "barras.png"

        await msg.reply_photo(photo=buf, caption="📊 Gráfico de barras (0–10)")
        buf.close()

    except Exception:
        # Log para ver en docker compose logs -f
        print("[barras] Excepción:\n" + traceback.format_exc())
        await msg.reply_text(f"❌ Error generando la gráfica.\n{HELP}")

def get_handler():
    return CommandHandler("barras", barras)
