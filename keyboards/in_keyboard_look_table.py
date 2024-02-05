from typing import List, Dict, Tuple

from utils.all import months_dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def keyboard_look_table(storage_list: List[Tuple[str, str]], command_buttons: int = 2) -> InlineKeyboardMarkup:
    """ Выводит кнопки с месяцами. При нажатии либо открывается ссылка, либо передается колбэк для открытия
    локального файла. Принимает результат ф-ции  - models.models_utils.get_all_table().
    В callback_data передает строку: [Номер_месяца ссылка / путь]
    :param storage_list: список кортежей [(Номер_месяца(str), ссылка/путь(str))]
    :param command_buttons: кнопки управления. Если выставить 1 - только кнопка 'В главное меню'.
    """
    all_month: Dict[str, str] = months_dict

    buttons_months = [
        InlineKeyboardButton(
            text=all_month[month],
            url=storage if 'https:' in storage else None,
            callback_data=storage if 'https:' not in storage else None
        ) for month, storage in storage_list]

    buttons_control = [
        InlineKeyboardButton(text='|x| Удалить неактуальный график', callback_data='del_table'),
        InlineKeyboardButton(text='|<| В главное меню', callback_data='menu')
    ]
    buttons_row3 = [buttons_months[n:n+3] for n in range(0, len(buttons_months), 3)]
    for n, button in enumerate(buttons_control):
        if command_buttons == 1 and n == 0: continue
        buttons_row3.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons_row3)
    return keyboard

