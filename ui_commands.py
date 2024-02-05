""" Регистрация команд для кнопки меню """
from aiogram import Bot
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand


async def set_ui_commands(bot: Bot):
    """
    Устанавливает команды бота в пользовательском интерфейсе
    :param bot: Экземпляр бота
    """
    commands = [
        BotCommand(command="menu", description="Кнопочное меню"),
    ]
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats()
    )
