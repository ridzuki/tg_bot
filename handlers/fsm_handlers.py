from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InputMediaPhoto, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.chat_action import ChatAction
from aiogram.fsm.context import FSMContext

from .fsm import GPTRequest, CelebrityTalk, QUIZ

from keyboards import inl_main_menu, inl_random_menu, inl_gpt_menu
from keyboards.callback_data import CallbackMenu

from utils.loading import LoadingController
from utils import FileManager
from utils.enum_path import Path

from ai import chat_gpt
from ai.messages import GPTMessage
from ai.enums import GPTRole

fsm_router = Router()

@fsm_router.message(GPTRequest.wait_for_request)
async def wait_for_user_request(message: Message, state: FSMContext, bot: Bot):
    """
        Ожидание запроса от пользователя
    """
    chat_id = message.chat.id
    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file="gpt")),
        caption="Думаю"
    )

    loader = LoadingController(
        bot=bot,
        chat_id=chat_id,
        message=loading_message,
        text="Думаю",
    )
    await loader.start()
    msg_list = GPTMessage('gpt')
    msg_list.update(GPTRole.USER, message.text)
    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.message_id,
    )
    response = await chat_gpt.request(msg_list, bot)
    await loader.stop()
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='gpt')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=loading_message.message_id,
        reply_markup=inl_gpt_menu()
    )



