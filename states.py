from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    default = State()
    name_input = State()
    send_msg_to_user = State()
    send_all = State()
