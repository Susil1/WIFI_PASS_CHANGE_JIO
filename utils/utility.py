import secrets
import string
import logging
from typing import Any
from dataclasses import dataclass,field

from .colors import RESET,BLUE,GREEN,YELLOW

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
        
class LogConsole:
    def __init__(self,logger_file):
        self.log_file_path = logger_file
        self.file_log = self._get_file_logger()
    def _get_file_logger(self):
        file_logger = logging.getLogger("file")
        file_logger.setLevel(logging.INFO)
        fh = logging.FileHandler(self.log_file_path)
        fh.setFormatter(logging.Formatter("[%(asctime)s] - %(message)s", "%d-%b-%y %I:%M:%S %p")) 
        file_logger.addHandler(fh)
        return file_logger
    def log(self, msg: str,err=False):
        if err:
            self.file_log.error(msg)
        else:
            self.file_log.info(msg)