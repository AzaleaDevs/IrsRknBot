import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

MESES_NOMBRE = {
    1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
    7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
}

def _fmt_eur(v: float) -> str:
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

async def mostrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    db_path = context.application.bot_data.get("DB_PATH")
    if not db_path:
        await msg.reply_text("⚠️ DB no inicializada.")
        return

    # /mostrar [n]
    try:
        n = int(context.args[0]) if context.args else 20
        n = max(1, min(n, 100))
    except ValueError:
        n = 20

    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT ID, CAMPO, MES, ANYO, IMPORTE "
                "FROM FACTURAS ORDER BY ID DESC LIMIT ?",
                (n,)
            )
            rows = await cur.fetchall()
            if not rows:
                await msg.reply_text("📭 No hay facturas registradas.")
                return

            total = sum(r["IMPORTE"] for r in rows)
            lines = [f"🗂️ Últimas {len(rows)} facturas (total parcial: {_fmt_eur(total)} €):"]
            for r in rows:
                mes_nombre = MESES_NOMBRE.get(r["MES"], str(r["MES"]))
                lines.append(
                    f"#{r['ID']} • {r['CAMPO']} • {mes_nombre} {r['ANYO']} • {_fmt_eur(r['IMPORTE'])} €"
                )
            await msg.reply_text("\n".join(lines))
    except Exception as e:
        await msg.reply_text("❌ Error al listar facturas.")
        print("[mostrar] Excepción:", e)

def get_handler():
    return CommandHandler("mostrar", mostrar)
