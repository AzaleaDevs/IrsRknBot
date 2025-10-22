import io
import re
from typing import List, Tuple
from telegram import Update, FSInputFile
from telegram.ext import ContextTypes, CommandHandler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Colores básicos en español -> nombres que reconoce matplotlib
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
    "  /grafica 30 verde manzanas 20 rojo fresas 50 azul arándanos\n\n"
    "Notas:\n"
    "  - El objeto puede tener varias palabras (se toma todo hasta el siguiente número).\n"
    "  - Colores soportados: azul, rojo, verde, amarillo, morado, violeta, naranja,\n"
    "    negro, blanco, gris, cian, magenta, rosa, marrón/marron, turquesa.\n"
)

_number_re = re.compile(r"^[+-]?(\d+([.,]\d*)?|[.,]\d+)$")

def _is_number(token: str) -> bool:
    return bool(_number_re.match(token))

def _to_float(token: str) -> float:
    return float(token.replace(",", "."))

def _parse_triples(text: str) -> List[Tuple[float, str, str]]:
    """
    Devuelve lista de triples (valor, color, etiqueta) a partir de:
    <num> <color> <obj> [<num> <color> <obj> ...]
    El <obj> puede abarcar varios tokens hasta el siguiente <num>.
    """
    # Quita el prefijo del comando y menciones (/grafica@MiBot)
    cleaned = re.sub(r"^/grafica(@\w+)?\s*", "", text, flags=re.IGNORECASE).strip()
    if not cleaned:
        raise ValueError("Faltan argumentos.")

    tokens = cleaned.split()
    i = 0
    triples: List[Tuple[float, str, str]] = []

    while i < len(tokens):
        # 1) número
        if i >= len(tokens) or not _is_number(tokens[i]):
            raise ValueError(f"Se esperaba un número en la posición {i+1} (token: '{tokens[i] if i < len(tokens) else ''}').")
        value = _to_float(tokens[i])
        i += 1

        # 2) color
        if i >= len(tokens):
            raise ValueError("Falta el color después del número.")
        color = tokens[i].lower()
        i += 1

        # 3) objeto (uno o más tokens) hasta el siguiente número o fin
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
        triples = _parse_triples(msg.text or "")
    except ValueError as e:
        await msg.reply_text(f"⚠️ {e}\n\n{HELP_TEXT}")
        return

    values = [v for v, _, _ in triples]
    labels = [lbl for _, _, lbl in triples]
    total = sum(values)

    if total <= 0:
        await msg.reply_text("⚠️ La suma de los valores debe ser mayor que 0.")
        return

    # Colores: usa el color si está en el mapa, si no None (matplotlib elige)
    colors = []
    for _, col, _ in triples:
        colors.append(COLOR_MAP.get(col, None))

    # Dibujar pie chart
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

    await msg.reply_photo(
        photo=FSInputFile(buf, filename="grafica.png"),
        caption="📊 Gráfico de sectores",
    )

def get_handler():
    return CommandHandler("grafica", grafica)
