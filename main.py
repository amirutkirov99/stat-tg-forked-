from dotenv import load_dotenv
import os
import json
from datetime import datetime
import pytz
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.methods.send_message import SendMessage
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest 
import sqlite3
import re
from flask import Flask, render_template
from threading import Thread
from background import keep_alive
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

keep_alive()


# app = Flask(__name__)


# @app.route('/')
# def index():
#     return '''<body style="margin: 0; padding: 0;">
#     <iframe width="100%" height="100%" src="https://axocoder.vercel.app/" frameborder="0" allowfullscreen></iframe>
#   </body>'''


# def run():
#     app.run(host='0.0.0.0', port=8080)


# def keep_alive():
#     t = Thread(target=run)
#     t.start()


# keep_alive()
print("Server Running Because of Axo")
load_dotenv()  # env
token = os.getenv("BOT_TOKEN")
dev = int(os.getenv("DEVELOPER_CHAT_ID"))
chanel = int(os.getenv("CHANNEL_ID"))
admins = list(map(int, os.getenv('ADMINS').split(',')))


def create_users_table():
    # Определяем путь к базе данных
    db_name = 'users.db'
    db_path = os.path.join(os.getcwd(), db_name)

    # Подключаемся к базе данных (создаем, если не существует)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER NOT NULL,
                       full_name TEXT NOT NULL,
                       username TEXT,
                       time TEXT)''')

    # Закрываем соединение
    conn.commit()
    conn.close()


# Создаем таблицу и получаем путь к базе данных
create_users_table()


def remove_numbered_parentheses(text):
    # Регулярное выражение для поиска строк вида " (1)", " (2)", " (3)" и т.д.
    pattern = r" \(\d+\)"
    # Замена найденных строк на пустую строку
    cleaned_text = re.sub(pattern, "", text)
    return cleaned_text


def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def get_user_count():
    db_name = 'users.db'
    db_path = os.path.join(os.getcwd(), db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def insert_or_update_user(id, full_name, username="-", time="-"):
    # Подключаемся к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь с таким именем
    cursor.execute('''SELECT id FROM users WHERE id = ?''', (id,))
    existing_id = cursor.fetchone()

    if existing_id:
        # Если пользователь уже существует, обновляем время и имя пользователя
        cursor.execute(
            f'''UPDATE users SET full_name = "{full_name}", username = "{username}", time = "{time}" WHERE id = {id}''')
    else:
        # Если пользователь не существует, добавляем новую запись с текущим временем
        cursor.execute('''INSERT INTO users (id, full_name, username, time) VALUES (?, ?, ?, ?)''',
                       (id, full_name, username, time))

    # Закрываем соединение
    conn.commit()
    conn.close()


def get_users():
    # Установка соединения с базой данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        # Выборка всех записей из таблицы MultiText
        cursor.execute(
            "SELECT id, full_name, username, time Content FROM users")
        rows = cursor.fetchall()

        # Формирование списка пар Id и Content
        id_content_pairs = [(row[0], row[1], row[2], row[3],) for row in rows]

        return id_content_pairs

    except sqlite3.Error as e:
        conn.commit()
        conn.close()
        print("Ошибка при выборке данных из базы данных:", e)
        return []
    finally:
        # Закрытие соединения
        conn.commit()
        conn.close()


filename = "users_data.txt"


def send_time():
    # Задаем часовой пояс UTC+5
    # Можете заменить на подходящий вам часовой пояс
    timezone = pytz.timezone('Asia/Tashkent')
    now = datetime.now(timezone)
    current_time = now.strftime("%Y-%m-%d // %H:%M:%S | %Z GMT")
    # Отправляем текущее время пользователю
    return current_time


def save_users_to_file(filename):
    try:
        with open(filename, 'w', encoding='utf-16') as file:
            file.write(f"Юзеры:\n")
            for user in get_users():
                file.write(f"ID: {user[0]}, ")
                file.write(f"Full Name: {user[1]}, ")
                file.write(f"Username: {user[2]}, ")
                file.write(f"Time: {user[3]};")
                file.write("\n")  # Добавляем пустую строку между записями
    except IOError as e:
        print(f"Ошибка при сохранении данных в файл {filename}: {e}")


# Указываем имя файла для сохранения данных
# Сохраняем данные пользователей в текстовый файл, перезаписывая его, если он уже существует


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота

bot = Bot(token=token)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start

async def set_commands(
        bot: Bot,
        user_id,
        admins = admins
) -> None:
    commands = [
        BotCommand(
            command="start",
            description="Перезапустить бота!"
        ),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(chat_id=user_id))
    for admin in admins:
        commands.append(
            BotCommand(
                command="users",
                description="Посмотреть список пользователей"
            )
        )
        commands.append(
            BotCommand(
                command="publish",
                description="Опубликовать новый запись"
            )
        )
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(chat_id=admin))


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await set_commands(bot, user_id=message.from_user.id)
    if message.from_user.id in admins:
        kb = [
            [types.KeyboardButton(text="Опубликовать кнопку")],
            [types.KeyboardButton(text="Получить список пользователей")]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите кнопку"
        )
        await message.answer("Здраствуйте!", reply_markup=keyboard)
    else:
        await message.answer(f"Здраствуйте!\n{message.from_user.id}", reply_markup=ReplyKeyboardRemove())


@dp.message(F.text.lower() == "опубликовать кнопку")
async def with_puree(message: types.Message):
    await message.reply("Пусто")


@dp.message(F.text.lower() == "получить список пользователей")
async def without_puree(message: types.Message):
    if message.from_user.id in admins:
        save_users_to_file(filename)
        document = FSInputFile(filename)
        await bot.send_document(
            chat_id=message.from_user.id,
            caption=f"Юзеры\nАктуальный на {escape_markdown(send_time())}",
            document=document,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await message.reply("У вас недостаточно прав чтобы выполнить эту команду!")


@dp.message(Command("publish"))
async def cmd_random(message: types.Message):
    if message.from_user.id in admins:
        builder = InlineKeyboardBuilder()
        button_text = "❤️"
        callback_data = json.dumps({'action': 'chanel_value', 'text': button_text})
        builder.add(types.InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data)
        )
        if message.text != "/publish":
            await message.reply("Опубликовано!")
            await bot.send_message(
                chat_id=chanel,
                text=message.text.replace("/publish ", ""),
                reply_markup=builder.as_markup()
            )
        elif message.text == "/publish" or message.text == "/publish ":
            await message.reply("Нельзя опубликовать пустое слово!")

async def send_Data(username, callback: types.CallbackQuery, fname, user_id, builder, type=1):
    text1 = (
        f"Пользователь нажал на кнопку\\.\n"
        f"Full name: [{escape_markdown(fname)}](tg://user?id={user_id})\n"
        f"ID: `{user_id}`\n"
        f"Юзернейм: {escape_markdown(username)}\n"
        f"Время: {escape_markdown(send_time())}"
        )
    text2 = (
        f"Пользователь нажал на кнопку\\.\n"
        f"Full name: `{escape_markdown(fname)}`\n"
        f"ID: `{user_id}`\n"
        f"Юзернейм: {escape_markdown(username)}\n"
        f"Время: {escape_markdown(send_time())}\n"
        f"У пользователя профиль приватный"
        )
    try:
        if type == 1:
            await callback.bot.send_message(
                chat_id=dev,
                text=text1,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
        elif type == 2:
            await callback.message.edit_text(
                text=text1,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
    except:
        if type == 1:
            await callback.bot.send_message(
                chat_id=dev,
                text=text2,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif type == 2:
            await callback.message.edit_text(
                text=text2,
                parse_mode=ParseMode.MARKDOWN_V2
            )
@dp.callback_query(F.data.func(lambda data: json.loads(data).get('action') == "chanel_value"))
async def send_random_value(callback: types.CallbackQuery, bot: Bot):
    

    username = f"{callback.from_user.username}" if callback.from_user.username is None else f"@{callback.from_user.username}"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="ссылка на пользователя",
            url=f"tg://user?id={callback.from_user.id}"
        )
    )
    await send_Data(username=username, callback=callback, fname=callback.from_user.full_name, user_id=callback.from_user.id, builder=builder, type=1)

    try:
        await callback.answer("Я так знал, ты крут(а)🔥")
        insert_or_update_user(
            callback.from_user.id, callback.from_user.full_name, f"{username}", send_time())
    except:
        print(f"{callback.from_user.id}, {callback.from_user.full_name}, {callback.from_user.username}, {send_time()}")
        await callback.bot.send_message(chat_id=dev, text="Ошибка в базе данных при добавлении!")

    user_count = get_user_count()
    # Обновляем текст кнопки
    data = json.loads(callback.data)
    button_text = data['text']

    new_button_text = f"{remove_numbered_parentheses(button_text)} ({user_count})"
    new_callback_data = json.dumps(
        {'action': 'chanel_value', 'text': new_button_text})

    builder1 = InlineKeyboardBuilder()
    builder1.add(
        InlineKeyboardButton(
            text=new_button_text,
            callback_data=new_callback_data
        )
    )

    # Получение текста публикации
    message_text = callback.message.text

    try:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=message_text,  # Используем текст текущего сообщения
            reply_markup=builder1.as_markup()
        )
    except Exception as e:
        pass


MAX_USERS_PER_PAGE = 10


@dp.message(Command("users"))
async def cmd_inline_url(message: types.Message):
    if message.from_user.id in admins:
        await send_user_list(message)


async def send_user_list(message: types.Message, page: int = 0, edit_message_id=None):
    users = get_users()
    start_idx = page * MAX_USERS_PER_PAGE
    end_idx = start_idx + MAX_USERS_PER_PAGE
    current_users = users[start_idx:end_idx]

    builder = InlineKeyboardBuilder()
    for user in current_users:
        builder.row(
            InlineKeyboardButton(
                text=user[1],
                callback_data=f"user_data_{user[0]}"
            )
        )

    if page > 0 or end_idx < len(users):
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="<<Назад",
                    callback_data=f"page_{page - 1}"
                )
            )

        if end_idx < len(users):
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="Вперед>>",
                    callback_data=f"page_{page + 1}"
                )
            )

        builder.row(*navigation_buttons)

    if edit_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=edit_message_id,
            text='Выберите пользователя',
            reply_markup=builder.as_markup()
        )
    else:
        await message.reply(
            'Выберите пользователя',
            reply_markup=builder.as_markup()
        )


@dp.callback_query(F.data.startswith("page_"))
async def handle_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    await send_user_list(callback.message, page, edit_message_id=callback.message.message_id)
    await callback.answer()


@dp.callback_query(F.data.startswith("user_data_"))
async def send_random_value(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[2])

    # Получаем пользователей при каждом вызове
    users = get_users()
    user = next((u for u in users if u[0] == user_id), None)
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="ссылка на пользователя",
            url=f"tg://user?id={user[0]}"
            )
        )
    username = f"\({user[2]}\)" if user[2] == "None" else f"{user[2]}"
    await send_Data(username=username, callback=callback, fname=user[1], user_id=user[0], builder=builder, type=2)
    # if user:
    #     try:
    #         await callback.message.edit_text(
    #             text=f"Пользователь нажал на кнопку\\.\nFull name: [{escape_markdown(user[1])}](tg://user?id={user[0]})\nID: `{user[0]}`\nЮзернейм: {username}\nВремя: {escape_markdown(user[3])}",
    #             parse_mode=ParseMode.MARKDOWN_V2,
    #             reply_markup=builder.as_markup()
    #         )

    #     except Exception as e:
    #         # logging.info(e)
    #         await callback.message.edit_text(
    #             text=f"Пользователь нажал на кнопку\\.\nFull name: `{escape_markdown(user[1])}`\nID: `{user[0]}`\nЮзернейм: {username}\nВремя: {escape_markdown(user[3])}\nУ пользователя профиль приватный",
    #             parse_mode=ParseMode.MARKDOWN_V2,
    #         )
    await callback.answer()


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
