""" Основные исполнительные хэндлеры для главного меню (/menu) """
import re
from typing import Dict, List, Tuple, Union

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from keyboards.in_keyboard_look_table import keyboard_look_table
from keyboards.in_keyboard_menu import keyboard_main, keyboard_back
from log_settings import log
from keyboards.in_keyboard_add_dell_table import add_xlsx1
from models.db import Users
from models.models_utils import get_or_create_user, get_all_table
from utils.all import open_profile, months_dict
from utils.exel_reader import save_google_sheet_locally, get_today_employees

router = Router()


@router.message(CommandStart())
async def start(message: Message, user: str, session: AsyncSession) -> None:
    """ Старт бота """
    log.warning(f'user - /start')
    # создание пользователя
    await get_or_create_user(message, session)
    await message.answer('👷🏻‍♂️ Вы запустили приложение для отображения рабочих смен:\n'
                         '- из файлов .xlsx\n'
                         '- из онлайн таблиц Google sheets\n\n'
                         'Чтобы начать, отправьте /menu\n')

@router.message(Command('menu'), StateFilter(None))
async def cmd_menu(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    """ Главное меню бота """
    log.warning(f'user - /menu')
    text = ('<code>'
            '~~~~~~~~~~~~~~~~~~~~~~~~~\n'
            '|   Выберете действие   |\n'
            '~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'
            '</code>\n')
    if edit_message is True:
        return await message.edit_text(text=text, reply_markup=keyboard_main())
    await message.answer(text=text, reply_markup=keyboard_main())


async def cmd_look_table(message: Message, user: str, session: AsyncSession, edit_message: bool = False) -> None:
    """ Пункт меню просмотреть таблицы.  """
    log.warning(f'user look_table')
    tables: List[Tuple[str, str]] = await get_all_table(session=session)
    if tables:
        months: Dict[str, str] = months_dict
        await message.edit_text(
            f'📋 Зарегистрированы графики за <code>[ {" ".join([months[n[0]] for n in tables])} ]</code>.\n'
            f'Чтобы просмотреть нужный, выберете кнопку ниже.',
            reply_markup=keyboard_look_table(storage_list=tables))



async def cmd_load(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    log.warning(f'user get load table')
    await message.edit_text('👷🏻‍♂️ Для анализа таблицы - загрузите ее удобным способом 👇',
                            reply_markup=add_xlsx1())



async def cmd_go(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    """ Вывод смены """
    await message.edit_text(f'🥷 Перед тем как сделать запрос, таблица должна быть\n'
                            f'сохранена через кнопку меню\n'
                            f'<code>'
                            f'--------------------\n'
                            f'|прикрепить таблицу|\n'
                            f'--------------------</code>\n\n'
                            f'🔍 Чтобы узнать состав смены, отправьте <i>число.месяц</i>\n'
                            f'<code>Пример</code>: <i>31.12</i>')



@router.message(F.text.regexp(re.compile(r'(\d{2}\.\d{2})')), StateFilter(None))
async def cmd_get(message: Message, user: str, session: AsyncSession):
    """ Чтенице таблицы """
    log.warning(f'user get {message.text}')
    date: str = message.text
    day: str = date.split('.')[0]
    month: str = date.split('.')[1]
    pattern = r'\b(?:0[1-9]|[12]\d|3[01])\b'  # Забирает цифру от 01 до 31
    day_accept: str = ''.join(re.findall(pattern, day))
    if not day_accept:
        return await message.answer(f'❌ День {day} введен некорректно. Введите двухзначное число, например 01.01')
    # загрузка файла из ссылки (запрашивает в бд за нужный месяц)

    file: Union[str, bool] = await save_google_sheet_locally(month=month, session=session)
    employees = await get_today_employees(file_path=file, day=day)
    await message.answer(employees)


async def cmd_help(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    log.warning(f'user - /help')
    text = (f'📆 Вы запустили приложение для отображения рабочих смен:\n'
            f'- из файлов .xlsx\n'
            f'- из онлайн таблиц Google sheets\n\n'
            f'Чтобы получить информацию о составе смены - таблицу нужно сначала прикрепить, выбрав в меню '
            f'<b>|загрузить таблицу|</b>\n\n'
            f'Чтобы узнать кто выходит в конкретный день\n'
            f'введите дату: <b>|01.01|</b>\n\n'
            f'Для просмотра активных пользователей бота, выберете\n'
            f'<b>|просмотреть пользователей|</b>')
    if edit_message is True: await message.edit_text(text=text, reply_markup=keyboard_back())
    else: await message.answer(text=text, reply_markup=keyboard_back())


async def cmd_users(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    """ Показывает актуальных пользователей из списка c ссылкой на профиль """
    log.warning(f'user watch all users')
    query = await session.execute(select(Users))
    users = query.scalars()
    text = 'Активные пользователи бота:\n'
    text += "\n".join(f"{open_profile(user.user_id, '👤')} <code>{user.username}</code>" for user in users)
    if edit_message is True:
        await message.edit_text(text)
    else: await message.answer(text)


async def cmd_example(message: Message, user: str, session: AsyncSession, edit_message: bool = False):
    log.warning(f'user get example table')
    instruction: str = ('Для того чтобы бот корректно считал данные, рекомендуется воспользоваться данным шаблоном.'
                        'Бот автоматически выделит заголовки, написанные заглавными буквами в названия отделов.')
    await message.edit_text(f'{instruction}', reply_markup=keyboard_back())
    table_from_local = FSInputFile("example_table.xlsx")
    result = await message.answer_document(
        table_from_local,
        caption="Шаблон для заполнения"
    )
    # file_ids.append(result.document.file_id)



