from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, FSInputFile
from aiogram import Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from asyncio import sleep as async_sleep
from datetime import datetime

from states import BotStates
import text
from config import BOT_TOKEN, SUPER_ADMIN_ID_LIST, DATE_FORMAT
from db import db_client, write_data_to_csv
from db import OrderRecord, ContactRecord, UserRecord, UserInfo
from logger import logger_client
from keyboards import *
from exeptions import *

# init global variables (bot, router, db class)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()


@router.message(Command(text.start_command))
async def start_handler(message: Message, state: FSMContext):
    simple_user = True 
    if message.from_user.id in SUPER_ADMIN_ID_LIST:
        await message.answer(text=text.super_admin_guide)
        simple_user = False
    if db_client.is_admin_exist(message.from_user.username):
        await message.answer(text.admin_guide)
        db_client.change_admin_user_id(message.from_user.username, message.from_user.id)
        simple_user = False
    
    if simple_user:
        await message.answer(text.start)

    if not db_client.is_user_exist(message.from_user.id):
        db_client.add_user(message.from_user.id, message.from_user.username, message.from_user.username)       # name = username bu default


@router.message(Command(text.change_name_command))
async def change_name_handler(message: Message, state: FSMContext):
    await message.answer(text.name_input_prompt)
    await state.set_state(BotStates.name_input)


@router.message(BotStates.name_input)
async def set_name_handler(message: Message, state: FSMContext):
    db_client.change_name(user_id=message.from_user.id, new_name=message.text)
    await message.answer(text.reg_success_text(message.text))
    await state.set_state(BotStates.default)


# stubs for future functional
@router.message(Command(text.service_1_command))
async def service_1_handler(message: Message, state: FSMContext):
    keyboard = create_service_button(ServiceCallback(service_id=1).pack())
    await message.answer(text.service_1_text, reply_markup=keyboard)


@router.message(Command(text.service_2_command))
async def service_2_handler(message: Message, state: FSMContext):
    keyboard = create_service_button(ServiceCallback(service_id=2).pack())    
    await message.answer(text.service_2_text, reply_markup=keyboard)


@router.message(Command(text.service_3_command))
async def service_3_handler(message: Message, state: FSMContext):
    keyboard = create_service_button(ServiceCallback(service_id=3).pack())
    await message.answer(text.service_3_text, reply_markup=keyboard)


@router.message(Command(text.send_message_command))
async def send_message_command_handler(message: Message, state: FSMContext):
    await message.answer(text.send_message_text)


@router.callback_query(ServiceCallback.filter())
async def service_button_handler(query: CallbackQuery, callback_data: ServiceCallback, state: FSMContext):
    await query.message.answer(text=text.service_text)

    order = OrderRecord(id=0, order_id=db_client.gen_order_id(), user_id=query.from_user.id, service_id=callback_data.service_id, order_date=datetime.now())
    db_client.add_user_order_record(order)
    if not db_client.is_user_contact_data_exist(query.from_user.id):
        await query.message.answer(text=text.send_contact_request_text, reply_markup=SHARE_CONTACT_KEYBOARD)
        await async_sleep(30)   # подождать 30 сек и отправить информацию о заказе
        await send_user_order_data_to_admins(query.from_user.id, order)
    else:
        await send_user_order_data_to_admins(query.from_user.id, order)
    
 
@router.message(F.contact)
async def contact_message_handler(message: Message, state: FSMContext):
    try:
        db_client.add_user_contact_data(message.from_user.id, message.contact.first_name, message.contact.last_name, message.contact.phone_number)
    except UserAlreadyExist as e:
        logger_client.error_exp(e)

    await message.answer(text=text.contact_message_success, reply_markup=ReplyKeyboardRemove())

# SHADOW COMMANDS HANDLERS

@router.message(Command(text.add_admin_command))
async def add_admin_command_handler(message: Message, command: CommandObject):
    if message.from_user.id in SUPER_ADMIN_ID_LIST:
        if not command.args:
            await message.answer(text.invalid_args)
        else:
            username = command.args if command.args[0] != '@' else command.args[1:]
            username = username.strip()
            try:
                db_client.add_admin(username)
            except UserAlreadyExist:
                await message.answer("Админ с таким именем уже существует!")
            else:
                await message.answer(f"Пользователь {username} успешно добавлен как админ!")


@router.message(Command(text.del_admin_command))
async def del_admin_command_handler(message: Message, command: CommandObject):
    if message.from_user.id in SUPER_ADMIN_ID_LIST:
        if not command.args:
            await message.answer(text.invalid_args)
        else:
            username = command.args if command.args[0] != '@' else command.args[1:]
            username = username.strip()
            try:
                db_client.del_admin(username)
            except UserNotExist:
                await message.answer(f"Пользователь {username} не является админом!")
            else:
                await message.answer(f"Пользователь {username} больше не является админом!")


@router.message(Command(text.admin_list_command))
async def del_admin_command_handler(message: Message, command: CommandObject):
    if message.from_user.id in SUPER_ADMIN_ID_LIST:
        admins_list_text =  ''.join([f'{i + 1}) {username}\n' for i, username in enumerate(db_client.get_all_admins_username())])
        if admins_list_text:
            await message.answer(admins_list_text)
        else:
            await message.answer("Список админов пуст")

