from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

from keyboards.inl_keyboards import inl_main_menu
from utils import FileManager
from utils.enum_path import Path


command_router = Router()

@command_router.message(Command('start'))
async def start(message:Message, command:CommandObject):
    await message.answer_photo(
        photo = FSInputFile(Path.IMAGES.value.format(file=command.command)),
        caption=FileManager.read_txt(Path.MESSAGES, command.command),
        reply_markup=inl_main_menu()
    )

