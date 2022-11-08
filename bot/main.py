from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from googletrans import Translator
from datetime import datetime
from threading import Thread

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

users = []
countries = []
chat_id = 0

#______________________________________________________________________________________________
# SET-GET-UPDATE FUNCTION

def set_user(name, id):
    check = False
    for user in users:
        if user[1] == id:
            check = True
            break
    if check == False: 
        users.append([name, id, False])
        write_users()
    return check

def check_change(id):
    for user in users:
        if user[1] == id:
            return user[2]

def get_lang(country):
    if country == 'США': 
        return 'en'
    elif country == 'Россия':
        return 'ru'
    elif country == 'Япония':
        return 'ja'
    elif country == 'Россия':
        return 'ru'
    elif country == 'Китай':
        return 'zh-cn'
    elif country == 'Испания':
        return 'es'
    elif country == 'Бразилия':
        return 'pt'
    elif country == 'Франция':
        return 'fr'
    elif country == 'Италия':
        return 'it'
    elif country == 'Норвегия':
        return 'no'
    elif country == 'Египет':
        return 'ar'
    elif country == 'ОАЭ':
        return 'ar'
    elif country == 'Индия':
        return 'hi'
    elif country == 'Турция':
        return 'tr'
    elif country == 'Мексика':
        return 'es'
    elif country == 'Куба':
        return 'es'
    elif country == 'Ирландия':
        return 'ga'
    elif country == 'Англия':
        return 'en'
    elif country == 'Германия':
        return 'de'
    elif country == 'Казахстан':
        return 'kk'
    elif country == 'Южная Корея':
        return 'ko'
    elif country == 'Греция':
        return 'el'
    elif country == 'Грузия':
        return 'ka'
    else: return 'ru'

def clean_states():
    while True:
        if datetime.now().hour%4 == 0 and datetime.now().minute == 0 and datetime.now().second == 0:
            for line in users:
                dp.current_state(user = line[1]).finish()

thread_clean_states = Thread(target=clean_states)

#______________________________________________________________________________________________
# INPUT-OUTPUT FUNCTION

def write_chat_id():
    global chat_id
    with open('data/chat-id.txt', 'w', encoding='utf-8') as file:
        file.write(str(chat_id))
    file.close

def read_chat_id():
    global chat_id
    with open('data/chat-id.txt', 'r', encoding='utf-8') as file:
        chat_id_str = file.read()
    file.close
    if chat_id_str != '':
        chat_id = int(chat_id_str)

def write_users():
    global users
    with open('data/users.txt', 'w', encoding='utf-8') as file:
        for user in users:
            file.write(user[0] + ' ' + str(user[1]) + ' ' + str(user[2]) + '\n')
    file.close()

def read_users():
    global users
    with open('data/users.txt', 'r', encoding='utf-8') as file:
        string = file.read().splitlines()
    file.close()
    for user in string:
        name = user.split(" ")[0]
        id = user.split(" ")[1]
        change = user.split(" ")[2]
        if change == 'False': 
            change = 0
        else: 
            change = 1
        users.append([name, int(id), bool(change)])

def write_countries():
    global countries
    with open('data/countries.txt', 'w', encoding='utf-8') as file:
        for line in countries:
            file.write(line[0] + ': ' + line[1] + '\n')
    file.close()

def read_countries():
    global countries
    with open('data/countries.txt', 'r', encoding='utf-8') as file:
        string = file.read().splitlines()
    file.close()
    for line in string:
        country = line.split(": ")[0]
        name = line.split(": ")[1].split(" ")[0]
        countries.append([country, name]) 

#______________________________________________________________________________________________
# KEYBOARD FUNCTION

def start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Выбрать страну'))
    return keyboard

def number_keyboard():
    global countries
    buttons = []
    for i in range(0, len(countries)):
        if countries[i][1] == 'none':
            buttons.append(f"{i + 1}")
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=6)
    keyboard.add(*buttons)
    return keyboard

def yesno_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Да'))
    keyboard.add(types.KeyboardButton('Нет'))
    return keyboard

#______________________________________________________________________________________________
# MESSAGE-HANDLER FUNCTION

class Choose(StatesGroup):
    waiting_for_start = State()
    waiting_for_number = State()
    waiting_for_yesno = State()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(set_chat_id, commands="setchatid", state="*")
    dp.register_message_handler(send_start, commands="start", state="*")
    dp.register_message_handler(send_help, commands="help", state="*")
    dp.register_message_handler(set_default, commands="reset", state="*")
    dp.register_message_handler(get_all, commands="getall", state="*")
    dp.register_message_handler(send_start_again, state=None)
    dp.register_message_handler(start_choosen, state=Choose.waiting_for_start)
    dp.register_message_handler(number_choosen, state=Choose.waiting_for_number)
    dp.register_message_handler(yesno_choosen, state=Choose.waiting_for_yesno)

async def set_chat_id(msg: types.Message):
    global chat_id
    chat_id = msg.chat.id
    write_chat_id()

