""" Главное меню бота """
from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def keyboard_main():
    """ Клавиатура главного меню """
    names = {
        'Прикрепить график': 'load',
        'Прикрепленные графики': 'look_table',
        'Узнать состав смены': 'go',
        'Просмотреть пользователей': 'users',
        'Получить справку': 'help',
        'Скачать образец таблицы': 'example',
        'Выйти': 'quit'
    }

    buttons = [InlineKeyboardButton(text=name, callback_data=data) for name, data in names.items()]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
    return keyboard

def keyboard_back():
    """ Отдельная кнопка 'назад', в главное меню """
    button = InlineKeyboardButton(text='Назад', callback_data='menu')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard




