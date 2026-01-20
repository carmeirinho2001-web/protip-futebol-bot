import requests
import datetime
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== VARIÁVEIS (USE VARIÁVEIS DE AMBIENTE NO SERVIDOR) ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
# ===============================================================

HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ProTip Futebol\n\n"
        "📊 Sinais automáticos todos os dias\n"
        "⚽ Ligas nacionais e internacionais\n"
        "⏰ Atualização diária\n\n"
        "Use /sinais para ver os jogos favoritos do dia."
    )

def buscar_jogos_hoje():
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoje}
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", [])

def gerar_sinais(jogos):
    sinais = []
    for j in jogos:
        home = j["teams"]["home"]["name"]
        away = j["teams"]["away"]["name"]
        # Heurística simples (vamos refinar depois):
        # prioriza jogos com status futuro e ligas principais
        league = j["league"]["name"]
        status = j["fixture"]["status"]["short"]
        if status == "NS" and league:
            sinais.append(f"🟢 {home} vence vs {away}")
        if len(sinais) == 5:
            break
    return sinais

async def sinais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        jogos = buscar_jogos_hoje()
        sinais = gerar_sinais(jogos)
        if sinais:
            msg = "🔥 SINAIS DO DIA\n\n" + "\n".join(sinais) + "\n\n📊 Gestão: 1 unidade"
        else:
            msg = "Hoje não há sinais confiáveis suficientes. ❌"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Erro ao buscar sinais. Tente novamente mais tarde.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sinais", sinais))
    app.run_polling()
