from aiogram.types import Message
from datetime import datetime,timedelta

from utils.utility import UserData,UserInfo,Command
from utils.constants import DATE_FMT
from .connection import DB_Connection

def is_valid_date(date_str: str) -> bool:
    from datetime import datetime
    try:
        datetime.strptime(date_str, DATE_FMT)
        return True
    except ValueError:
        return False

def authorise(key: str, message: Message, DB: DB_Connection) -> UserInfo:
    from_user = message.from_user
    data = DB.get_auth_data(key)

    # Default response
    info = UserInfo(user_id=0)

    if not data or not from_user:
        return info
    
    now = datetime.now()
    user_id = from_user.id
    username = from_user.username or ""
    first_name = from_user.first_name or ""

    role = data.get("role", "")
    expiry_date = data.get("expiry_date")
    num_of_commands = data.get("num_of_commands", 0)
    days = data.get("days", 0)
    time_data: dict = data.get("time", {"hours": 0, "minutes": 0, "seconds": 0})

    last_used = datetime.now().strftime(DATE_FMT)

    cmd_data = DB.get_command_data(user_id=user_id)
    num_of_commands += cmd_data.get("commands_remaining",0) if cmd_data else 0
    if not is_valid_date(expiry_date):
        expiry_date = ""
    # If expiry not pre-defined, extend previous or now
    if not expiry_date and role != "admin" and not num_of_commands:
        prev_expiry_str = cmd_data.get("expiry_date") if cmd_data else None
        base_time = (
            datetime.strptime(prev_expiry_str, DATE_FMT)
            if prev_expiry_str
            else now
        )
        base_time = base_time if base_time > now else now
        delta_kwargs = {**time_data, "days": days}
        expiry_date = (base_time + timedelta(**delta_kwargs)).strftime(DATE_FMT)
    user_data = UserData(
        user_id=user_id,
        username=username,
        role=role,
        first_name=first_name,
        joined_date=now.strftime("%d %b %Y, %I:%M %p (%a)")
    )

    info = UserInfo(
        user_id=user_id,
        username=username,
        first_name=first_name,
        role=role,
        expiry_date=expiry_date,
        commands_remaining=num_of_commands,
        joined_date=now.strftime("%d %b %Y, %I:%M %p (%a)"),
        status=True
    )

    command_data = Command(
        user_id=user_id,
        expiry_date=expiry_date,
        commands_remaining=num_of_commands,
        last_used=last_used
    )

    DB.add_user_data(user_data)
    DB.update_commands(command_data)

    return info