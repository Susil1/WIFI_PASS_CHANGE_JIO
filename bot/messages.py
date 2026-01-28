from datetime import datetime

from aiogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton,CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
import asyncio

from router.connection import routerConnection
from .utility import BOT_LOGGER

def delete_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, delete", callback_data="confirm_delete"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_delete")
        ]
    ])
async def send_help(message: Message,ADMIN_URL):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Admin Page", url=ADMIN_URL)]
            ]
    )

    await message.answer(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=kb
    )
async def change_pass_handler(message: Message,connection:routerConnection):
    msg = message.text
    args = msg.split() if msg else []
    if not (1 < len(args) < 3):
        await message.answer(pass_change_msg,parse_mode=ParseMode.HTML)
        return
    *_,password = args
    if message.from_user:
        BOT_LOGGER.log(f"Changing wifi password user_id={message.from_user.id}")
    status = await asyncio.to_thread(connection.changePassword, password)
    if (status == "OK"):
        BOT_LOGGER.log("Wifi password changed successfully")
        await message.answer(
            "✅ <b>Password Changed Successfully!</b>",
            parse_mode=ParseMode.HTML
        )
    else:
        BOT_LOGGER.log(f"Wifi password change failed status={status}", err=True)
        await message.answer(
            wrong_password_msg,
            parse_mode=ParseMode.HTML
        )
        
async def lan_clients_handler(message:Message,time_str,results):
    kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬇ Show Details", callback_data="more")]
            ]
        )
    msg = ("<b>📡 Scan Results:</b>\n\n"
           f"<b>Scan Time:</b>\n{time_str}\n\n"
           "<pre>")
    for res in results:
        msg += ( f"Host Name : {res['hostName']}\n"
            f"IPv4      : {res['ipv4Address']}\n"
                "----------------------------\n")
    msg += "</pre>"
    await message.answer(
        msg,
        parse_mode=ParseMode.HTML,
        reply_markup=kb
        )
    
async def show_less(callback: CallbackQuery,state:FSMContext):
    if not isinstance(callback.message,Message):
        return
    kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬇ Show Details", callback_data="more")]
            ]
        )
    results = await state.get_data()
    if (not results):
        kb=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Rescan", callback_data="rescan")]
            ]
        )
        time_str = datetime.now().strftime("🕒 %r\n📅 %d-%b-%G (%A)")
        msg = (
            "📡 <b>Scan Results</b>\n\n"
            "<b>Scan Time:</b>\n"
            f"{time_str}\n\n"
            "📭 <b>No devices found</b>\n"
            "🔄 Tap below to scan again"
            )
        await callback.message.edit_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
        await callback.answer()
        return
    
    results_list = results.get("lan_results",[])
    time_str = results.get("time_str","time")
    msg = ("<b>📡 Scan Results:</b>\n\n"
           f"<b>Scan Time:</b>\n{time_str}\n\n"
           "<pre>")
    for res in results_list:
        msg += ( f"Host Name : {res['hostName']}\n"
            f"IPv4      : {res['ipv4Address']}\n"
                "----------------------------\n")
    msg += "</pre>"
    
    await callback.message.edit_text(
        msg,
        parse_mode=ParseMode.HTML,
        reply_markup=kb
    )
    await callback.answer()
