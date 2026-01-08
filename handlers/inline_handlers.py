from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.enums.chat_action import ChatAction

from aiogram.fsm.context import FSMContext
from keyboards.int_keyboards import keyboard_main_menu, random

from utils import FileManager
from utils.enum_path import Path

from ai import chat_gpt
from ai.messages import GPTMessage

from keyboards.callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ


inline_router = Router()


@inline_router.callback_query(CallbackMenu.filter(F.button == 'start'))
@inline_router.callback_query(CallbackMenu.filter(F.button == 'main'))
async def main_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard_main_menu(),
    )


@inline_router.callback_query(CallbackMenu.filter(F.button == 'random'))
async def random_handler(callback: CallbackQuery, callback_data: CallbackMenu, bot: Bot):
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )
    await bot.send_chat_action(
        chat_id=callback.from_user.id,
        action=ChatAction.TYPING,
    )
    response = await chat_gpt.request(GPTMessage('random'), bot)
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=response,
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=random(),
    )