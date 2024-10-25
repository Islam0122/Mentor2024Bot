from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
from keyboard.inline import language_selection_keyboard, start_functions_keyboard, return_inline_keyboard, \
    materials_inline_keyboard
from message_text.text import messages

start_functions_private_router = Router()
start_functions_private_router.message.filter(ChatTypeFilter(['private']))
user_preferences = {}


async def send_welcome_message(user, target, photo_path='media/images/img_1.png'):
    """Функция для отправки приветственного сообщения с фото."""
    user_id = user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']

    # Создание клавиатуры через отдельную функцию
    keyboard_markup = start_functions_keyboard(language)

    # Попытка отправить сообщение с фото
    try:
        await target.answer_photo(
            photo=types.FSInputFile(photo_path),
            caption=f"{user.full_name}! 😊\n\n{messages[language]['welcome']}",
            reply_markup=keyboard_markup
        )
    except Exception as e:
        await target.answer(f"Произошла ошибка при отправке фото: {e}")
        await target.answer(f"{user.full_name}! 😊\n\n{messages[language]['welcome']}")


@start_functions_private_router.message(CommandStart())
@start_functions_private_router.message(F.text.lower().contains('start') | (F.text.lower() == 'start'))
async def start_cmd(message: types.Message):
    """Обработчик команды /start"""
    await send_welcome_message(message.from_user, message)


@start_functions_private_router.callback_query(F.data.startswith('start'))
async def start_command_callback_query(query: types.CallbackQuery) -> None:
    """Обработчик callback_query с командой start"""
    await query.message.delete()
    await send_welcome_message(query.from_user, query.message)


@start_functions_private_router.message(Command("select_language"))
async def select_language(message: types.Message):
    """Обработчик команды выбора языка через сообщение"""
    keyboard = language_selection_keyboard()
    await message.answer(
        "Please select your language / Пожалуйста, выберите язык / Тилди тандаңыз:",
        reply_markup=keyboard
    )


@start_functions_private_router.callback_query(F.data == 'select_language')
async def select_language_callback(query: types.CallbackQuery):
    """Обработчик выбора языка через callback"""
    await query.message.delete()
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']
    keyboard = language_selection_keyboard(language)
    await query.message.answer(
        "Please select your language / Пожалуйста, выберите язык / Тилди тандаңыз:",
        reply_markup=keyboard
    )


@start_functions_private_router.callback_query(F.data.startswith('set_language_'))
async def set_language_callback(query: types.CallbackQuery):
    """Обработчик установки языка через callback"""
    await query.message.delete()
    user_id = query.from_user.id

    # Если пользователь не существует, инициализируем его настройки
    if user_id not in user_preferences:
        user_preferences[user_id] = {}

    # Установка языка в зависимости от нажатой кнопки
    if query.data == "set_language_ru":
        user_preferences[user_id]['language'] = 'ru'
        response = "Язык установлен на русский."
    elif query.data == "set_language_en":
        user_preferences[user_id]['language'] = 'en'
        response = "Language set to English."
    elif query.data == "set_language_kgz":
        user_preferences[user_id]['language'] = 'kgz'
        response = "Тил кыргызча болуп орнотулду."

    language = user_preferences[user_id]['language']
    await query.message.answer(
        text=response,
        reply_markup=return_inline_keyboard(language)
    )


@start_functions_private_router.callback_query(F.data.startswith('help'))
async def help_callback(query: types.CallbackQuery):
    await query.message.delete()
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']
    await query.message.answer(messages[language]['help_message'],
                               reply_markup=return_inline_keyboard(language),parse_mode=ParseMode.MARKDOWN                   )


@start_functions_private_router.callback_query(F.data.startswith('materials'))
async def additional_features_callback(query: types.CallbackQuery):
    await query.message.delete()
    user_id = query.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}

    language = user_preferences[user_id]['language']
    await query.message.answer(f"{messages[language]['materials']}:",
                               reply_markup=materials_inline_keyboard(language),
                               )