async def show_more(callback: CallbackQuery,state:FSMContext):
    if not isinstance(callback.message,Message):
        return
    kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬆ Hide Details", callback_data="less")]
            ]
        )
    results = await state.get_data()
    if (not results):
        kb=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Rescan", callback_data="rescan")]
            ]
        )
        time_str = datetime.now().strftime("🕒 %r\n📅 %d-%b-%G (%A)")
        msg = (
            "📡 <b>Scan Results</b>\n\n"
            "<b>Scan Time:</b>\n"
            f"{time_str}\n\n"
            "📭 <b>No devices found</b>\n"
            "🔄 Tap below to scan again"
            )
        await callback.message.edit_text(
            msg,
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
        await callback.answer()
        return 
    results_list = results.get("lan_results",[])
    time_str = results.get("time_str","time")
    msg = ("<b>📡 Scan Results:</b>\n\n"
           f"<b>Scan Time:</b>\n{time_str}\n\n"
           "<pre>")
    for res in results_list:
        msg += ( f"Host Name : {res['hostName']}\n"
            f"IPv4      : {res['ipv4Address']}\n"
            f"IPv6      : {res['ipv6Address']}\n"
            f"MAC       : {res['macAddress']}\n"
                "----------------------------\n")
    msg += "</pre>"
    await callback.message.edit_text(
    msg,
    parse_mode=ParseMode.HTML,
    reply_markup=kb
    )
    await callback.answer()

async def memory_usage_handler(message:Message,results):
    current_usage , free_usage = results["currentUsage"], results["free"]
    total_blocks = 20
    used_blocks = int((current_usage / 100) * total_blocks)
    free_blocks = total_blocks - used_blocks

    bar = "█" * used_blocks + "░" * free_blocks

    msg = (
        "💾 <b>Memory Usage</b>\n\n"
        f"<code>{bar}\n"
        "USED     FREE\n"
        "─────    ─────\n"
        f"{current_usage}%    {free_usage}%"
        "</code>"
        )
    await message.answer(msg,parse_mode=ParseMode.HTML)
async def wireless_config_handler(message:Message,results):
    max_clients = results["maxClients"]
    security = results["security"]
    ssid = results["ssid"]

    msg = (
        "<code>"
        "👥 MAX CLIENTS   🔐 SECURITY\n"
        " ────────────     ───────────\n"
        f"      {max_clients}           {security}\n\n"
        "📶 SSID\n"
        "─────\n"
        f"{ssid}"
        "</code>"
    )
    await message.answer(msg,parse_mode=ParseMode.HTML)
async def system_status_handler(message:Message,results):
    firmware = results["firmwareVersion"]
    hardware = results["hardwareVersion"]
    model = results["modelName"]
    connected = results["numberOfConnectedDevices"]
    serial = results["serialNumber"]
    ssid_24 = results["ssid24Ghz"]
    ssid_5 = results["ssid5Ghz"]
    system_name = results["systemName"]
    voip = results["voipStatus"]
    wireless_24 = results["wireless24Ghz"]
    wireless_5 = results["wireless5Ghz"]


    msg = (
        "<code>"
        "⚙️ SYSTEM STATUS\n"
        "──────────────\n"
        f"🧩 FIRMWARE   : {firmware}\n"
        f"🛠 HARDWARE   : {hardware}\n"
        f"📦 MODEL      : {model}\n"
        f"👥 CONNECTED  : {connected}\n"
        f"🔢 SERIAL     : {serial}\n"
        "─────────────────────\n"
        f"📶 SSID 2.4G  : {ssid_24}\n"
        f"📶 SSID 5G    : {ssid_5}\n"
        "─────────────────────\n"
        f"🖥 SYSTEM     : {system_name}\n"
        "─────────────────────\n"
        f"📞 VOIP       : {'ON' if voip else 'OFF'}\n"
        f"📡 2.4G WIFI  : {'ON' if wireless_24 else 'OFF'}\n"
        f"📡 5G WIFI    : {'ON' if wireless_5 else 'OFF'}"
        "</code>"
    )


    await message.answer(msg,parse_mode=ParseMode.HTML)

help_text = (
    "╭━━━━━━━━━━━━━━━━━━━━╮\n"
    "📡 <b>ROUTER CONTROL BOT</b>\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"

    "⚙️ <b>Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"

    "🔑 <code>/change_pass newpass</code>\n"
    "└─ Change router password\n\n"

    "👥 <b>/get_lan_clients</b>\n"
    "└─ Show connected LAN clients\n\n"

    "💾 <b>/get_memory_usage</b>\n"
    "└─ Show memory usage status\n\n"

    "📡 <b>/get_wireless_config</b>\n"
    "└─ Show wireless configuration\n\n"

    "🖥 <b>/get_system_status</b>\n"
    "└─ Show router system status\n\n"

    "👤 <b>/get_user_profile</b>\n"
    "└─ Show your authorised user profile\n\n"

    "🗑 <b>/delete_profile</b>\n"
    "└─ Delete your authorised user account\n\n"

    "📖 <b>/help</b>\n"
    "└─ Show this help menu\n\n"

    "━━━━━━━━━━━━━━━━━━━━\n"
    "🔐 <b>Authorisation Required</b>\n"
    "└─ Use <code>/authorise &lt;your_code&gt;</code> to access commands\n\n"

    "⚠️ <i>Use commands carefully</i>"
)


pass_change_msg = (
            "⚠️ <b>Incorrect command usage!</b>\n\n"
            "✅ <b>Correct format:</b>\n"
            "<code>/change_pass your_password</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/change_pass 12345</code>"
        )

wrong_password_msg = (
    "❌ <b>Password Change Failed!</b>\n\n"
    "⚠️ The provided password is invalid or the operation could not be completed.\n"
    "🔁 Please try again using the correct format:\n"
    "<code>/change_pass your_password</code>"
)
wrong_auth_msg = (
    "❌ <b>Wrong usage!</b>\n\n"
    "Correct format:\n"
    "<code>/authorise &lt;YOUR_KEY&gt;</code>\n\n"
    "Example:\n"
    "<code>/authorise ABCD-1234-KEY</code>"
)
admin_msg = (
    "⚠️ <b>Access already granted.</b>\n\n"
    "Your account already has admin privileges.\n"
    "This action is not required."
)
user_profile_msg = (
        "━━━━━━━━━━━━━━\n"
        "👤 <b>USER PROFILE</b>\n"
        "━━━━━━━━━━━━━━\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "🔤 Username: @{username}\n"
        "📛 Name: {first_name}\n"
        "🗓 Joined: {joined_date}\n\n"
        "📊 <b>ACCOUNT</b>\n"
        "🎭 Role: {role}\n"
        "📅 Expiry: {expiry_date}\n"
        "⚙️ Commands Left: {commands_remaining}\n"
        "━━━━━━━━━━━━━━"
    )
access_denied_msg = (
    "🚫 <b>Access denied!</b>\n\n"
    "No user profile was found for your account.\n\n"
    "To get access, please authorise first:\n"
    "<code>/authorise &lt;YOUR_CODE&gt;</code>"
)

delete_confirm_msg = (
    "🗑 <b>Your account has been deleted successfully.</b>\n\n"
    "<i>You can re-authorise anytime using:</i>\n"
    "<code>/authorise &lt;your_code&gt;</code>"
)
wrong_code_msg = (
    "❌ <b>Wrong code!</b>\n\n"
    "The authorisation code you entered is invalid.\n"
    "Please try again."
)