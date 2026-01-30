from collections.abc import Awaitable, Callable
from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
import asyncio

from ..utility import DB

class UsedCommands(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject,dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        if isinstance(event, Message):
            if isinstance(event, Message):
                user_id = event.from_user.id if event.from_user else None   
                msg = event.text or ""
                command = msg.split()[0]
                if command and user_id:
                    await asyncio.to_thread(DB.update_used_commands, user_id, command)
        return await handler(event, data)