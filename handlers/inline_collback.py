""" Общие, не стейтовые инлайн ответы """


from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from handlers import handlers_common
from utils.all import months_dict

router = Router()


@router.callback_query(F.data.endswith('.xlsx'))
async def send_table(callback: CallbackQuery, user: str, session: AsyncSession):
    """ Отправляет локальный файл таблицы, переданный в callback.data пользователю """
    await callback.answer()
    months = months_dict
    table_from_local = FSInputFile(callback.data)
    result = await callback.message.answer_document(
        table_from_local,
        caption=f"таблица, подгруженная за {months[callback.data.split('.')[-2].split('_')[-2][-2:]]}"
    )


@router.callback_query(F.data.in_(['load', 'go', 'users', 'help', 'quit', 'look_table', 'example']))
async def get_comand(callback: CallbackQuery, user: str, session: AsyncSession):
    """ Ответы с главного меню '/menu', перенаправляет в команды """
    await callback.answer()
    data = callback.data
    if data == 'quit':
        return await callback.message.delete()
    func = getattr(handlers_common, f'cmd_{data}')
    return await func(message=callback.message, user=user, session=session, edit_message=True)

@router.callback_query(F.data == 'menu', StateFilter(None))
async def cmd_back(callback: CallbackQuery, user: str, session: AsyncSession):
    """ Кнопка назад -> вызывает главное меню """
    data = callback.data
    func = getattr(handlers_common, f'cmd_{data}')
    return await func(message=callback.message, user=user, session=session, edit_message=True)


