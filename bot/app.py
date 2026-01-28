import asyncio

from aiogram import Bot, Dispatcher,F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from router.file_handler import config

from db.utility import authorise

from utils.utility import UserInfo

from .file_handler import getToken
from .utility import periodic_task,getFormattedExpiryDate,reconnect,CONNECTION,DB
from .messages import (send_help,
                       delete_confirm_kb,
                       wrong_auth_msg,
                       admin_msg,user_profile_msg,
                       access_denied_msg,
                       delete_confirm_msg,
                       wrong_code_msg
                    )
from .handler.commands import command_route

RECONNECT_INTERVAL_SECONDS = 15 * 60
IP_ADDRESS = config["IP"]["ip"]
ADMIN_URL = f"https://{IP_ADDRESS}/"

CONNECTION.initialise_connection()
TOKEN = getToken()

def getUserInfo(user_id:int)->UserInfo:
    data = DB.get_user_data(user_id)
    if not data:
        return UserInfo(user_id=user_id)
    username = data.get("username","")
    first_name = data.get("first_name","")
    role = data.get("role","")
    expiry_date = data.get("expiry_date","")
    commands_remaining = data.get("commands_remaining",0)
    joined_date = data.get("joined_date","")
    info = UserInfo(
        user_id=user_id,
        username=username,
        first_name=first_name,
        role=role,
        expiry_date=expiry_date,
        commands_remaining=commands_remaining,
        joined_date=joined_date,
        status=True
    )
    return info
dp = Dispatcher()
dp.include_router(command_route)

@dp.message(Command("authorise"))
async def authorise_user(message: Message):
    msg = message.text.split(maxsplit=1) if message.text else []
    if(not len(msg) == 2):
        await message.answer(
            wrong_auth_msg,
            parse_mode=ParseMode.HTML
        )
        return
    key:str = msg[1]
    user_id = message.from_user.id if message.from_user else 0
    if DB.check_admin(user_id):
        await message.answer(
            admin_msg,
            parse_mode=ParseMode.HTML
        )
        return
    if DB.failed_attempts(user_id) >= 5:
        await message.answer("⛔ Too many attempts. Try later.")
        return
    
    user_info = authorise(key,message,DB)
    if user_info.status:
        await message.answer(
            "🎉 <b>Success!</b>\n\n"
            "Your authorisation code is valid.\n",
            parse_mode=ParseMode.HTML
        )
        username = user_info.username or "N/A"
        first_name = user_info.first_name or "N/A"
        role = user_info.role or "N/A"
        expiry_date = user_info.expiry_date or "N/A"
        commands_remaining = user_info.commands_remaining or "N/A"
        joined_date = user_info.joined_date or "N/A"
        if user_info.expiry_date:
            expiry_date = getFormattedExpiryDate(expiry_date)
        
        text = user_profile_msg.format(
            user_id,
            username,
            first_name,
            joined_date,
            role,
            expiry_date,
            commands_remaining
        )
        await message.answer(text,parse_mode=ParseMode.HTML)
        return
    await message.answer(
        wrong_code_msg,
        parse_mode=ParseMode.HTML
    )
@dp.message(Command("get_user_profile"))
async def get_user_profile(message: Message):
    if not message.from_user:
        return
    user_info:UserInfo = getUserInfo(message.from_user.id)
    if user_info.status:
        user_id = user_info.user_id
        username = user_info.username or "N/A"
        first_name = user_info.first_name or "N/A"
        role = user_info.role or "N/A"
        expiry_date = user_info.expiry_date or "N/A"
        commands_remaining = user_info.commands_remaining or "N/A"
        joined_date = user_info.joined_date or "N/A"

        if user_info.expiry_date:
            expiry_date = getFormattedExpiryDate(expiry_date)
            
        text = user_profile_msg.format(
            user_id,
            username,
            first_name,
            joined_date,
            role,
            expiry_date,
            commands_remaining
            )

        await message.answer(text,parse_mode=ParseMode.HTML)
        return
    await message.answer(
            access_denied_msg,
            parse_mode=ParseMode.HTML
        )

@dp.message(Command("delete_profile"))
async def delete_profile(message: Message):
    if not message.from_user:
        return
    if (not DB.get_user_data(message.from_user.id)):
        await message.answer(
            access_denied_msg,
            parse_mode=ParseMode.HTML
        )
        return
    sent = await message.answer(
        "⚠️ <b>Are you sure you want to delete your account?</b>\n\n"
        "This action is <b>irreversible</b>.",
        reply_markup=delete_confirm_kb(),
        parse_mode=ParseMode.HTML
    )
    await asyncio.sleep(30)
    
    try:
        await sent.edit_reply_markup(reply_markup=None)
        await sent.edit_text(
        "<i>No action was taken within 30 seconds.</i>",
        parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        # Buttons already gone or message already edited
        pass
@dp.callback_query(F.data == "confirm_delete")
async def confirm_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not DB.get_user_data(user_id):
        await callback.answer("Not authorised", show_alert=True)
        return

    if DB.delete_user(user_id):
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                delete_confirm_msg,
                parse_mode=ParseMode.HTML
            )

        await callback.answer(
            "✅ Account deleted successfully",
            show_alert=True
        )
    else:
        await callback.answer(
            "❌ Deletion failed.\nUser not found in database.",
            show_alert=True
        )
@dp.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    if not DB.get_user_data(callback.from_user.id):
        await callback.answer("Not authorised", show_alert=True)
        return
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "❌ <b>Account deletion cancelled.</b>",
            parse_mode=ParseMode.HTML
        )

    await callback.answer("Cancelled")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await send_help(message,ADMIN_URL)
    
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await send_help(message,ADMIN_URL)


async def main():
    reconnect_task = asyncio.create_task(periodic_task(lambda: reconnect(CONNECTION), RECONNECT_INTERVAL_SECONDS))
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        print("🤖 Bot started. Press Ctrl+C to stop.")
        await dp.start_polling(bot)

    except asyncio.CancelledError:
        # NORMAL shutdown signal from asyncio
        pass

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (Ctrl+C)")

    except Exception as e:
        print("❌ Unexpected error:", e)

    finally:
        CONNECTION.logout()
        reconnect_task.cancel()
        print("🔻 Closing bot session...")
        await bot.session.close()
        print("✅ Bot shutdown complete.")
