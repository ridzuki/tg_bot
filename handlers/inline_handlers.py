import asyncio
import json
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile, InputFile
from aiogram.enums.chat_action import ChatAction

from aiogram.fsm.context import FSMContext
from keyboards.inl_keyboards import keyboard_main_menu, random

from utils import FileManager
from utils.enum_path import Path

from ai import chat_gpt
from ai.messages import GPTMessage

from keyboards.callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ

inline_router = Router()


@inline_router.callback_query(CallbackMenu.filter(F.button == 'start'))
@inline_router.callback_query(CallbackMenu.filter(F.button == 'main'))
async def main_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Главное меню с кнопками
    """
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
    """
        Генерация случайного факта + картинки через GPT
        с анимацией 'Ищу факт...' и TYPING
    """

    await bot.send_chat_action(
        chat_id=callback.from_user.id,
        action=ChatAction.TYPING,
    )

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption="Ищу факт.",
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    loading_task = True

    async def loading_animation():
        dots = ["", ".", "..", "..."]
        i = 0
        while loading_task:
            try:
                await bot.edit_message_caption(
                    chat_id=callback.from_user.id,
                    message_id=callback.message.message_id,
                    caption=f"Ищу факт{dots[i % 4]}",
                )
            except:
                pass
            i += 1
            await asyncio.sleep(0.5)

    animation = asyncio.create_task(loading_animation())

    async def typing_loop():
        while loading_task:
            try:
                await bot.send_chat_action(chat_id=callback.from_user.id, action=ChatAction.TYPING)
            except:
                pass
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(typing_loop())

    raw_response = await chat_gpt.request(GPTMessage('random'), bot)

    try:
        data = json.loads(raw_response)
        caption = data.get("caption", "Случайный факт")
        image_prompt = data.get("image_prompt", "")
    except json.JSONDecodeError:
        caption = raw_response
        image_prompt = ""

    if image_prompt:
        image_url = await chat_gpt.generate_image(image_prompt, bot)
    else:
        image_url = Path.IMAGES.value.format(file=callback_data.button)

    loading_task = False
    await animation
    await typing_task

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=image_url,
            caption=caption,
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=random(),
    )
