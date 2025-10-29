import re
import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Mapa de meses ES -> número
MESES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "SETIEMBRE": 9, "OCTUBRE": 10,
    "NOVIEMBRE": 11, "DICIEMBRE": 12
}
# Aceptaremos abreviaturas típicas
ABRV = {
    "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SEP": 9, "SET": 9, "OCT": 10, "NOV": 11, "DIC": 12
}

def _parse_mes(token: str) -> int:
    t = token.strip().upper().replace("É", "E").replace("Á","A").replace("Í","I").replace("Ó","O").replace("Ú","U")
    # número directo
    if t.isdigit():
        m = int(t)
        if 1 <= m <= 12:
            return m
        raise ValueError("MES debe estar entre 1 y 12.")
    # nombre
    if t in MESES:
        return MESES[t]
    if t in ABRV:
        return ABRV[t]
    raise ValueError("MES no reconocido. Usa nombre (EJ: JUNIO) o número (1-12).")

def _parse_anyo(token: str) -> int:
    if not token.isdigit():
        raise ValueError("AÑO debe ser numérico (EJ: 2025).")
    y = int(token)
    if y < 2000:
        raise ValueError("AÑO debe ser >= 2000.")
    return y

def _parse_importe(token: str) -> float:
    # Soporta 1.234,56  |  1234,56  |  1234.56
    t = token.strip()
    # Elimina separadores de miles (.)
    t = re.sub(r"\.(?=\d{3}(\D|$))", "", t)
    # Cambia coma decimal por punto
    t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        raise ValueError("IMPORTE inválido. Ej: 45,78")
    if v < 0:
        raise ValueError("IMPORTE debe ser >= 0.")
    # Redondeo a 2 decimales para guardar “limpio”
    return round(v, 2)

def _fmt_eur(v: float) -> str:
    # 1234.5 -> 1.234,50
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

async def facturar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    db_path = context.application.bot_data.get("DB_PATH")
    if not db_path:
        await msg.reply_text("⚠️ DB no inicializada.")
        return

    # /facturar GAS JUNIO 2025 45,78
    args = context.args
    if len(args) != 4:
        await msg.reply_text("Uso: /facturar <CAMPO> <MES> <AÑO> <IMPORTE>\nEj: /facturar GAS JUNIO 2025 45,78")
        return

    try:
        campo = args[0].strip().upper()
        mes = _parse_mes(args[1])
        anyo = _parse_anyo(args[2])
        importe = _parse_importe(args[3])
    except ValueError as e:
        await msg.reply_text(f"⚠️ {e}\nEjemplo: /facturar LUZ 10 2025 43,55")
        return

    try:
        async with aiosqlite.connect(db_path) as db:
            cur = await db.execute(
                "INSERT INTO FACTURAS (CAMPO, MES, ANYO, IMPORTE) VALUES (?, ?, ?, ?)",
                (campo, mes, anyo, importe)
            )
            await db.commit()
            new_id = cur.lastrowid
        await msg.reply_text(
            f"✅ Factura registrada #{new_id}\n"
            f"• CAMPO: {campo}\n"
            f"• PERÍODO: {mes:02d}/{anyo}\n"
            f"• IMPORTE: {_fmt_eur(importe)} €"
        )
    except Exception as e:
        await msg.reply_text("❌ Error al guardar la factura.")
        print("[facturar] Excepción:", e)

def get_handler():
    return CommandHandler("facturar", facturar)
