import logging
import openai
from config import *
from replies import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, \
                          KeyboardButton, \
                          InlineKeyboardMarkup, \
                          InlineKeyboardButton

# Configure bot
logging.basicConfig(level=logging.INFO)
openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Configure Keyboards
mainKeyboard = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('/help')
b2 = KeyboardButton('/description')
b3 = KeyboardButton('/chat')
mainKeyboard.add(b1, b2, b3)


async def aiQuery(prompt):
    try:
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0
        )
        return completion.choices[0].text
    except:
        return None


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id, HELP_COMMAND, parse_mode='HTML')


@dp.message_handler(commands=['description'])
async def desc_command(message: types.Message):
    await bot.send_message(message.from_user.id, DESC_COMMAND, parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(WELCOME_MESSAGE,
                        reply_markup=mainKeyboard,
                        parse_mode='HTML')


@dp.message_handler(commands=['chat'])
async def echo(message: types.Message):
    answer = await aiQuery(message.text)

    if answer is not None:
        await message.reply(answer)
    else:
        await message.reply('Ошибка')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
