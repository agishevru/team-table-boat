""" Утилиты для быстрой работы моделями """


from datetime import datetime
from typing import Union, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aiogram.types import Message, ChatMemberUpdated

from log_settings import log
from models.db import Users, UrlGoogleSheets_month


async def get_or_create_user(message: Union[Message, ChatMemberUpdated], session: AsyncSession):
    """ Идентефицирует пользователя в бд / заводит запись о нем """
    db_query = await session.execute(select(Users).filter_by(user_id=message.from_user.id))
    user_by_id = db_query.scalar()
    if user_by_id:
        return user_by_id
    else:
        new_user_by_id = Users(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            time=datetime.now().strftime('%d.%m.%y %H:%M')
        )
        session.add(new_user_by_id)
        await session.commit()
        log.critical(f'New user in db {new_user_by_id.user_id} {new_user_by_id.username}')
        return new_user_by_id


async def delete_user(message: Union[Message, ChatMemberUpdated], session: AsyncSession) -> bool:
    """ Удаление пользователя. Выявляет айди по переданному типу обновлению. """
    db_query = await session.execute(select(Users).filter_by(user_id=message.from_user.id))
    user_by_id = db_query.scalar()
    if user_by_id:
        await session.delete(user_by_id)
        await session.commit()
        log.critical(f'User [{user_by_id.user_id} {user_by_id.username}] DELETED from db bot')
        return True
    return False

async def get_all_table(session: AsyncSession) -> Union[List[Tuple[str, str]], bool]:
    """ Сбор всех прикрепленных таблиц. Возвращает список кортежей [(месяц, ссылка/путь), ..] """
    db_query = await session.execute(select(UrlGoogleSheets_month))
    tables = db_query.scalars()
    if tables:
        date: List[Tuple[str, str]] = []
        for table in tables:
            if table.url_google_sheets:
                date.append((table.month, table.url_google_sheets))
            elif table.path_file:
                date.append((table.month, table.path_file))
        return date
    else:
        return False

async def delete_table(user: str, session: AsyncSession, current_month: str) -> bool:
    """ Удаление таблицы за выбранный месяц.
     :param current_month: строка(номер_месяца) """
    db_query = await session.execute(select(UrlGoogleSheets_month).filter_by(month=current_month))
    row_table = db_query.scalar()
    if row_table:
        await session.delete(row_table)
        await session.commit()
        log.critical(f'User [{user}] DELETED table - [{current_month} month]')
        return True
    return False
