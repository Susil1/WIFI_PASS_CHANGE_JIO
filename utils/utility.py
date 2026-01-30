import secrets
import string
import logging
import os
from typing import Any
from pathlib import Path
from dataclasses import dataclass,field

from .colors import RESET,BLUE,GREEN,YELLOW,RED

def getNewPassword():
    myNames = ["susil","sumit","situ"]
    chars =  string.digits
    symbol = "!@#$%^&*_-"

    name = secrets.choice(myNames)
    nums = ''.join(secrets.choice(chars) for _ in range(secrets.randbelow(3) + 3))
    symbols = ''.join(secrets.choice(symbol) for _ in range(secrets.randbelow(3) + 2))

    password = name + nums + symbols

    return password

@dataclass
class Payload:
    method: str
    params: dict[str, str] = field(default_factory=dict)
    jsonrpc: str = "2.0"
    
    # Returns data for json type 
    def json(self)->dict:
        return {
            "jsonrpc":self.jsonrpc,
            "method":self.method,
            "params":self.params
        }
        
@dataclass
class Response:
    code:str
    message:str
    status:str
    results:Any
@dataclass
class UserData:
    user_id:int
    username:str
    first_name:str
    role:str
    joined_date:str
        
    def toDict(self):
        user_data:dict = {
            "user_id":self.user_id,
            "username":self.username,
            "first_name":self.first_name,
            "role":self.role,
            "joined_date":self.joined_date
        } 
        return user_data
@dataclass
class UserInfo:
    user_id:int
    username:str = ""
    first_name:str = ""
    role:str = ""
    expiry_date:str = ""
    commands_remaining:int = 0
    status:bool = False
    joined_date:str = ""
@dataclass
class Command:
    user_id:int
    expiry_date:str
    commands_remaining:int
    last_used:str
    used_commands:list = field(default_factory=list)

    def toDict(self):
        command_data:dict = {
            "user_id":self.user_id,
            "expiry_date":self.expiry_date,
            "commands_remaining":self.commands_remaining,
            "used_commands":self.used_commands,
            "last_used":self.last_used

        } 
        return command_data
def print_results(data:Any,tabs=1)->None:
    if (isinstance(data,list)):
        for res in data:
            if (isinstance(res,list) or isinstance(res,dict)):
                print_results(res)
            else:
                print("\t"*tabs,res)
            print("-"*60)
    elif (isinstance(data,dict)):
        items = sorted(data.items())
        for key,value in items:
            if (isinstance(value,list)):
                print_results(value)
            elif (isinstance(value,dict)):
                print_results(value,tabs=tabs+1)
            else:  
                print(f"{'\t'*tabs}{BLUE}{key}: {RESET}",value)
    else:
        print("\t"*tabs,data)

def print_response(data:Response)->None:
    results = data.results
    print(GREEN,"-"*80,RESET)
    print(f"{BLUE}Code: {RESET}{data.code}")
    print(f"{BLUE}Message: {YELLOW}{data.message}{RESET}")
    print(f"{BLUE}Status: {RESET}{data.status}")
    if (results):
        print(f"{BLUE}Results: {RESET}")
        print_results(results)
    print(GREEN,"-"*80,RESET)

class RealTimeFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.stream.flush()
        os.fsync(self.stream.fileno())
class LogConsole:
    def __init__(self, logger_file: Path, console=True):
        self.console = console
        self.file_logger = self._get_file_logger(logger_file)
        self.console_logger = self._get_console_logger()

    def _get_file_logger(self, logger_file: Path):
        logger_name = f"file_{logger_file.resolve()}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            fh = RealTimeFileHandler(logger_file)
            fh.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] - %(message)s",
                "%d-%b-%y %I:%M:%S %p"
            ))
            logger.addHandler(fh)

        return logger

    def _get_console_logger(self):
        logger = logging.getLogger("console")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] - %(message)s",
                "%I:%M:%S %p"
            ))
            logger.addHandler(ch)

        return logger

    def log(self, msg: str, err=False):
        if err:
            self.file_logger.error(msg)
            if self.console:
                self.console_logger.error(f"{RED}{msg}{RESET}")
        else:
            self.file_logger.info(msg)
            if self.console:
                self.console_logger.info(f"{GREEN}{msg}{RESET}")      
