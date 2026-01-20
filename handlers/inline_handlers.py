import json
import re

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext

from logger import get_logger

from ai.enums import GPTRole

from .fsm import GPTRequest, CelebrityTalk, QUIZ, Translate, Recommendation

from keyboards import inl_cancel
from keyboards.inl_keyboards import inl_main_menu, inl_random_menu, inl_gpt_cancel, inl_talk_menu, inl_quiz_topics, \
    inl_translate_menu, inl_translate_back, inl_recommendation_topics, inl_recommendation_genre, inl_recommendation_actions
from keyboards.callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ, CallbackTranslate, CallbackRecommend

from utils import FileManager
from utils.enum_path import Path
from utils.loading import LoadingController

from ai import chat_gpt
from ai.messages import GPTMessage

inline_router = Router()

logger = get_logger("INLINE")


@inline_router.callback_query(CallbackMenu.filter(F.button == 'start'))
@inline_router.callback_query(CallbackMenu.filter(F.button == 'main'))
async def get_main_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Главное меню с кнопками
    """
    logger.info("Opens main menu", extra={"user_id": callback.from_user.id})
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
    """
    chat_id = callback.from_user.id
    logger.info("Random fact requested", extra={"user_id": chat_id})

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
    logger.info("Sending random fact", extra={"user_id": chat_id})

    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image_url,
        caption=caption,
        reply_markup=inl_random_menu()
    )

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info("Loading message deleted", extra={"user_id": chat_id})
    except:
        logger.warning("Error deleting loading message", extra={"user_id": chat_id})


@inline_router.callback_query(CallbackMenu.filter(F.button == 'quiz'))
async def get_quiz_menu(callback: CallbackQuery, callback_data: CallbackMenu, state:  FSMContext,bot: Bot):
    chat_id=callback.from_user.id
    logger.info("Open quiz menu", extra={"user_id": chat_id})
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
    logger.info(f"Quiz subject chosen: {callback_data.subject}", extra={"user_id": chat_id})
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
    logger.info("Open GPT menu", extra={"user_id": chat_id})
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
    logger.info("Open talk menu", extra={"user_id": chat_id})
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
    logger.info(f"Celebrity chosen: {callback_data.celebrity}", extra={"user_id": chat_id})
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
    logger.info("Open translation menu", extra={"user_id": chat_id})

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
    logger.info(f"Language selected: {lang}", extra={"user_id": chat_id})

    await state.set_state(Translate.text)
    await state.update_data(language=lang, message_id=callback.message.message_id)

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=f"Выбран язык: {lang}\nОтправьте текст для перевода",
        ),
        chat_id = chat_id,
        message_id = callback.message.message_id,
        reply_markup = inl_translate_back()
    )


