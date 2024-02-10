import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import httpx
import asyncio

# Логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Вставьте ваш токен Telegram бота здесь
TELEGRAM_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'

# URL внешнего API
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Отправь мне что-нибудь, и я передам это во внешний API.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    async with httpx.AsyncClient() as client:
        response = await client.post(EXTERNAL_API_URL, json={'question': question})
        if response.status_code == 200:
            answer = response.json().get('answer', 'Извините, не могу обработать ваш запрос.')
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ответ от API: {answer}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при обработке вашего запроса.")

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
