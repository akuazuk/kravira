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
    payload = {
        "question": question_text,
        # Убедитесь, что ваш API поддерживает следующие параметры в запросе.
        "overrideConfig": {
            "returnSourceDocuments": True
        },
        "history": [
            {
                "message": "Hello, how can I assist you?",
                "type": "apiMessage"
            },
            {
                "type": "userMessage",
                "message": "Hello I am Bob"
            },
            {
                "type": "apiMessage",
                "message": "Hello Bob! how can I assist you?"
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EXTERNAL_API_URL,
                json=payload,
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                # Проверьте структуру ответа и адаптируйте ключ для получения ответа
                answer = data.get('answer', 'Извините, не получилось обработать ваш запрос.')
                await message.answer(answer)
            else:
                logging.error(f"Ошибка ответа от API: {response.status_code} - {response.text}")
                await message.answer('Произошла ошибка при обработке вашего запроса API.')
        except httpx.RequestError as e:
            logging.error(f"Ошибка запроса к API: {str(e)}")
            await message.answer('Произошла ошибка при отправке запроса к API.')
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {str(e)}")
            await message.answer('Произошла неизвестная ошибка.')

async def on_startup(dp: Dispatcher):
    await bot.delete_webhook()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
