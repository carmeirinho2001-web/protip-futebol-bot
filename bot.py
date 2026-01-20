import requests
import datetime
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
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
    free = []
    vip = []

    for j in jogos:
        if j["fixture"]["status"]["short"] != "NS":
            continue

        home = j["teams"]["home"]["name"]
        away = j["teams"]["away"]["name"]
        league = j["league"]["name"]

        vip.append(f"🟢 {home} vence vs {away} ({league})")
        vip.append(f"🔵 Over 1.5 gols — {home} x {away}")

        if len(free) < 3:
            free.append(f"🟢 {home} vence ({league})")

        if len(vip) >= 12:
            break

    return free, vip

async def envio_automatico(app):
    enviado = None

    while True:
        agora = datetime.datetime.now()
        hoje = agora.date()

        if agora.hour == 10 and agora.minute == 0 and enviado != hoje:
            jogos = buscar_jogos_hoje()
            free, vip = gerar_sinais(jogos)

            if free and CANAL_FREE_ID:
                await app.bot.send_message(
                    chat_id=CANAL_FREE_ID,
                    text="🔥 SINAIS GRATUITOS – HOJE\n\n" +
                         "\n".join(free) +
                         "\n\n👉 Entre no VIP"
                )

            if vip and CANAL_VIP_ID:
                await app.bot.send_message(
                    chat_id=CANAL_VIP_ID,
                    text="💎 SINAIS VIP – HOJE\n\n" +
                         "\n".join(vip) +
                         "\n\n📊 Gestão: 1 unidade"
                )

            enviado = hoje

        await asyncio.sleep(60)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ProTip Futebol\n\n"
        "📊 Sinais automáticos todos os dias\n"
        "💎 Canal VIP disponível\n"
        "⏰ Envio diário automático"
    )

async def post_init(app):
    app.create_task(envio_automatico(app))

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
