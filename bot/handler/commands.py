from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.context import FSMContext

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

command_route = Router()
command_route.message.middleware(AuthMiddleware())
command_route.callback_query.middleware(AuthMiddleware())

@command_route.message(Command("change_pass"))
async def pass_change(message: Message):
    await change_pass_handler(message,CONNECTION)


@command_route.message(Command("get_lan_clients"))
async def lan_clients(message: Message,state:FSMContext):
    results:list = CONNECTION.getInfo("getLanClients").results
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
    results:list = CONNECTION.getInfo("getLanClients").results
    time_str = datetime.now().strftime("🕒 %r\n📅 %d-%b-%G (%A)")
    await state.update_data(lan_results=results)
    await state.update_data(time_str=time_str)
    if (not isinstance(callback.message,Message)):
        return
    await lan_clients_handler(callback.message,time_str,results)
    await callback.answer()
    
@command_route.message(Command("get_memory_usage"))
async def memory_usage(message: Message):
    results = CONNECTION.getInfo("getMemoryUtilisation").results
    await memory_usage_handler(message,results)
    
@command_route.message(Command("get_wireless_config"))
async def wireless_config(message: Message):
    results = CONNECTION.getInfo("getWirelessConfiguration").results
    await wireless_config_handler(message,results)
    
    
@command_route.message(Command("get_system_status"))
async def system_status(message: Message):
    results = CONNECTION.getInfo("getSystemStatus").results
    await system_status_handler(message,results)