import requests
import datetime
import os
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

# IDs dos canais (substitua depois)
CANAL_FREE_ID = os.getenv("CANAL_FREE_ID")
CANAL_VIP_ID = os.getenv("CANAL_VIP_ID")

HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

def buscar_jogos_hoje():
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoje}
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    return r.json().get("response", [])

def gerar_sinais(jogos):
    sinais_free = []
    sinais_vip = []

    for j in jogos:
        if j["fixture"]["status"]["short"] != "NS":
            continue

        home = j["teams"]["home"]["name"]
        away = j["teams"]["away"]["name"]
        league = j["league"]["name"]

        sinais_vip.append(f"🟢 {home} vence vs {away} ({league})")
        sinais_vip.append(f"🔵 Over 1.5 gols — {home} x {away}")

        if len(sinais_free) < 3:
            sinais_free.append(f"🟢 {home} vence ({league})")

        if len(sinais_vip) >= 12:
            break

    return sinais_free, sinais_vip

async def enviar_sinais_automatico(context: ContextTypes.DEFAULT_TYPE):
    jogos = buscar_jogos_hoje()
    free, vip = gerar_sinais(jogos)

    bot: Bot = context.bot

    if free:
        msg_free = "🔥 SINAIS GRATUITOS – HOJE\n\n" + "\n".join(free) + \
                   "\n\n👉 Entre no VIP para mais sinais"
        await bot.send_message(chat_id=CANAL_FREE_ID, text=msg_free)

    if vip:
        msg_vip = "💎 SINAIS VIP – HOJE\n\n" + "\n".join(vip) + \
                  "\n\n📊 Gestão: 1 unidade"
        await bot.send_message(chat_id=CANAL_VIP_ID, text=msg_vip)

async def start(update, context):
    await update.message.reply_text(
        "🤖 ProTip Futebol\n\n"
        "📊 Sinais automáticos todos os dias\n"
        "💎 Conteúdo VIP disponível\n"
        "📲 Acompanhe pelo canal"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    job_queue = app.job_queue

    job_queue.run_daily(
        enviar_sinais_automatico,
        time=datetime.time(hour=10, minute=0)
    )

    app.run_polling()
