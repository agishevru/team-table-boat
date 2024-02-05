""" Сценарии """
import os
from typing import Tuple, List, Dict

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from handlers.handlers_common import cmd_menu
from keyboards.in_keyboard_add_dell_table import keyboard_months, keyboard_cancel, kb_yes_no
from models.db import UrlGoogleSheets_month
from models.models_utils import get_all_table, delete_table
from utils.exel_reader import save_google_sheet_locally
from utils.all import months_dict
from log_settings import log

router = Router()


@router.callback_query(~StateFilter(None), F.data == 'menu')
async def cancel_state_and_go_menu(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Кнопка в главное меню из любого стейта """
    log.warning(f'user cansel state [{state}]')
    await callback.answer()
    await state.clear()
    await cmd_menu(message=callback.message, user=user, session=session, edit_message=True)


# Сохранение ссылки на гугл шитс
class SaveUrlTable(StatesGroup):
    """ Загрузка ссылок на таблицы """
    get_month = State()
    load_url = State()

@router.callback_query(F.data == 'save_url', StateFilter(None))
async def choose_save_url(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Сохранить ссылку на google sheets"""
    log.warning(f'user clicked [save_url]')
    await callback.answer()
    await callback.message.edit_text('🏗 Выберете месяц, за который хотите прикрепить график\n', reply_markup=keyboard_months())
    #ставим стейт выбор месяца
    await state.set_state(SaveUrlTable.get_month)

@router.callback_query(StateFilter(SaveUrlTable.get_month))
async def choose_month(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Запись в бд месяца """
    log.warning(f'user choose for save_url [{callback.data.split()[0]} month]')
    await callback.answer()
    months: Dict[str, str] = months_dict
    await callback.message.edit_text(f'👷🏻‍♂️ Отлично, выбран <code>{months[callback.data]}</code>\n'
                                     f'⛓ Теперь отправьте ссылку на таблицу Google Sheets')
    # обновление информации за указанный месяц
    await session.merge(UrlGoogleSheets_month(month=callback.data))
    await session.commit()
    # передаем в стейт месяц и меняем его состояние
    await state.update_data(month=callback.data)
    await state.set_state(SaveUrlTable.load_url)


@router.message(StateFilter(SaveUrlTable.load_url))
async def save_url(message: Message, user: str, state: FSMContext, session: AsyncSession):
    """ Сохранение ссылки """
    user_data: Dict[str, str] = await state.get_data()
    months: Dict[str, str] = months_dict
    month: str = user_data['month']     # 01-31
    # Проверка ссылки
    file = await save_google_sheet_locally(google_sheets_url=message.text, session=session)
    if file:
        log.warning(f'user save url: [{message.text}]')
        await message.answer(f'🏡 Таблица за {months[user_data["month"]]} сохранена.\n'
                             f'Чтобы узнать состав смены, отправьте <i>число.месяц</i>\n'
                             f'<code>Пример</code>: <i>31.12</i>')
        await session.merge(UrlGoogleSheets_month(month=month, url_google_sheets=message.text, path_file=None))
        await session.commit()
        await state.clear()
    else:
        await message.answer('🚧 По этой ссылке невозможно загрузить таблицу.\n'
                             'Ссылка должна иметь вид:\n'
                             '<b>https://docs.google.com/spreadsheets/d/1O8Zssdfsdf453454jkl5j34/edit#gid=0</b>\n'
                             'Где <code>1O8Zssdfsdf453454jkl5j34</code> - идентификатор вашей таблицы\n'
                             'А все остальное должно быть как в примере выше.',
                             reply_markup=keyboard_cancel())

@router.callback_query(~StateFilter(None), F.data == 'cancel')
async def cancel(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Выход из любого стейта """
    log.warning(f'user cancel state {await state.get_state()}')
    user_data: Dict[str, str] = await state.get_data()
    months: Dict[str, str] = months_dict
    month: str = user_data['month']  # 01-31
    await state.clear()
    text = callback.message.text
    await callback.message.edit_text(text)
    await callback.message.answer('🔘 Вы отменили сценарий')
    await delete_table(user=user, session=session, current_month=month)



# Сохранение файла таблицы
class SaveFileTable(StatesGroup):
    """ Загрузка файлов таблицы """
    get_month = State()
    load_url = State()

@router.callback_query(F.data == 'save_file', StateFilter(None))
async def choose_save_file(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Выбор месяца"""
    log.warning(f'user clicked [choose_save_file]')
    await callback.answer()
    await callback.message.edit_text('🏗 Выберете месяц, за который хотите прикрепить график\n', reply_markup=keyboard_months())
    #ставим стейт выбор месяца
    await state.set_state(SaveFileTable.get_month)

@router.callback_query(StateFilter(SaveFileTable.get_month), F.data == 'yes')
async def save_month(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Замена ссылки на локальный файл """
    log.warning(f'user replace url to file')
    await callback.answer()
    months: Dict[str, str] = months_dict
    user_data: Dict[str, str] = await state.get_data()
    month = user_data['month']
    await session.merge(UrlGoogleSheets_month(month=month))
    await session.commit()
    # передаем в стейт месяц и меняем его состояние
    await state.set_state(SaveFileTable.load_url)
    await callback.message.edit_text(f'👷🏻‍♂️ Отлично, выбран <code>{months[month]}</code>\n'
                                     f'⛓ Теперь отправьте Exel файл с графиком.\n'
                                     f'(Расширение должно быть .xlsx)')


@router.callback_query(StateFilter(SaveFileTable.get_month))
async def choose_month(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Запись в бд месяца """
    log.warning(f'user choose for save_url [{callback.data.split()[0]} month]')
    await callback.answer()
    months: Dict[str, str] = months_dict
    # обновление информации за указанный месяц
    await state.update_data(month=callback.data)
    query = await session.execute(select(UrlGoogleSheets_month).filter_by(month=callback.data))
    row = query.scalar()
    if row:
        return await callback.message.answer(
            f'За месяц <code>{months[callback.data]}</code> уже прикреплена ссылка на Google Sheets. '
            f'Желаете заменить ее на файл?',
            reply_markup=kb_yes_no()
        )
    else:
        await session.merge(UrlGoogleSheets_month(month=callback.data))
        await session.commit()
        # передаем в стейт месяц и меняем его состояние
        await state.set_state(SaveFileTable.load_url)
        await callback.message.edit_text(f'👷🏻‍♂️ Отлично, выбран <code>{months[callback.data]}</code>\n'
                                         f'⛓ Теперь отправьте Exel файл с графиком.\n'
                                         f'(Расширение должно быть .xlsx)')


@router.message(StateFilter(SaveFileTable.load_url), F.document)
async def save_file(message: Message, user: str, state: FSMContext, session: AsyncSession):
    """ Сохранение файла """
    user_data: Dict[str, str] = await state.get_data()
    months: Dict[str, str] = months_dict
    month: str = user_data['month']     # 01-31

    path = os.path.join(os.path.abspath('files'), f'{month}_month.xlsx')
    file = await message.bot.download(message.document, destination=path)
    await session.merge(UrlGoogleSheets_month(month=month, url_google_sheets=None, path_file=path))
    await session.commit()
    await state.clear()
    await message.answer(f'🏡 Таблица за {months[user_data["month"]]} сохранена.\n'
                         f'Чтобы узнать состав смены, отправьте <i>число.месяц</i>\n'
                         f'<code>Пример</code>: <i>31.12</i>')
    log.warning(f'user save file: [{path}]')






# Удаление ссылки
class DeleteTable(StatesGroup):
    """ Удалить таблицу за выбранный месяц """
    waite_month = State()

@router.callback_query(F.data == 'del_table')
async def choose_month(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Выбор месяца для удаления таблицы """
    log.warning(f'user [{user}] start state DeleteTable')
    await callback.answer()
    await state.set_state(DeleteTable.waite_month)
    # актуальные месяцы
    tables: List[Tuple[str, str]] = await get_all_table(session=session)
    months_list: List[str] = [row[0] for row in tables]     # ['01','02'..]
    await callback.message.edit_text(
        '👷🏻‍♂️ За какой месяц удалить таблицу?',
        reply_markup=keyboard_months(current_months=months_list))

@router.callback_query(StateFilter(DeleteTable.waite_month))
async def del_month(callback: CallbackQuery, user: str, state: FSMContext, session: AsyncSession):
    """ Удаление таблицы """
    await callback.answer()
    months: Dict[str, str] = months_dict
    current_month: str = callback.data  # 01-31
    alias_month = months[current_month]
    if await delete_table(user=user, session=session, current_month=current_month):
        await callback.message.edit_text(f'🗑 Таблица за {alias_month} успешно удалена из памяти')
        log.warning(f'user [{user}] successfully delete table [{current_month} month]')
    else:
        await callback.message.edit_text(f'🚧 Не удалось удалить данные за {alias_month}. '
                                         f'Просто загрузите новую таблицу, через главное меню, если хотите поменять '
                                         f'данные.')
        log.warning(f'user [{user}] unable delete table [{current_month} month]')
    await state.clear()



