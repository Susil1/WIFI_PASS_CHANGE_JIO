from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection 

from datetime import datetime,timedelta

from utils.utility import UserData,Command
from utils.constants import DATE_FMT,MAX_ATTEMPTS

from .file_handler import get_connection_string

class DB_Connection:
    def __init__(self):
        URL = get_connection_string()
        client:MongoClient = MongoClient(URL)
        db:Database = client["telegram_bot"]
        
        self.user_col:Collection = db["users"]
        self.command_col:Collection = db["commands"]
        self.code_col:Collection = db["codes"]
        self.spam_col:Collection = db["spams"]
        
        self.user_col.create_index("user_id", unique=True)
        self.command_col.create_index("user_id", unique=True)
        self.code_col.create_index("code", unique=True)  
        self.spam_col.create_index("user_id", unique=True)  
        
    def add_user_data(self,user_data:UserData):
        query = { "user_id": user_data.user_id }
        newvalues = { "$set": user_data.toDict() }
        self.user_col.update_one(query,newvalues,upsert=True)
            
    def update_commands(self,new_command_data:Command):
        query = { "user_id": new_command_data.user_id }
        newvalues = { "$set": new_command_data.toDict() }
        self.command_col.update_one(query,newvalues,upsert=True)
    def get_command_data(self,user_id:int):
        query = { "user_id": user_id }
        res = self.command_col.find_one(query)
        return res
    def check_admin(self,user_id:int)-> bool:
        query = { "user_id": user_id }
        data = self.user_col.find_one(query)
        if data and data["role"] == "admin":
            return True
        return False
    def isAuthorised(self, user_id: int) -> bool:
        query = {"user_id": user_id}
        user_data = self.user_col.find_one(query)
        commands_data = self.command_col.find_one(query)
        if not user_data or not commands_data:
            return False
        role = user_data["role"]
        now = datetime.now()
        expiry_date: str = commands_data.get("expiry_date",now.strftime(DATE_FMT))
        commands_remaining: int = commands_data.get("commands_remaining", 0)
        if role == "admin":
            return True
        if expiry_date:
            try:
                date_obj = datetime.strptime(expiry_date, DATE_FMT)
            except ValueError:
                return False
            if date_obj > now:
                return True
            if date_obj < now:
                if commands_remaining:
                    self.command_col.update_one(
                        query,
                        {"$inc": {"commands_remaining": -1}}
                    )
                    return True
                return False
        if commands_remaining:
            self.command_col.update_one(
                query,
                {"$inc": {"commands_remaining": -1}}
            )
            return True
        return False
    def failed_attempts(self,user_id:int)->int:
        query = {"user_id": user_id}
        data = self.spam_col.find_one(query)
        if not data:
            return 0
        return data.get("failed_attempts", 0)
    def add_failed_attempts(self, user_id: int):
        query = {"user_id": user_id}
        now = datetime.now()
        data = self.spam_col.find_one(query)
        if not data:
            self.spam_col.insert_one({
                "user_id": user_id,
                "failed_attempts": 1,
                "last_failed_attempts": now.strftime(DATE_FMT)
            })
            return

        failed_attempts = data.get("failed_attempts", 0)
        try:
            last_failed = datetime.strptime(
                data.get("last_failed_attempts"), DATE_FMT
            )
        except ValueError:
            self.spam_col.update_one(
                query,
                {"$set": 
                    {"last_failed_attempts": now.strftime(DATE_FMT)}
                    }
                )
            last_failed = now

        if now > last_failed + timedelta(days=1):
            self.spam_col.update_one(
                query,
                {"$set": {
                    "failed_attempts": 1,
                    "last_failed_attempts": now.strftime(DATE_FMT)
                }}
            )
            return

        if failed_attempts < MAX_ATTEMPTS:
            self.spam_col.update_one(
                query,
                {"$inc": {"failed_attempts": 1},
                "$set": {"last_failed_attempts": now.strftime(DATE_FMT)}}
            )
            return
        
    def get_auth_data(self,code:str):
        query = { "code": code }
        res = self.code_col.find_one(query)
        self.code_col.delete_one(query)    # Delete If Not stated
        return res
    def get_user_data(self,user_id:int):
        user = self.user_col.find_one({"user_id": user_id})
        auth = self.command_col.find_one({"user_id": user_id})

        combined = {}
        if user: combined.update(user)
        if auth: combined.update(auth)

        return combined
    def delete_user(self, user_id: int) -> bool:
        query = {"user_id": user_id}
        user_res = self.user_col.delete_one(query)
        cmd_res = self.command_col.delete_one(query)
        if user_res.deleted_count > 0 or cmd_res.deleted_count > 0:
            return True
        return False   
    
    def update_used_commands(self,user_id:int,command:str):
        query = { "user_id": user_id }
        self.command_col.update_one(
            query,
            {"$push": {"used_commands": command}}
        )  
