import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import bot, router
from aiogram.types import BotCommand
import text


BOT_COMMANDS = [
        BotCommand(command=f'/{text.start_command}', description=text.start_command_desc),
        BotCommand(command=f'/{text.service_1_command}', description=text.service_1_command_desc),
        BotCommand(command=f'/{text.service_2_command}', description=text.service_2_command_desc),
        BotCommand(command=f'/{text.service_3_command}', description=text.service_3_command_desc),
        BotCommand(command=f'/{text.change_name_command}', description=text.change_name_command_desc),
        BotCommand(command=f'/{text.send_message_command}', description=text.send_message_command_desc),
    ]


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router=router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

