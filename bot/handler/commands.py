from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.context import FSMContext

import asyncio

from datetime import datetime

from ..middleware.auth import AuthMiddleware

from ..messages import (change_pass_handler,
                        lan_clients_handler,
                        show_more,show_less,
                        memory_usage_handler,
                        wireless_config_handler,
                        system_status_handler
                    )
from ..utility import CONNECTION
from ..utility import BOT_LOGGER

command_route = Router()
command_route.message.middleware(AuthMiddleware())
command_route.callback_query.middleware(AuthMiddleware())

@command_route.message(Command("change_pass"))
async def pass_change(message: Message):
    if message.from_user:
        BOT_LOGGER.log(f"/change_pass user_id={message.from_user.id} name={message.from_user.first_name}")
    await change_pass_handler(message,CONNECTION)


@command_route.message(Command("get_lan_clients"))
async def lan_clients(message: Message,state:FSMContext):
    if message.from_user:
        BOT_LOGGER.log(f"/get_lan_clients user_id={message.from_user.id} name={message.from_user.first_name}")
    response = await asyncio.to_thread(CONNECTION.getInfo, "getLanClients")
    results:list = response.results
    time_str = datetime.now().strftime("🕒 %r\n📅 %d-%b-%G (%A)")
    await state.update_data(lan_results=results)
    await state.update_data(time_str=time_str)
    await lan_clients_handler(message,time_str,results)
    
@command_route.callback_query(F.data == "less")
async def hide_details(callback: CallbackQuery,state:FSMContext):
    await show_less(callback,state)

@command_route.callback_query(F.data == "more")
async def show_more_details(callback: CallbackQuery,state:FSMContext):
    await show_more(callback,state)
    
@command_route.callback_query(F.data == "rescan")
async def rescan(callback: CallbackQuery,state:FSMContext):
    BOT_LOGGER.log(f"rescan lan clients user_id={callback.from_user.id} name={callback.from_user.first_name}")
    response = await asyncio.to_thread(CONNECTION.getInfo, "getLanClients")
    results:list = response.results
    time_str = datetime.now().strftime("🕒 %r\n📅 %d-%b-%G (%A)")
    await state.update_data(lan_results=results)
    await state.update_data(time_str=time_str)
    if (not isinstance(callback.message,Message)):
        return
    await lan_clients_handler(callback.message,time_str,results)
    await callback.answer()
    
@command_route.message(Command("get_memory_usage"))
async def memory_usage(message: Message):
    if message.from_user:
        BOT_LOGGER.log(f"/get_memory_usage user_id={message.from_user.id} name={message.from_user.first_name}")
    response = await asyncio.to_thread(CONNECTION.getInfo, "getMemoryUtilisation")
    results = response.results
    await memory_usage_handler(message,results)
    
@command_route.message(Command("get_wireless_config"))
async def wireless_config(message: Message):
    if message.from_user:
        BOT_LOGGER.log(f"/get_wireless_config user_id={message.from_user.id} name={message.from_user.first_name}")
    response = await asyncio.to_thread(CONNECTION.getInfo, "getWirelessConfiguration")
    results = response.results
    await wireless_config_handler(message,results)
    
    
@command_route.message(Command("get_system_status"))
async def system_status(message: Message):
    if message.from_user:
        BOT_LOGGER.log(f"/get_system_status user_id={message.from_user.id} name={message.from_user.first_name}")
    response = await asyncio.to_thread(CONNECTION.getInfo, "getSystemStatus")
    results = response.results
    await system_status_handler(message,results)