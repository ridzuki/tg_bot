import json

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext

from logger import logger

from ai.enums import GPTRole
from misc import print_message

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


@inline_router.callback_query(CallbackMenu.filter(F.button == 'start'))
@inline_router.callback_query(CallbackMenu.filter(F.button == 'main'))
async def get_main_menu(callback: CallbackQuery, callback_data: CallbackMenu, state: FSMContext, bot: Bot):
    """
        Главное меню с кнопками
    """
    logger.info(f"[MenuINL] User {callback.from_user.id} opens the main menu")
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
    logger.info(f"[RandomINL] User {chat_id} asks for a random fact")

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
    logger.info(f"[RandomINL] Sending to {chat_id} a random fact: {caption}")

    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image_url,
        caption=caption,
        reply_markup=inl_random_menu()
    )

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info(f"[RandomINL] Message deleted {chat_id}")
    except:
        logger.warning(f"[RandomINL] Error in deleting {chat_id}")


@inline_router.callback_query(CallbackMenu.filter(F.button == 'quiz'))
async def get_quiz_menu(callback: CallbackQuery, callback_data: CallbackMenu, state:  FSMContext,bot: Bot):
    chat_id=callback.from_user.id
    logger.info(f"[QUIZINL] User {chat_id} asks for a quiz")
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
    logger.info(f"[QUIZINL] User {chat_id} chooses a subject: {callback_data.subject}")
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
    logger.info(f"[GPTINL] User {chat_id} asks for a GPT conversation")
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
    logger.info(f"[TalkINL] User {chat_id} asks for a talk conversation")
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
    logger.info(f"[TalkINL] User {chat_id} chooses a celebrity: {callback_data.celebrity}")
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
    logger.info(f"[TranslateINL] User {chat_id} opens translation menu")

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
    logger.info(f"[TranslateINL] User {chat_id} selected language: {lang}")

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
async def recommendation_menu(callback: CallbackQuery, callback_data: CallbackMenu, bot: Bot):
    """
        Меню рекомендаций
    """
    chat_id = callback.from_user.id
    logger.info(f"[RecommendationINL] User {chat_id} opens recommendation menu")

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
    logger.info(f"[RecommendationINL] User {chat_id} opens genre menu for category: {category}")

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file=callback_data.button)),
            caption="Выберите жанр 👇",
        ),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=inl_recommendation_genre(category)
    )


@inline_router.callback_query(CallbackRecommend.filter((F.genre) & (F.button != "dislike")))
async def take_recommendation(callback: CallbackQuery, callback_data: CallbackRecommend, state: FSMContext, bot: Bot):
    """
        Выдача рекомендаций
    """
    chat_id = callback.from_user.id
    category = callback_data.category
    genre = callback_data.genre
    logger.info(f"[RecommendationINL] User {chat_id} takes recommendation for category: {category} and genre: {genre}")

    data = await state.get_data()
    dislikes = data.get("dislikes", [])

    logger.info(
        f"[RecommendationINL] Current dislikes for user={chat_id}: {dislikes}"
    )

    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
        caption="Вспоминаю рекомендации"
    )

    loader = LoadingController(
        bot=bot,
        chat_id=chat_id,
        message=loading_message,
        text="Вспоминаю рекомендации",
    )

    await loader.start()

    msg_list = GPTMessage('recommendation.txt')
    msg_list.update(GPTRole.USER, f"{category} {genre}. Не предлагай: {dislikes}")

    logger.info(f"[RecommendationINL] GPT request | user={chat_id} | prompt={msg_list.json()}")

    response = await chat_gpt.request(msg_list, bot)

    logger.info(
        f"[RecommendationINL] GPT response | user={chat_id} | response_preview={response}")

    await state.update_data(messages=msg_list)
    await loader.stop()

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_recommendation_actions(category, genre)
    )

    logger.info(
        f"[RecommendationINL] Recommendation sent | user={chat_id} | message_id={callback.message.message_id}"
    )

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        logger.info(f"[RecommendationINL] Message deleted {chat_id}")
    except:
        logger.warning(f"[RecommendationINL] Error in deleting {chat_id}")


@inline_router.callback_query(CallbackRecommend.filter(F.button == 'dislike'))
async def dislike_item(callback: CallbackQuery, callback_data: CallbackRecommend, state: FSMContext, bot: Bot):
    """
        Обработка кнопки 'Не нравится'
    """
    chat_id = callback.from_user.id
    category = callback_data.category
    genre = callback_data.genre
    raw_item = callback_data.item
    if raw_item:
        item = raw_item.strip().split('—', 1)[0]
    else:
        item = None

    logger.info(f"[RecommendationINL] User {chat_id} dislikes item: {item}")

    data = await state.get_data()
    dislikes = data.get("dislikes", [])

    if item and item not in dislikes:
        dislikes.append(item)
        logger.info(f"[RecommendationINL] Item added to dislikes | user={chat_id} | dislikes={dislikes}")
    else:
        logger.debug(f"[RecommendationINL] Item already in dislikes or empty | user={chat_id}")

    await state.update_data(dislikes=dislikes)

    loading_message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
        caption="Вспоминаю другие рекомендации..."
    )

    loader = LoadingController(
        bot=bot,
        chat_id=chat_id,
        message=loading_message,
        text="Вспоминаю рекомендации",
    )
    await loader.start()

    msg_list = GPTMessage('recommendation.txt')
    msg_list.update(GPTRole.USER, f"{category} {genre}. Не интересуют: {dislikes}")

    logger.info(f"[RecommendationINL] GPT request after dislike | user={chat_id} | prompt={msg_list.json()}")

    response = await chat_gpt.request(msg_list, bot)

    logger.info(f"[RecommendationINL] GPT response after dislike | user={chat_id} | response_preview={response}")

    await state.update_data(messages=msg_list)
    await loader.stop()

    await bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(Path.IMAGES.value.format(file='recommendation')),
            caption=response,
        ),
        chat_id=chat_id,
        message_id=callback.message.message_id,
        reply_markup=inl_recommendation_actions(category, genre)
    )

    logger.info(f"[RecommendationINL] Updated recommendation after dislike | user={chat_id}")

    try:
        await bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
    except:
        logger.warning(f"[RecommendationINL] Failed to delete loading message {chat_id}")