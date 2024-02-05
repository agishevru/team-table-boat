""" Телеграм бот для обработки обработки таблиц рабочих графиков в форматах .xlsx и google sheets online """

import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from log_settings import log
from handlers import handlers_common, inline_collback, handlers_actual_users, fsm_handlers
from middlewares import middlerware_db
from models.db import Base
from ui_commands import set_ui_commands

async def main():
    log.warning('start bot')

    # Хранилище для Fsm: редис или оперативная память
    if config.fsm_memory_redis is True:
        try:
            redis = Redis(host='localhost', port=6379, db=1)
            await redis.ping()
            storage = RedisStorage(redis=redis)
        except Exception as exc:
            log.critical(exc)
            log.critical('MemoryStorage is selected for FSM')
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()


    # Асинхронная Алхимия
    engine = create_async_engine(url=config.db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # Бот
    bot = Bot(config.bot_token, parse_mode='html')
    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(middlerware_db.DbSessionMiddleware(sessionmaker))    # мидлварь передающая сессию Алхимии

    dp.include_router(handlers_common.router)
    dp.include_router(handlers_actual_users.router)
    dp.include_router(inline_collback.router)
    dp.include_router(fsm_handlers.router)

    # Отобразить меню команд
    await set_ui_commands(bot)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