async def send_start_again(msg: types.Message, state: FSMContext):
    await msg.answer("Нажми на \"Выбрать страну\"", reply_markup=start_keyboard())
    await state.set_state(Choose.waiting_for_start)

async def send_start(msg: types.Message, state: FSMContext):
    member = await bot.get_chat_member(chat_id, msg.from_user.id)
    if member["status"] != "left":
        set_user(msg.from_user.first_name, msg.from_user.id)
        await msg.answer(f"Привет, {msg.from_user.first_name}!\n\n\
Нажми на \"Выбрать страну\" для начала", reply_markup=start_keyboard())
        await state.set_state(Choose.waiting_for_start.state)
    else:
        await msg.answer("Привет, к сожалению, тебя нет в списке допустимых пользователей")

async def send_help(msg: types.Message):
    await msg.answer("Вот что я могу:\n\n/start - начать чат\n\n/help - получить список команд\n\n\
/reset - сбросить список\n\n/getall - получить список")

async def set_default(msg: types.Message):
    global countries
    if msg.from_user.id == 788094142:
        for line in countries:
            line[1] = 'none'
        write_countries()
        for line in users:
            line[2] = False
        write_users()
        await msg.answer('Значения сброшены')
    else:
        await msg.answer('Недостаточно прав') 

async def get_all(msg: types.Message):
    global countries
    if msg.from_user.id == 788094142:
        message = ''
        for line in countries:
            message += line[0] + ': ' + line[1] + '\n'
        await msg.answer(message) 
    else:
        await msg.answer('Недостаточно прав') 

async def start_choosen(msg: types.Message, state: FSMContext):
    global countries
    if msg.text.lower() == 'выбрать страну':
        check = True
        for line in countries:
            if msg.from_user.first_name == line[1] and check_change(msg.from_user.id) == False:
                check = False
                await msg.answer('Хочешь изменить выбор?', reply_markup=yesno_keyboard())
                await state.set_state(Choose.waiting_for_yesno)
                break
            elif msg.from_user.first_name == line[1] and check_change(msg.from_user.id) == True:
                check = False
                await msg.answer('Больше выбирать нельзя', reply_markup=start_keyboard())
                break
        if check == True: 
            await msg.answer("Выбери цифру из списка, и я отправлю тебе твою страну.\n\
Ты так же сможешь сделать выбор повторно, но только один раз", reply_markup=number_keyboard())
            await state.set_state(Choose.waiting_for_number)
    else:
        await give_diff_answer(msg, state)

async def number_choosen(msg: types.Message, state: FSMContext):
    if msg.text.lower().isdigit():
            if int(msg.text.lower()) <= len(countries) and int(msg.text.lower()) > 0:
                if countries[int(msg.text.lower())-1][1] == 'none':
                    countries[int(msg.text.lower())-1][1] = msg.from_user.full_name
                    write_countries()
                    translator = Translator()
                    translation = translator.translate('Отличный выбор', src='ru', dest=get_lang(countries[int(msg.text.lower())-1][0]))
                    await msg.answer(f"{translation.text}! \
Твоя страна - {countries[int(msg.text.lower())-1][0]}", reply_markup=start_keyboard())
                    await state.set_state(Choose.waiting_for_start)
                else:
                    await msg.answer("Выбери число из доступных на клавиатуре", reply_markup=number_keyboard())
            else:
                    await msg.answer("Выбери число из доступных на клавиатуре", reply_markup=number_keyboard())
    else:
        await give_diff_answer(msg, state)

async def yesno_choosen(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        for user in users:
            if user[1] == msg.from_user.id:
                user[2] = True
        write_users()
        for line in countries:
            if (line[1] == msg.from_user.full_name):
                line[1] = 'none'
        write_countries()
        await msg.answer("Выбери цифру из списка, и я отправлю тебе твою страну", reply_markup=number_keyboard())
        await state.set_state(Choose.waiting_for_number)
    elif msg.text.lower() == 'нет':
        await msg.answer("Окей", reply_markup=start_keyboard())
        await state.set_state(Choose.waiting_for_start)
    else:
        await give_diff_answer(msg, state)

swear_words = ['сука', 'блять', 'бля', 'заебал', 'пидор', 'мудак', 'гнида', 'падла', 'уебок', 'пиздец', 'тупой']

async def give_diff_answer(msg: types.Message, state: FSMContext):
    for word in str(msg.text.lower()).split():
        if word in swear_words:
            with open('images/15611531.jpg', 'rb') as photo:
                await msg.bot.send_photo(msg.from_user.id, photo)
            photo.close()
            return
    if msg.text.lower() == 'привет':
        await msg.answer(f"Привет, {msg.from_user.full_name}")
    else: 
        await msg.answer('Не понимаю, что это значит')

#______________________________________________________________________________________________
# MAIN FUNCTION      

if __name__ == '__main__':
    read_chat_id()
    read_users()
    read_countries()
    try:
        register_handlers(dp)
        thread_clean_states.start()
        executor.start_polling(dp, skip_updates = True)
    finally:
        write_chat_id()
        write_users()
        write_countries()
