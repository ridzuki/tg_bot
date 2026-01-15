from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile

from keyboards.inl_keyboards import inl_main_menu
from utils import FileManager
from utils.enum_path import Path
from logger import logger


command_router = Router()


async def send_start_photo(target_message: Message, cmd_name: str):
    await target_message.answer_photo(
        photo=FSInputFile(Path.IMAGES.value.format(file=cmd_name)),
        caption=FileManager.read_txt(Path.MESSAGES, cmd_name),
        reply_markup=inl_main_menu()
    )

@command_router.message(Command("start"))
async def start_command(message: Message, command: CommandObject):
    user_id = message.from_user.id
    cmd_name = command.command if command else "start"
    logger.info(f"[Start] User {user_id} triggered start via command")
    await send_start_photo(message, cmd_name)


@command_router.message(~F.fsm_state)
async def start_callback(message: Message, bot: Bot):
    user_id = message.from_user.id
    cmd_name = "start"
    logger.info(f"[Start] User {user_id} triggered start via callback")
    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.message_id,
    )
    await send_start_photo(message, cmd_name)