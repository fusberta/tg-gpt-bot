import logging
import openai
import os
from config import *
from replies import *
from pydub import AudioSegment
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
mkbtn1 = KeyboardButton('Команды')
mkbtn2 = KeyboardButton('Описание')
mkbtn3 = KeyboardButton('Начать чат')
mainKeyboard.add(mkbtn1, mkbtn2, mkbtn3)

chatKeyboard = ReplyKeyboardMarkup(resize_keyboard=True)
ckbtn1 = KeyboardButton('Закончить чат')
chatKeyboard.add(ckbtn1)

inlineChat = InlineKeyboardMarkup(row_width=3)
icbtn1 = InlineKeyboardButton('Начать чат', callback_data='chat')
inlineChat.add(icbtn1)


async def aiQuery(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'Тебя зовут Аркадиус. Ты помогаешь полььзователю'},
                {"role": "user", "content": prompt}
            ]
        )
        result = completion.choices[0].message.content
        return result
    except:
        return None


async def handle_chat(callback):
    global chat_respond
    chat_respond = True
    await bot.send_message(callback.from_user.id, text='Чат начинается...', reply_markup=chatKeyboard)

chat_respond = False


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
async def handle_chat_command(message: types.Message):
    # Set the flag variable to True to allow the bot to respond to messages
    await handle_chat(message)


@dp.message_handler(commands=['end_chat'])
async def handle_end_chat_command(message: types.Message):
    global chat_respond
    if chat_respond:
        chat_respond = False
        await message.reply('Чат закончен. Спасибо за использование бота!')


@dp.message_handler(content_types=['text'])
async def bot_menu(message: types.Message):
    if not message.text:
        return
    global chat_respond
    if message.text == 'Команды' or message.text == '/help':
        await bot.send_message(message.from_user.id, HELP_COMMAND, parse_mode='HTML')
    elif message.text == 'Описание' or message.text == '/description':
        await bot.send_message(message.from_user.id, DESC_COMMAND, parse_mode='HTML')
    elif message.text == 'Начать чат':
        await handle_chat(message)
    elif message.text == 'Закончить чат':
        if chat_respond:
            chat_respond = False
            await bot.send_message(message.from_user.id, 'Чат закончен. Спасибо за использование бота!',
                                   reply_markup=mainKeyboard)
    elif chat_respond:
        if not any(substring in message.text for substring in
                   ('/help', '/start', '/description', 'Команды', 'Описание', 'Начать чат')):
            await bot.send_chat_action(message.chat.id, action='typing')
            answer = await aiQuery(message.text)
            if answer is not None:
                await message.reply(answer)
            else:
                await message.reply('Произошла ошибка, попробуйте спросить об этом позже...')
    else:
        await message.reply('Неизвестная команда, чтобы задать вопрос, нажмите на кнопку', reply_markup=inlineChat)


@dp.callback_query_handler()
async def callback_query_handler(callback: types.CallbackQuery):
    if callback.data == 'chat':
        await handle_chat(callback)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
