""" Внешняя (outter) мидлварь, передающая данные пользователя в удобном виде в дате. """
from sqlalchemy.ext.asyncio import async_sessionmaker

from log_settings import log
from typing import Any, Callable, Dict, Awaitable
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject



class DbSessionMiddleware(BaseMiddleware):
    """ Передает db сессию в хэндлер """
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # удобный идентефикатор юзера
        user = f'{data["event_from_user"].id} {data["event_from_user"].username}'
        data["user"] = user  # занести в дату новый ключ
        log.debug(f'outer - {datetime.now()}')  # таймкод

        # объект сессии бд
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)

