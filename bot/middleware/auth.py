from collections.abc import Awaitable, Callable
from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.enums import ParseMode

from ..utility import DB,BOT_LOGGER

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject,dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if event.from_user else 0
            if user_id and DB.isAuthorised(user_id):
                return await handler(event, data)

            BOT_LOGGER.log(f"Access denied user_id={user_id}")
            text = (
                "⛔ <b>Access denied!</b>\n\n"
                "You are not authorised to use this feature.\n\n"
                "To get access, please authorise first:\n"
                "<code>/authorise &lt;YOUR_CODE&gt;</code>"
            )

            if isinstance(event, Message):
                await event.answer(text, parse_mode=ParseMode.HTML)
                return

            if isinstance(event, CallbackQuery):
                if event.message:
                    await event.message.answer(text, parse_mode=ParseMode.HTML)
                await event.answer()
                return
        