from aiogram import Router, Bot
from aiogram.types import Message, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.enums.chat_action import ChatAction
from aiogram.fsm.context import FSMContext

from keyboards.inl_keyboards import inl_translate_back
from logger import get_logger

from .fsm import GPTRequest, CelebrityTalk, QUIZ, Translate

from keyboards import inl_gpt_menu, inl_cancel, inl_quiz_menu

from utils.loading import LoadingController
from utils.enum_path import Path

from ai import chat_gpt
from ai.messages import GPTMessage
from ai.enums import GPTRole

fsm_router = Router()

logger = get_logger("FSM")

@fsm_router.message(GPTRequest.wait_for_request)
async def gpt_wait_for_request(message: Message, bot: Bot):
    """
        Ожидание запроса от пользователя
    """
    chat_id = message.chat.id

    logger.info("GPT request received", extra={"user_id": chat_id})

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
    try:
        response = await chat_gpt.request(msg_list, bot)
        logger.info("GPT response sent", extra={"user_id": chat_id})
    except Exception as e:
        logger.error("Error processing GPT response", extra={"user_id": chat_id})
        response = "Error"

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


@fsm_router.message(QUIZ.game)
async def user_answer(message: Message, state: FSMContext, bot: Bot):
    """
        Обработка ответа на QUIZ от юзера
    """
    chat_id = message.from_user.id
    logger.info("Quiz answer received", extra={"user_id": chat_id})

    message_list = await state.get_value('messages')
    message_id = await state.get_value('message_id')
    score = await state.get_value('score') or 0
    message_list.update(GPTRole.USER, message.text)
    response = await chat_gpt.request(message_list, bot)
    message_list.update(GPTRole.CHAT, response)
    await state.update_data(messages=message_list)
    if response == 'Правильно!':
        score += 1
        await state.update_data(score=score)
    response += f'\n\nВаш счет: {score} баллов!'
    logger.info("Quiz response ready", extra={"user_id": chat_id})

    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.message_id,
    )
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='quiz')),
            caption=response,
        ),
        chat_id=message.from_user.id,
        message_id=message_id,
        reply_markup=inl_quiz_menu(),
    )


@fsm_router.message(CelebrityTalk.dialog)
async def celebrity_talk(message: Message, state: FSMContext, bot: Bot):
    """
        Обработка сообщения от пользователя на разговор с известными личностями
    """
    chat_id=message.chat.id
    logger.info("Celebrity talk message received", extra={"user_id": chat_id})

    await bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.TYPING
    )
    message_list = await state.get_value('messages')
    celebrity = await state.get_value('celebrity')
    message_list.update(GPTRole.USER, message.text)
    response = await chat_gpt.request(message_list, bot)
    message_list.update(GPTRole.CHAT, response)
    await state.update_data(messages=message_list)
    logger.info("Celebrity talk response ready", extra={"user_id": chat_id})
    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=FSInputFile(Path.IMAGES.value.format(file=celebrity)),
        caption=response,
        reply_markup=inl_cancel()
    )


@fsm_router.message(Translate.text)
async def translate_text(message: Message, state: FSMContext, bot: Bot):
    """
        Обработка сообщения от пользователя и перевод
    """
    chat_id=message.from_user.id
    data = await state.get_data()
    message_id = data.get('message_id')
    language = data.get('language')
    user_text = message.text
    logger.info("Translate text received", extra={"user_id": chat_id})

    await bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.TYPING
    )

    msg_list = GPTMessage('translate')
    msg_list.update(GPTRole.USER, f"Переведи на {language}: {user_text}")

    try:
        response = await chat_gpt.request(msg_list, bot)
        logger.info("Translate response ready", extra={"user_id": chat_id})
    except Exception as e:
        logger.error("Error processing translate response", extra={"user_id": chat_id})
        response = "Произошла ошибка при переводе."

    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.message_id,
    )

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='translate')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=inl_translate_back(),
    )
