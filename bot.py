import requests
import datetime
import os
import asyncio
from telegram import Bot, Update
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

async def envio_automatico(app):
    bot: Bot = app.bot
    enviado_hoje = None

    while True:
        agora = datetime.datetime.now()
        hoje = agora.date()

        # horário do envio (10:00)
        if agora.hour == 10 and agora.minute == 0 and enviado_hoje != hoje:
            jogos = buscar_jogos_hoje()
            free, vip = gerar_sinais(jogos)

            if free:
                await bot.send_message(
                    chat_id=CANAL_FREE_ID,
                    text="🔥 SINAIS GRATUITOS – HOJE\n\n" +
                         "\n".join(free) +
                         "\n\n👉 Entre no VIP para mais sinais"
                )

            if vip:
                await bot.send_message(
                    chat_id=CANAL_VIP_ID,
                    text="💎 SINAIS VIP – HOJE\n\n" +
                         "\n".join(vip) +
                         "\n\n📊 Gestão: 1 unidade"
                )

            enviado_hoje = hoje

        await asyncio.sleep(60)  # checa a cada 1 minuto

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ProTip Futebol\n\n"
        "📊 Sinais automáticos todos os dias\n"
        "💎 Canal VIP disponível\n"
        "⏰ Envio diário automático"
    )

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    asyncio.create_task(envio_automatico(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
