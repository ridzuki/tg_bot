import asyncio
import json

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile, InputFile
from aiogram.enums.chat_action import ChatAction
from aiogram.fsm.context import FSMContext

from handlers.fsm import GPTRequest
from keyboards.inl_keyboards import inl_main_menu, inl_random_menu, inl_gpt_cancel
from keyboards.callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ

# from .fsm import GPTRequest, CelebrityTalk, QUIZ

from utils import FileManager
from utils.enum_path import Path
from utils.loading import LoadingController

from ai import chat_gpt
from ai.messages import GPTMessage


inline_router = Router()


@inline_router.callback_query(CallbackMenu.filter(F.button == 'start'))
@inline_router.callback_query(CallbackMenu.filter(F.button == 'main'))
async def get_main_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
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
        reply_markup=inl_main_menu(),
    )


# TODO: сделать удаление сообщения если это сообщение-меню
@inline_router.callback_query(CallbackMenu.filter(F.button == 'random'))
async def get_random_fact(callback: CallbackQuery, callback_data: CallbackMenu, bot: Bot):
    """
        Генерация случайного факта + картинки через GPT
        с анимацией 'Ищу факт...' и TYPING
    """
    chat_id = callback.from_user.id

    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
        caption="Ищу факт"
    )

    loader = LoadingController(
        bot=bot,
        chat_id=chat_id,
        message=loading_message,
        text="Ищу факт",
    )
    await loader.start()

    raw_response = await chat_gpt.request(GPTMessage('random'), bot)

    try:
        data = json.loads(raw_response)
        caption = data.get("caption", "Случайный факт")
        image_prompt = data.get("image_prompt", "")
    except json.JSONDecodeError:
        caption = raw_response
        image_prompt = ""

    loader.update_text('Рисую картинку к факту')

    if image_prompt:
        image_url = await chat_gpt.generate_image(image_prompt, bot)
    else:
        image_url = Path.IMAGES.value.format(file=callback_data.button)

    await loader.stop()
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image_url,
        caption=caption,
        reply_markup=inl_random_menu()
    )

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
    except:
        pass


#
# @inline_router.callback_query(CallbackMenu.filter(F.button == 'quiz'))
# async def get_quiz_menu(callback: CallbackQuery, callback_data: CallbackMenu, bot: Bot):
#     await state.set_state(QUIZ.game)
#     messages = await state.get_value("messages")
#     if not messages:
# TODO: сделать удаление сообщения если это сообщение-меню или начат новый запрос (через кнопку)
@inline_router.callback_query(CallbackMenu.filter(F.button == 'gpt'))
async def get_gpt_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Разговоры с GPT
    """
    await state.set_state(GPTRequest.wait_for_request)
    await state.update_data(message_id=callback.message.message_id)
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inl_gpt_cancel()
    )