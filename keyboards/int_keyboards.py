from collections import namedtuple

from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import CallbackMenu, CallbackTalk, CallbackQUIZ


Button = namedtuple('Button', ['text', 'callback'])

def keyboard_main_menu():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Рандомный факт', 'random'),
        Button('КВИЗ!', 'quiz'),
        Button('Перевести', 'translate'),
        Button('Спросить GPT', 'gpt'),
        Button('Разговор со звездой', 'talk')
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback=CallbackMenu(button=button.callback)
        )
    keyboard.adjust(2,2)
    return keyboard.as_markup()

def random():
    keyboard = InlineKeyboardBuilder()
    buttons = [
        Button('Хочу еще!', 'random'),
        Button('Закончить!', 'start'),
    ]
    for button in buttons:
        keyboard.button(
            text=button.text,
            callback=CallbackMenu(button=button.callback),
        )
    return keyboard.as_markup()