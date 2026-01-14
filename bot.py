import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from main import create_transport_service
from formatters.stop_formatter import format_stop_info

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a bot created with aiogram.")


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    text = (
        "Доступные команды:\n"
        "/start — запуск бота\n"
        "/help — список команд\n"
        "/stop <id> — показать расписание для остановки\n"
    )
    await message.answer(text)


@dp.message(Command("stop"))
async def command_stop_handler(message: Message) -> None:
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите ID остановки. Пример: /stop 1234")
        return
    stop_code = args[1]

    transport_service = create_transport_service()
    stop_info = transport_service.get_stop_info(stop_code)
    text = format_stop_info(stop_info)
    await message.answer(text)


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
