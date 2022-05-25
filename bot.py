from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem

from parser_jutsu import Jutsu

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

jutsu = Jutsu()

class States(Helper):
    mode = HelperMode.snake_case
    STATE_SEARCH = ListItem()

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет 😉\nИспользуй команду /search для поиска аниме')

@dp.message_handler(commands=['search'])
async def process_search_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Что искать будем?')
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[0])

@dp.message_handler(state=States.STATE_SEARCH)
async def search_state_case(message: types.Message):
    if not jutsu.search(message.text):
        await bot.send_message(message.chat.id, 'Не удалось найти 😔')
    else:
        anime_button = InlineKeyboardButton(jutsu.name, callback_data='anime_button')
        keyboard = InlineKeyboardMarkup().add(anime_button)
        await bot.send_message(message.chat.id, 'Нашлось аниме 😼', reply_markup=keyboard)
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()

@dp.callback_query_handler(lambda c: c.data == 'anime_button')
async def process_callback_anime_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    for season in jutsu.seasons:
        keyboard.add(InlineKeyboardButton(season, callback_data=season))
    await callback_query.message.edit_text(jutsu.name, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in jutsu.seasons)
async def process_callback_season_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    jutsu.select_season(callback_query.data)
    keyboard = InlineKeyboardMarkup()
    for seria in jutsu.series:
        keyboard.add(InlineKeyboardButton(seria, callback_data=seria))
    await callback_query.message.edit_text(jutsu.name, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in jutsu.series)
async def process_callback_seria_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    jutsu.select_seria(callback_query.data)
    jutsu.link()
    await bot.send_message(callback_query.from_user.id, jutsu.url + jutsu.data[jutsu.season][jutsu.seria])

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)