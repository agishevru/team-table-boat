""" Модуль на отслеживание событий добавленияия и удаления бота пользователем. Актуализирует состояние активных
подписчиков в бд Users. """

from aiogram import F, Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from sqlalchemy.ext.asyncio import AsyncSession

from log_settings import log
from models.models_utils import get_or_create_user, delete_user

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, user: str, session: AsyncSession):
    """ Удаляет пользователя из бд """
    log.warning(f'user BLOCKED bot')
    await delete_user(event, session)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, user: str, session: AsyncSession):
    """ Добавляет пользователя в бд """
    log.warning(f'user UNBLOCKED bot')
    await get_or_create_user(event, session)










