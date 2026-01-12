import json

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext

from logger import logger

from ai.enums import GPTRole

from .fsm import GPTRequest, CelebrityTalk, QUIZ, Translate

from keyboards import inl_cancel
from keyboards.inl_keyboards import inl_main_menu, inl_random_menu, inl_gpt_cancel, inl_talk_menu, inl_quiz_topics, inl_translate_menu
from keyboards.callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ, CallbackTranslate

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
    logger.info(f"[Menu] User {callback.from_user.id} opens the main menu")
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
    logger.info(f"[Random] User {chat_id} asks for a random fact")

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
    logger.info(f"[Random] Sending to {chat_id} a random fact: {caption}")

    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image_url,
        caption=caption,
        reply_markup=inl_random_menu()
    )

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info(f"[Random] Message deleted {chat_id}")
    except:
        logger.warning(f"[Random] Error in deleting {chat_id}")


@inline_router.callback_query(CallbackMenu.filter(F.button == 'quiz'))
async def get_quiz_menu(callback: CallbackQuery, callback_data: CallbackMenu, state:  FSMContext,bot: Bot):
    chat_id=callback.from_user.id
    logger.info(f"[QUIZ_INL] User {chat_id} asks for a quiz")
    await state.set_state(QUIZ.game)
    messages = await state.get_value("messages")
    if not messages:
        await state.update_data(score=0, messages=None, message_id=callback.message.message_id)
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inl_quiz_topics()
    )


@inline_router.callback_query(CallbackQUIZ.filter(F.button == 'quiz'))
async def get_subj(callback: CallbackQuery, callback_data: CallbackQUIZ, state: FSMContext, bot: Bot):
    chat_id=callback.from_user.id
    logger.info(f"[QUIZ_INL] User {chat_id} chooses a subject: {callback_data.subject}")
    message_list = await state.get_value('messages')
    if not message_list:
        message_list = GPTMessage('quiz')
    message_list.update(GPTRole.USER, callback_data.subject)
    response = await chat_gpt.request(message_list, bot)
    await state.update_data(messages=message_list)
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=response,
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inl_cancel(),
    )


# TODO: сделать удаление сообщения если это сообщение-меню или начат новый запрос (через кнопку)
@inline_router.callback_query(CallbackMenu.filter(F.button == 'gpt'))
async def get_gpt_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Разговоры с GPT
    """
    chat_id=callback.from_user.id
    logger.info(f"[GPT] User {chat_id} asks for a GPT conversation")
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


@inline_router.callback_query(CallbackMenu.filter(F.button == 'talk'))
async def get_talk_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Меню разговоров с известными личностями
    """
    chat_id=callback.from_user.id
    logger.info(f"[Talk_INL] User {chat_id} asks for a talk conversation")
    await state.clear()
    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inl_talk_menu()
    )


@inline_router.callback_query(CallbackTalk.filter(F.button == 'talk'))
async def talk_with_celebrity(callback: CallbackQuery, callback_data: CallbackTalk, state: FSMContext, bot: Bot):
    """
        Разговоры с известными личностями
    """
    chat_id=callback.from_user.id
    logger.info(f"[Talk_INL] User {chat_id} chooses a celebrity: {callback_data.celebrity}")
    await state.set_state(CelebrityTalk.dialog)
    message_list = GPTMessage(callback_data.celebrity)
    response = await chat_gpt.request(message_list, bot)
    message_list.update(GPTRole.CHAT, response)
    await state.update_data(messages=message_list, celebrity=callback_data.celebrity)
    await bot.edit_message_media(
        media=InputMediaPhoto(
                media=FSInputFile(Path.IMAGES.value.format(file=callback_data.celebrity)),
                caption=response,
            ),
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=inl_cancel(),
        )


# TODO тут что то надо придумать с тем от куда берется текст сообщения
@inline_router.callback_query(CallbackMenu.filter(F.button == 'translate'))
async def translate_menu(callback: CallbackQuery, callback_data: CallbackMenu, bot: Bot):
    """
        Меню переводчика
    """
    chat_id = callback.from_user.id
    logger.info(f"[Translate] User {chat_id} opens translation menu")

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_translate_menu()
    )


@inline_router.callback_query(CallbackTranslate.filter())
async def translate_text(callback: CallbackQuery, callback_data: CallbackTranslate, state: FSMContext, bot: Bot):
    """
        Переводчик
    """
    lang = callback_data.language
    chat_id = callback.from_user.id
    logger.info(f"[Translate] User {chat_id} selected language: {lang}")

    await state.set_state(Translate.text)
    await state.update_data(language=lang)

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=f"Выбран язык: {lang}\nОтправьте текст для перевода",
        ),
        chat_id = chat_id,
        message_id = callback.message.message_id,
        reply_markup = inl_cancel()
    )

