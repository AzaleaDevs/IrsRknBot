import io
import re
import traceback
from typing import List, Tuple
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Backend headless
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Colores básicos ES -> matplotlib
COLOR_MAP = {
    "azul": "blue",
    "rojo": "red",
    "verde": "green",
    "amarillo": "yellow",
    "morado": "purple",
    "violeta": "violet",
    "naranja": "orange",
    "negro": "black",
    "blanco": "white",
    "gris": "gray",
    "cian": "cyan",
    "magenta": "magenta",
    "rosa": "pink",
    "marron": "brown",
    "marrón": "brown",
    "turquesa": "turquoise",
}

HELP_TEXT = (
    "Uso: /grafica <numero> <color> <objeto> [<numero> <color> <objeto> ...]\n"
    "Ejemplos:\n"
    "  /grafica 94 azul cielo 6 rojo fuego\n"
    "  /grafica 30 verde ventas online 70 rojo ventas tienda\n"
    "Notas:\n"
    "  - El objeto puede tener varias palabras (se toma todo hasta el siguiente número).\n"
)

_number_re = re.compile(r"^[+-]?(\d+([.,]\d*)?|[.,]\d+)$")

def _is_number(token: str) -> bool:
    return bool(_number_re.match(token))

def _to_float(token: str) -> float:
    return float(token.replace(",", "."))

def _parse_triples(text: str) -> List[Tuple[float, str, str]]:
    cleaned = re.sub(r"^/grafica(@\w+)?\s*", "", text, flags=re.IGNORECASE).strip()
    if not cleaned:
        raise ValueError("Faltan argumentos.")

    tokens = cleaned.split()
    i = 0
    triples: List[Tuple[float, str, str]] = []

    while i < len(tokens):
        if i >= len(tokens) or not _is_number(tokens[i]):
            raise ValueError(f"Se esperaba un número en la posición {i+1} (token: '{tokens[i] if i < len(tokens) else ''}').")
        value = _to_float(tokens[i]); i += 1

        if i >= len(tokens):
            raise ValueError("Falta el color después del número.")
        color = tokens[i].lower(); i += 1

        if i >= len(tokens):
            raise ValueError("Falta el objeto/etiqueta después del color.")
        start = i
        while i < len(tokens) and not _is_number(tokens[i]):
            i += 1
        label = " ".join(tokens[start:i]).strip()
        if not label:
            raise ValueError("Etiqueta vacía; especifica el objeto después del color.")

        triples.append((value, color, label))

    return triples

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
        ax.pie(
            values,
            labels=labels,
            autopct=lambda p: f"{p:.1f}%",
            startangle=90,
            colors=colors if any(colors) else None,
        )
        ax.axis("equal")

        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        buf.name = "grafica.png"  # nombre lógico para Telegram

        await msg.reply_photo(photo=buf, caption="📊 Gráfico de sectores")
        buf.close()
        print("[grafica] Imagen enviada correctamente.")

    except ValueError as e:
        print(f"[grafica] Error de validación: {e}")
        await msg.reply_text(f"⚠️ {e}\n\n{HELP_TEXT}")
    except Exception:
        print("[grafica] Excepción no controlada:\n" + traceback.format_exc())
        await msg.reply_text("❌ Hubo un error generando la gráfica. Revisa el formato o los logs del bot.")

def get_handler():
    return CommandHandler("grafica", grafica)
