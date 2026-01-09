from collections import namedtuple

from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ

import os
from utils.enum_path import Path
from utils import FileManager


Button = namedtuple('Button', ['text', 'callback'])

def inl_main_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Рандомный факт 🧠', 'random'),
        Button('КВИЗ! ❓', 'quiz'),
        Button('Перевести', 'translate'),
        Button('Спросить GPT 🤖', 'gpt'),
        Button('Разговор со звездой 👤', 'talk')
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