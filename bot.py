import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import httpx
import asyncio

# Вставьте токен вашего бота здесь
TELEGRAM_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'

# URL внешнего API для обработки сообщений
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    await update.message.reply_text('Привет! Я бот, который обрабатывает сообщения через внешнее API.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения, отправляя их на внешнее API и возвращая ответ."""
    text = update.message.text
    # Отправляем действие "печатает"
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Асинхронная отправка запроса к внешнему API
    async with httpx.AsyncClient() as client:
        response = await client.post(EXTERNAL_API_URL, headers={'Content-Type': 'application/json'}, json={'question': text})
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', 'Извините, не могу обработать ваш запрос.')
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text('Произошла ошибка при обработке вашего запроса.')

def main():
    """Запускает бота."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