@inline_router.callback_query(CallbackMenu.filter(F.button == 'recommendation'))
async def recommendation_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Меню рекомендаций
    """
    chat_id = callback.from_user.id
    logger.info("Open recommendation menu", extra={"user_id": chat_id})

    await state.set_state(Recommendation.dislikes)
    await state.update_data(dislikes=[], current=None, messages=None)

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption=FileManager.read_txt(Path.MESSAGES, callback_data.button),
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_recommendation_topics()
    )


@inline_router.callback_query(CallbackRecommend.filter(F.category and ~F.genre))
async def genres_menu(callback: CallbackQuery, callback_data: CallbackRecommend, bot: Bot):
    """
        Меню жанров для выбранной темы
    """
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    category = callback_data.category
    logger.info(f"Open genre menu for category: {category}", extra={"user_id": chat_id})

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption="Выберите жанр 👇",
        ),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=inl_recommendation_genre(category)
    )


@inline_router.callback_query(CallbackRecommend.filter(F.button == 'recommendation'))
async def give_recommendation(callback: CallbackQuery, callback_data: CallbackRecommend, state: FSMContext, bot: Bot):
    chat_id = callback.from_user.id
    category = callback_data.category
    genre = callback_data.genre
    logger.info(f"Give recommendation requested: category={category}, genre={genre}", extra={"user_id": chat_id})

    data = await state.get_data()
    dislikes: list[str] = data.get("dislikes", [])
    logger.debug(f"Current dislikes before request: {dislikes}", extra={"user_id": chat_id})

    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
        caption="Вспоминаю рекомендации"
    )
    logger.debug("Loading message sent for recommendation", extra={"user_id": chat_id})

    loader = LoadingController(
        bot=bot,
        chat_id=chat_id,
        message=loading_message,
        text="Вспоминаю рекомендации",
    )
    await loader.start()
    logger.debug("Loader started", extra={"user_id": chat_id})

    msg_list = GPTMessage('recommendation.txt')
    msg_list.update(GPTRole.USER, f"{category} {genre}. Не интересует: {dislikes}")
    logger.info(f"GPT prompt JSON: {msg_list.json()}", extra={"user_id": chat_id})
    logger.info("Sending GPT recommendation request", extra={"user_id": chat_id})

    response = await chat_gpt.request(msg_list, bot)
    logger.info("GPT recommendation response received", extra={"user_id": chat_id})

    await state.update_data(messages=msg_list)
    await loader.stop()
    logger.debug("Loader stopped", extra={"user_id": chat_id})

    match = re.search(r'"([^"]+)"\s+—', response)
    item_title = match.group(1) if match else None
    if not item_title:
        # Fallbacks: try any quoted string, then first line before newline/dash
        alt_match = re.search(r'"([^"]+)"', response)
        if alt_match:
            item_title = alt_match.group(1)
        else:
            first_line = (response or "").splitlines()[0] if response else ""
            item_title = re.split(r'[—-]', first_line)[0].strip()
            if not item_title:
                item_title = None
    logger.debug(f"Extracted item title: {item_title}", extra={"user_id": chat_id})

    await state.update_data(current={
        "category": category,
        "genre": genre,
        "item": item_title,
    })
    logger.debug("State updated with current recommendation", extra={"user_id": chat_id})

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_recommendation_actions(category, genre, item_title)
    )
    logger.info("Recommendation message edited and actions attached", extra={"user_id": chat_id})

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info("Loading message deleted", extra={"user_id": chat_id})
    except Exception as e:
        logger.warning(f"Error deleting loading message: {e}", extra={"user_id": chat_id})


@inline_router.callback_query(CallbackRecommend.filter(F.button == 'dislike'))
async def dislike_recommendation(callback: CallbackQuery, callback_data: CallbackRecommend, state: FSMContext, bot: Bot):
    chat_id = callback.from_user.id
    item = (callback_data.item or "").strip()
    logger.info("Dislike clicked", extra={"user_id": chat_id})

    data = await state.get_data()
    current = data.get("current") or {}
    category = current.get("category")
    genre = current.get("genre")
    prev_item = (current.get("item") or "").strip()

    dislikes: list[str] = data.get("dislikes", [])
    before_len = len(dislikes)
    if prev_item and prev_item not in dislikes:
        dislikes.append(prev_item)
        logger.info(
            f"Dislike added: '{prev_item}' (category={category}, genre={genre})",
            extra={"user_id": chat_id}
        )
    else:
        logger.info(
            f"No dislike added (prev_item='{prev_item}')",
            extra={"user_id": chat_id}
        )

    if len(dislikes) != before_len:
        logger.debug(f"Dislikes updated: {dislikes}", extra={"user_id": chat_id})
    await state.update_data(dislikes=dislikes)

    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
        caption="Вспоминаю рекомендации"
    )
    logger.debug("Loading message sent for dislike flow", extra={"user_id": chat_id})

    loader = LoadingController(bot=bot, chat_id=chat_id, message=loading_message, text="Вспоминаю рекомендации")
    await loader.start()
    logger.debug("Loader started", extra={"user_id": chat_id})

    msg_list = data.get("messages") or GPTMessage('recommendation.txt')
    msg_list.update(GPTRole.USER, f"{category} {genre}. Не интересует: {dislikes}")
    logger.info(f"GPT prompt JSON (after dislike): {msg_list.json()}", extra={"user_id": chat_id})
    logger.info("Sending GPT recommendation request after dislike", extra={"user_id": chat_id})

    response = await chat_gpt.request(msg_list, bot)
    logger.info("GPT recommendation response received after dislike", extra={"user_id": chat_id})

    await state.update_data(messages=msg_list)
    await loader.stop()
    logger.debug("Loader stopped", extra={"user_id": chat_id})

    match = re.search(r'"([^"]+)"\s+—', response)
    item_title = match.group(1) if match else None
    await state.update_data(current={"category": category, "genre": genre, "item": item_title})
    logger.debug(f"Next item extracted and state updated: {item_title}", extra={"user_id": chat_id})

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_recommendation_actions(category, genre, item_title)
    )
    logger.info("Recommendation updated after dislike", extra={"user_id": chat_id})

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info("Loading message deleted", extra={"user_id": chat_id})
    except Exception as e:
        logger.warning(f"Error deleting loading message: {e}", extra={"user_id": chat_id})


