import configparser
import json

from utils.paths import CONFIG_FILE,CREDENTIAL_PATH,BASE_PATH,LOGGER_PATH
from utils.utility import LogConsole
config = configparser.ConfigParser()

# Configure IP address
config.read(CONFIG_FILE)
def getLoginData():
    if (not CREDENTIAL_PATH.exists()):
        raise FileNotFoundError("Credential File Not Found")
    with open(CREDENTIAL_PATH) as json_file:
        login_data = json.load(json_file)
    
    return login_data

def updateLoginData(data):
    with open(CREDENTIAL_PATH,mode="w") as json_file:
        json.dump(data,json_file)
    
def updateRouterPassword(newpassword):
    with open(BASE_PATH/"newpass.txt","w") as file:
        file.write(newpassword)
    
def downloadPacket(file_name,content):
    with open(file_name, "wb") as f:
        f.write(content)

logger = LogConsole(LOGGER_PATH)