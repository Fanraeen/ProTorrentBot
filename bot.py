from aiogram import Bot, Dispatcher, executor, types

from os import remove
from answer_build import *
from config import BOT_TOKEN


# Initial
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='Привет, это бот для поиска по торрент-трекерам.\n_Просто напиши..._',
                           parse_mode='markdown')


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('file'))
async def handler(callback_query: types.CallbackQuery):
    file_id = int(callback_query.data[4:])
    path_to_file = torrent_file_path(file_id)
    torrent_file = open(path_to_file, 'rb')
    await bot.send_document(chat_id=callback_query.message.chat.id, document=torrent_file)
    remove(path_to_file)


@dp.message_handler(lambda message: message.text.startswith('/torrent'))
async def get_torrent(message: types.Message):
    chat_id = message.chat.id
    torrent_id = message.text[8:]
    try:
        torrent_id = int(torrent_id)
    except:
        await bot.send_message(chat_id=chat_id, text='Проблема с id дружочек...')
    else:
        download_button = types.InlineKeyboardButton(
            'Скачать .torrent',
            callback_data=f'file{torrent_id}'
        )
        keyboard = types.InlineKeyboardMarkup().add(download_button)
        try:
            torrent_data = details_build_text(torrent_id=torrent_id)
        except:
            await bot.send_message(chat_id=chat_id, text='Произошла ошибка парсинга...')
        else:
            await bot.send_message(
                chat_id=chat_id, 
                text=str(torrent_data), 
                parse_mode='html', 
                reply_markup=keyboard
                )


@dp.message_handler(lambda message: message.text is not None)
async def search(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text='Начинаю искать...')
    try:
        result = search_build_text(message.text)
    except:
        await bot.send_message(chat_id=chat_id, text='Произошла ошибка парсинга...')
    await bot.send_message(chat_id=chat_id, text=result, parse_mode='html')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
