import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import config

bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message:Message):
    name = message.from_user.full_name
    await message.answer(f"Hello, {name}, I'm a bot!")


@dp.message(Command("random"))
async def random(message:Message):
    print(f'{message.from_user.full_name, message.text}')


@dp.message()
async def all_messages(message:Message):
    print(f'{message.from_user.full_name, message.text}')


@dp.message(Command("gpt"))
async def gpt(message:Message):
    print(f'{message.from_user.full_name, message.text}')


@dp.message(Command("talk"))
async def talk(message:Message):
    print(f'{message.from_user.full_name, message.text}')


@dp.message(Command("quiz"))
async def quiz(message:Message):
    print(f'{message.from_user.full_name, message.text}')

@dp.message(Command("translate"))
async def translate(message:Message):
    print(f'{message.from_user.full_name, message.text}')


async def start_bot():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())