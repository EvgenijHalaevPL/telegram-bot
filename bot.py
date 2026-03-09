import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# Теперь код берет токен из настроек Render, а не светит его в интернете
API_TOKEN = os.getenv('BOT_TOKEN')
CURRENCY_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

async def get_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()

        # Запрос курса EUR
        eur_response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
        eur_data = eur_response.json()
        
        usd_to_pln = data['rates'].get('PLN')
        eur_to_pln = eur_data['rates'].get('PLN')
        today = datetime.now().strftime("%d.%m.%Y")

        if usd_to_pln and eur_to_pln:
            await update.message.reply_text(
                f'Курс на {today}\n'
                f'USD/PLN: {usd_to_pln}\n'
                f'EUR/PLN: {eur_to_pln}'
            )
        else:
            await update.message.reply_text('Не удалось получить курсы валют.')
    except Exception as e:
        await update.message.reply_text("Ошибка при получении данных. Попробуйте позже.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Используйте команду /rate для получения курсов USD/PLN и EUR/PLN.')

if __name__ == '__main__':
    # Проверка, что токен вообще задан
    if not API_TOKEN:
        print("Ошибка: Переменная BOT_TOKEN не найдена в настройках!")
    else:
        application = ApplicationBuilder().token(API_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('rate', get_exchange_rate))
        print("Бот запущен...")
        application.run_polling()
