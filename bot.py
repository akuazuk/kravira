#API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'

import logging
from aiogram import Bot, Dispatcher, executor, types
import httpx
import asyncio

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, и я перешлю его во внешний API.")

@dp.message_handler()
async def send_question_to_external_api(message: types.Message):
    question_text = message.text
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EXTERNAL_API_URL,
                json={"question": question_text},  # Текст сообщения вставляется в JSON как значение ключа "question"
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()  # Генерирует исключение для ответов с ошибкой
            data = response.json()
            answer = data.get('answer', 'Извините, не получилось обработать ваш запрос.')
            await message.answer(answer)
        except httpx.HTTPStatusError as e:
            logging.error(f"Ошибка ответа от API: {e.response.status_code}")
            await message.answer('Произошла ошибка при обработке вашего запроса API.')
        except httpx.RequestError as e:
            logging.error(f"Ошибка запроса к API: {e}")
            await message.answer('Произошла ошибка при отправке запроса к API.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

