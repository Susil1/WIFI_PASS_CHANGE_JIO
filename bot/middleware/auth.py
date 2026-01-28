from collections.abc import Awaitable, Callable
from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.enums import ParseMode

from ..utility import DB

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject,dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            if (event.from_user and DB.isAuthorised(event.from_user.id)):
                return await handler(event, data)
            await event.answer(
                        "⛔ <b>Access denied!</b>\n\n"
                        "You are not authorised to use this feature.\n\n"
                        "To get access, please authorise first:\n"
                        "<code>/authorise &lt;YOUR_CODE&gt;</code>",
                        parse_mode=ParseMode.HTML
                    )
        