from aiogram import Bot, Dispatcher, executor, types

from answer_build import *
from config import BOT_TOKEN


# Initial 
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Привет, это бот для поиска по торрент-трекерам.\n_Просто напиши..._', parse_mode='markdown')


@dp.message_handler(lambda message: message.text.startswith('/torrent'))
async def get_torrent(message: types.Message):
    chat_id = message.chat.id
    torrent_id = message.text[8:]
    try:
        torrent_id = int(torrent_id)
    except:
        await bot.send_message(chat_id=chat_id, text='Проблема с id дружочек...')
    else:
        torrent_data = details_build_text(torrent_id=torrent_id)
        await bot.send_message(chat_id=chat_id, text=str(torrent_data), parse_mode='markdown')


@dp.message_handler(lambda message: message.text is not None)
async def search(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text='Начинаю искать...')
    result = search_build_text(message.text)
    await bot.send_message(chat_id=chat_id, text=result, parse_mode='markdown')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)