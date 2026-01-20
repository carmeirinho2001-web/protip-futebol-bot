import requests
import datetime
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

# Ligas principais (IDs da API-Football)
LIGAS_PRINCIPAIS = [
    2,    # Champions League
    3,    # Europa League
    39,   # Premier League
    40,   # Championship
    140,  # La Liga
    135,  # Serie A
    78,   # Bundesliga
    61,   # Ligue 1
    71,   # Brasileirão Série A
    72    # Brasileirão Série B
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ProTip Futebol\n\n"
        "🔥 Sinais automáticos TODOS OS DIAS\n"
        "⚽ Apenas jogos de HOJE\n"
        "🏆 Principais ligas\n\n"
        "Use /sinais para ver os palpites de hoje."
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
        league_id = j["league"]["id"]
        status = j["fixture"]["status"]["short"]

        if league_id in LIGAS_PRINCIPAIS and status == "NS":
            home = j["teams"]["home"]["name"]
            away = j["teams"]["away"]["name"]
            league = j["league"]["name"]

            sinais.append(f"🟢 {home} vence vs {away} ({league})")

        if len(sinais) >= 10:  # MAIS PALPITES
            break

    return sinais

async def sinais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        jogos = buscar_jogos_hoje()
        sinais = gerar_sinais(jogos)

        if sinais:
            msg = "🔥 SINAIS DE HOJE\n\n" + "\n".join(sinais) + "\n\n📊 Gestão: 1 unidade"
        else:
            msg = "❌ Nenhum jogo confiável encontrado para hoje."

        await update.message.reply_text(msg)

    except Exception:
        await update.message.reply_text("Erro ao buscar os sinais de hoje.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sinais", sinais))
    app.run_polling()