@router.message(Command(text.send_all_command))
async def send_all_command_handler(message: Message, state: FSMContext):
    if db_client.is_admin_exist(message.from_user.username):
        await message.answer("Напишите ваше сообщение и оно будет отправлено всем пользователям")
        await state.set_state(BotStates.send_all)


@router.message(Command(text.users_info_command))
async def send_users_info_handler(message: Message, state: FSMContext):
    if db_client.is_admin_exist(message.from_user.username):
        file_path = f"{datetime.now().strftime(DATE_FORMAT)}.csv"
        data = db_client.get_all_users_info()
        write_data_to_csv(data=data, file_path=file_path)
        document = FSInputFile(file_path)
        await message.answer_document(document=document)


@router.message(BotStates.send_all)
async def send_all_handler(message: Message, state: FSMContext):
    await send_msg_obj_to_all_users(message=message)
    await message.answer(text.message_send_success_text)
    await state.set_state(BotStates.default)


@router.callback_query(MsgCallback.filter())
async def answer_handler(query: CallbackQuery, callback_data: MsgCallback, state: FSMContext):
    await query.answer(text=f"Напишите ваше сообщение для {callback_data.username}")
    await state.update_data(user_id=callback_data.user_id)
    await state.set_state(BotStates.send_msg_to_user)


@router.message(BotStates.send_msg_to_user)
async def admin_to_user_msg_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = int(data.get('user_id'))
    if await send_msg_obj_by_user_id(message=message, user_id=user_id):
        await message.answer(text.message_send_success_text)
    else:
        await message.answer(text.message_send_failed)
    await state.set_state(BotStates.default)


@router.message()
async def communication_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = db_client.get_user(user_id)   # name from table users
    if user_data is None:
       user_alias = message.from_user.username
    else:
        user_alias =  user_data['name']

    keyboard = create_keyboard(user_id=message.from_user.id, username=user_alias)
    if await send_user_msg_to_admins(user_alias=user_alias, message=message, reply_keyboard=keyboard):
        await message.answer(text=text.message_send_success_text)
    else:
        await message.answer(text=text.message_send_failed)


async def send_message_by_user_id(user_id: int, text: str, reply_keyboard: InlineKeyboardMarkup | None = None) -> None:
    if reply_keyboard is None:
        await bot.send_message(chat_id=user_id, text=text)
    else:
        await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_keyboard)


async def send_message_by_username(username: str, text: str) -> None:
    chat = await bot.get_chat(username)
    await send_message_by_user_id(user_id=chat.id, text=text)


async def send_message_to_user_id_list(user_id_list: list[int], text: str, reply_keyboard: InlineKeyboardMarkup | None = None) -> None:
    for user_id in user_id_list:
        await send_message_by_user_id(user_id=user_id, text=text, reply_keyboard=reply_keyboard)


async def send_message_to_username_list(username_list: list[str], text: str) -> None:
    for username in username_list:
        await send_message_by_username(username=username, text=text)


async def send_message_to_all_users(text: str) -> None:
    user_id_list = db_client.get_all_users_id()
    await send_message_to_user_id_list(user_id_list=user_id_list, text=text)


async def send_msg_obj_to_all_users(message: Message) -> None:
    user_id_list = db_client.get_all_users_id()
    for user_id in user_id_list:
        await send_msg_obj_by_user_id(message=message, user_id=user_id)


async def send_message_to_admins(text: str, reply_keyboard: InlineKeyboardMarkup) -> None:
    admins_id_list = db_client.get_all_admins_id()
    await send_message_to_user_id_list(user_id_list=admins_id_list, text=text, reply_keyboard=reply_keyboard)


async def send_msg_obj_by_user_id(message: Message, user_id: int) -> bool:
    try:
        await message.copy_to(chat_id=user_id)
    except Exception as e:
        logger_client.error_exp(e)
        return False
    else:
        return True


async def send_msg_obj_to_user_id_list(user_id_list: list[int], message: Message) -> bool:      # эта функция используется только для отправки сообщения админам
    success = True
    for user_id in user_id_list:
        if not await send_msg_obj_by_user_id(message=message, user_id=user_id):
            await bot.send_message(text="Не удалось доставить сообщение. Возможно оно содержит невалидную информацию", chat_id=user_id)
            success = False
    
    return success


async def send_user_msg_to_admins(user_alias: str, message: Message, reply_keyboard: InlineKeyboardMarkup) -> bool:
    admins_id_list = db_client.get_all_admins_id()
    await send_message_to_user_id_list(user_id_list=admins_id_list, text=f"Сообщение от {user_alias}", reply_keyboard=reply_keyboard)
    return await send_msg_obj_to_user_id_list(user_id_list=admins_id_list, message=message)


async def send_user_order_data_to_admins(user_id: int, order: OrderRecord) -> None:
    user = db_client.get_user(user_id)
    if user is None:
        logger_client.error_msg("Пользователь не найден в базе данных! Возможно команда /start не была использована")
        return
    contact = db_client.get_user_contact_data(user_id)

    admins_id_list = db_client.get_all_admins_id()
    keyboard = create_keyboard(user_id=user['user_id'], username=user['name'])
    msg = text.create_order_desc(user=user, order=order, contact=contact)
    await send_message_to_user_id_list(user_id_list=admins_id_list, text=msg, reply_keyboard=keyboard)
