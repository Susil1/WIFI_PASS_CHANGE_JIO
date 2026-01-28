from aiogram.types import Message
from datetime import datetime,timedelta

from utils.utility import UserData,UserInfo,Command
from utils.constants import DATE_FMT
from .connection import DB_Connection

def is_valid_date(date_str: str|None) -> bool:
    from datetime import datetime
    if date_str is None:
        return False
    try:
        datetime.strptime(date_str, DATE_FMT)
        return True
    except ValueError:
        return False

def authorise(key: str, message: Message, DB: DB_Connection) -> UserInfo:
    from_user = message.from_user
    now = datetime.now()

    # Default unauthorised response
    default_info = UserInfo(user_id=0)

    if not from_user:
        return default_info

    data = DB.get_auth_data(key)
    if not data:
        DB.add_failed_attempts(user_id=from_user.id)
        return default_info

    user_id = from_user.id
    username = from_user.username or ""
    first_name = from_user.first_name or ""

    role = data.get("role", "")
    expiry_date = data.get("expiry_date")
    num_of_commands = data.get("num_of_commands", 0)
    days = data.get("days", 0)
    time_data = data.get("time") or {"hours": 0, "minutes": 0, "seconds": 0}

    last_used = now.strftime(DATE_FMT)

    cmd_data = DB.get_command_data(user_id=user_id)
    prev_user_data = DB.get_user_data(user_id=user_id)

    # Add remaining commands if exists
    if cmd_data:
        num_of_commands += cmd_data.get("commands_remaining", 0)

    # Normalize expiry_date
    if not is_valid_date(expiry_date):
        expiry_date = ""

    # If new expiry exists, keep the later one
    if expiry_date and cmd_data:
        old_expiry = cmd_data.get("expiry_date")
        if is_valid_date(old_expiry):
            if datetime.strptime(old_expiry, DATE_FMT) > datetime.strptime(expiry_date, DATE_FMT):
                expiry_date = old_expiry

    # Generate expiry if missing and not admin
    if not expiry_date and role != "admin":
        prev_expiry = cmd_data.get("expiry_date") if cmd_data else ""

        base_time = (
            datetime.strptime(prev_expiry, DATE_FMT)
            if is_valid_date(prev_expiry)
            else now
        )

        base_time = max(base_time, now)

        delta_kwargs = {"days": days, **time_data}
        expiry_date_obj = base_time + timedelta(**delta_kwargs)
        expiry_date = expiry_date_obj.strftime(DATE_FMT) if expiry_date_obj != now else ""

    joined_date = now.strftime("%d %b %Y, %I:%M:%S %p (%a)")
    if (prev_user_data):
        prev_joined_date = prev_user_data.get("joined_date") or joined_date
        try:
            joined_date = (min(now,datetime.strptime(prev_joined_date,"%d %b %Y, %I:%M:%S %p (%a)"))).strftime("%d %b %Y, %I:%M:%S %p (%a)")
        except ValueError:
            pass
    user_data = UserData(
        user_id=user_id,
        username=username,
        role=role,
        first_name=first_name,
        joined_date=joined_date
    )

    info = UserInfo(
        user_id=user_id,
        username=username,
        first_name=first_name,
        role=role,
        expiry_date=expiry_date,
        commands_remaining=num_of_commands,
        joined_date=joined_date,
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