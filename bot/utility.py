import asyncio
from datetime import datetime
from typing import Callable, Awaitable

from utils.constants import DATE_FMT

from router.connection import routerConnection
from router.file_handler import getLoginData

from db.connection import DB_Connection

LOGIN_DATA = getLoginData()
CONNECTION = routerConnection(LOGIN_DATA,console_log=False)
DB:DB_Connection = DB_Connection()

async def periodic_task(
    func: Callable[[], Awaitable[None]],
    interval: float,*args
):
    """
    Runs `func` every `interval` seconds in parallel (async).
    """
    while True:
        try:
            await func(*args)
        except Exception as e:
            print("Error", e)
        await asyncio.sleep(interval)
        
async def reconnect(router_connection:routerConnection):
    router_connection.reconnect()
    
def getFormattedExpiryDate(date:str):
    dateObj:datetime = datetime.strptime(date,DATE_FMT)
    date = dateObj.strftime("%Y-%m-%d %I:%M:%S %p")
    if datetime.now() > dateObj :
        return f"<s>{date}</s>"
    return date