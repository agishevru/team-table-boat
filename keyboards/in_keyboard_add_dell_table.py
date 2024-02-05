""" Клавиатура для выбора загрузки таблицы """
from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def add_xlsx1():
    """ Простая клавиатура выбора способа загрузки таблицы """
    names = {'Сохранить ссылку Google Sheets': 'save_url',
             'Загрузить Exel файл': 'save_file',
             'Назад': 'menu'}
    buttons = [InlineKeyboardButton(text=name, callback_data=data) for name, data in names.items()]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
    return keyboard


def keyboard_months(current_months: List[str] = None) -> InlineKeyboardMarkup:
    """ Кнопки с месяцами. Передает в callback_data: номер_месяца | back
    :param current_months: Опционно, список месяцев ['01', '02'..]
    """
    months = {
        "01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель", "05": "Май", "06": "Июнь", "07": "Июль",
        "08": "Август", "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
    }
    if current_months:
        buttons = [
            InlineKeyboardButton(text=months[month], callback_data=month) for month in current_months
            ]
    else:
        buttons = [
            InlineKeyboardButton(text=alias_month, callback_data=f'{num}') for num, alias_month in months.items()
        ]
    button_back = InlineKeyboardButton(text="В главное меню", callback_data="menu")
    buttons.append(button_back)
    # по три в ряд
    buttons_row3 = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons_row3)
    return keyboard

def keyboard_cancel():
    """ Выход из стейта """
    button = InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard

def kb_yes_no():
    """ Да / Нет """
    buttons = [
        InlineKeyboardButton(text=choose, callback_data=data) for choose, data in {'Да': 'yes', 'Нет': 'menu'}.items()
    ]
    keyboard = (InlineKeyboardMarkup(inline_keyboard=[buttons]))
    return keyboard


