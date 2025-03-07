from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from text import service_button_text_default, share_contact_button_text


class MsgCallback(CallbackData, prefix='msg'):
    user_id: int
    username: str


class ServiceCallback(CallbackData, prefix='service'):
    service_id: int


def create_keyboard(user_id: int, username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Ответить {username}", callback_data=MsgCallback(user_id=user_id, username=username).pack())

    return builder.as_markup()


def create_service_button(callback_data: str, text: str = service_button_text_default) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)

    return builder.as_markup()


def create_share_phone_button(text: str) -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text=text, request_contact=True)]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    
    return keyboard

SHARE_CONTACT_KEYBOARD = create_share_phone_button(share_contact_button_text)
