from collections import namedtuple

from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.builder import build_topic_map
from .callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ, CallbackTranslate, CallbackRecommend

import os
from utils.enum_path import Path
from utils import FileManager


Button = namedtuple('Button', ['text', 'callback'])

def inl_main_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Рандомный факт 🧠', 'random'),
        Button('КВИЗ! ❓', 'quiz'),
        Button('Переводчик 🌐', 'translate'),
        Button('Спросить GPT 🤖', 'gpt'),
        Button('Разговор со звездой 👤', 'talk'),
        Button('Рекомендации', 'recommendation')
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback_data=CallbackMenu(button=button.callback)
        )
    keyboard.adjust(2,2)
    return keyboard.as_markup()

def inl_random_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Хочу еще!', 'random'),
        Button('Закончить!', 'start'),
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback_data=CallbackMenu(button=button.callback),
        )
    return keyboard.as_markup()

def inl_quiz_topics():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Программирование', 'quiz_prog'),
        Button('Математика', 'quiz_math'),
        Button('Биология', 'quiz_biology'),
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback_data=CallbackQUIZ(
                button='quiz',
                subject=button.callback
            )
        )
    keyboard.button(
        text='Закончить!',
        callback_data=CallbackMenu(button='start')
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def inl_quiz_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Еще вопрос!',
        callback_data=CallbackQUIZ(
            button='quiz',
            subject='quiz_more',
        ),
    )
    keyboard.button(
        text='Сменить тему!',
        callback_data=CallbackMenu(button='quiz'),
    )
    keyboard.button(
        text='Закончить!',
        callback_data=CallbackMenu(button='start'),
    )
    return keyboard.as_markup()

def inl_gpt_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Еще запрос', 'gpt'),
        Button('Закончить!', 'start')
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback_data=CallbackMenu(button=button.callback),
        )
    return keyboard.as_markup()

def inl_gpt_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Отмена',
        callback_data=CallbackMenu(button='start'),
    )
    return keyboard.as_markup()

def inl_talk_menu():
    celebrities = [file.rsplit('.', 1)[0] for file in os.listdir(Path.IMG_DIR.value) if file.startswith('talk_')]
    keyboard = InlineKeyboardBuilder()
    for celebrity in celebrities:
        text_button = FileManager.read_txt(Path.PROMPTS, celebrity).split(',', 1)[0].split(' - ')[-1]
        keyboard.button(
            text=text_button,
            callback_data=CallbackTalk(
                button = 'talk',
                celebrity=celebrity
            )
        )
    keyboard.button(
        text='В главное меню',
        callback_data=CallbackMenu(button='start'),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def inl_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Закончить!',
        callback_data=CallbackMenu(button='start'),
    )
    return keyboard.as_markup()

def inl_translate_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Английский', 'en'),
        Button('Греческий', 'gr'),
        Button('Русский', 'ru')
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback_data=CallbackTranslate(
                button='translate',
                language=button.callback
            ),
        )
    keyboard.button(
        text="Закончить!",
        callback_data=CallbackMenu(button="start")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()

def inl_translate_back():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Сменить язык',
        callback_data=CallbackMenu(button='translate'),
    )
    return keyboard.as_markup()

def inl_recommendation_topics():
    keyboard = InlineKeyboardBuilder()
    topic_map = build_topic_map(Path.OTHER, "genres.txt")
    for topic_name, data in topic_map.items():
        keyboard.button(
            text=data["category"],
            callback_data=CallbackRecommend(
                button='recommendation',
                category=topic_name,
                genre = ""
            )
        )
    keyboard.button(
        text='Закончить!',
        callback_data=CallbackMenu(button='start')
    )

    keyboard.adjust(1)
    return keyboard.as_markup()

def inl_recommendation_genre(category):
    topic_map = build_topic_map(Path.OTHER, "genres.txt")
    data = topic_map.get(category)
    if not data:
        return None

    keyboard = InlineKeyboardBuilder()
    for genre_name in data["genres"]:
        keyboard.button(
            text= genre_name,
            callback_data=CallbackRecommend(
                button='recommendation',
                category=category,
                genre=genre_name
            )
        )

    keyboard.button(
        text='К выбору категории',
        callback_data=CallbackMenu(button='recommendation')
    )

    keyboard.adjust(2)
    return keyboard.as_markup()

def inl_recommend_more():
    pass
