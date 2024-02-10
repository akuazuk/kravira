#API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'

import logging
from aiogram import Bot, Dispatcher, executor, types
import httpx
import asyncio

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, и я перешлю его во внешний API.")

# Обработчик текстовых сообщений
@dp.message_handler(content_types=['text'])
async def handle_text_message(message: types.Message):
    # Получаем текст сообщения от пользователя
    user_question = message.text
    
    # Создаем асинхронный HTTP клиент
    async with httpx.AsyncClient() as client:
        # Отправляем запрос к внешнему API
        response = await client.post(
            EXTERNAL_API_URL,
            json={'question': user_question},
            headers={'Content-Type': 'application/json'}
        )
        
        # Проверяем статус ответа
        if response.status_code == 200:
            # Получаем ответ от API и отправляем его пользователю
            answer = response.json().get('answer', 'Извините, не смог получить ответ от API.')
            await message.answer(answer)
        else:
            await message.answer('Произошла ошибка при обработке вашего запроса.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
