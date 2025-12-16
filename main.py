import requests
import json
import urllib3
from dataclasses import dataclass,field
from pathlib import Path
from pprint import pprint
import configparser
import secrets
import string

#Constants
BASE_PATH = Path(__file__).parent
CREDENTIAL_PATH = BASE_PATH/"credentials.json"
CONFIG_FILE = BASE_PATH/"config.ini"

# Configure IP address
config = configparser.ConfigParser()
config.read("config.ini")

IP_ADDRESS = config["IP"]["ip"]
URL = f"https://{IP_ADDRESS}/WCGI"

# Disable the warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Initialise the session
SESSION = requests.Session()


def getNewPassword():
    myNames = ["susil","sumit","situ"]
    chars =  string.digits
    symbol = "!@#$%^&*_-"

    name = secrets.choice(myNames)
    nums = ''.join(secrets.choice(chars) for _ in range(secrets.randbelow(3) + 3))
    symbols = ''.join(secrets.choice(symbol) for _ in range(secrets.randbelow(3) + 2))

    password = name + nums + symbols

    return password

# dataclasses
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

class routerConnection:
    def __init__(self,login_data):
        self.login_data = login_data
        self.__is_loggedIn = False
    def raiseForLogin(self):
        if (not self.__is_loggedIn):
            raise Exception(f"You Are Not Logged In!")
    def request(self,method:str,params={}):
        HEADERS = {"Cookie": f"cSupport=1;"}

        payload = Payload(
            method = method,
            params=params
        )
        response = requests.post(
            URL,
            headers=HEADERS,
            json=payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def initialise_connection(self,params=None,times=0):
        HEADERS = {"Cookie": f"cSupport=1;"}
        if not params:
            login_payload = Payload(
                method = "login",
                params = self.login_data,
            )
        else:
            login_payload = Payload(
                method = "login",
                params = params,
            )
        login_response = SESSION.post(
            URL,
            headers=HEADERS,
            json=login_payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        if login_response.status_code != 200:
            raise ConnectionError("Login request failed")

        result = login_response.json()
        if (result["code"] == "ERR_LOGIN_ACCOUNT_LOCKED"):
            raise Exception("Too Many Wrong Attempts")
        if (result["code"]=="ERR_LOGIN_CREDENTIALS_FAIL" and times>=1):
            raise Exception("Invalid Credentials!")
        if (result["code"]=="ERR_LOGIN_CREDENTIALS_FAIL"):
            default_login_data = {
                "username": "admin",
                "password": "Jiocentrum"
            }
            print("Entering default credentials...")
            return self.initialise_connection(params=default_login_data,times=times+1)
            
        if "results" not in result:
            raise ValueError("Unexpected login response")
        
        if_logged_in=result.get("forcedLogin",False)
        loggedId=result["results"].get("loggedId",None)
        
        #Adding DATA 
        self.sysauth=login_response.cookies.get("sysauth")
        self.token = result["results"].get("token")
        if not self.token:
            raise ValueError("Token not received from router")
        
        HEADERS = {
        "Cookie": f"cSupport=1; sysauth={self.sysauth}"
        }
        
        if (if_logged_in):
            print("Already Logged In...")
            params={
                "authHeader":f"Bearer {self.token}",
                "loggedId":loggedId
                }
        else:
            params={"authHeader":f"Bearer {self.token}"}
        post_login_payload = Payload(
            method = "postLogin",
            params=params
            )

        post_login_response = SESSION.post(
            URL,
            headers=HEADERS,
            json=post_login_payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        if (post_login_response.json()["code"] == "ERR_POSTLOGIN_FACTORY_RESET"):
            password = self.login_data["password"]
            params = {
                "adminPassword": password,
                "guestPassword": password,
                "confirmAdminPassword": password,
                "confirmGuestPassword": password
                }
            self.getInfo("setFactoryReset",params=params)
            return self.initialise_connection()
        if post_login_response.status_code != 200:
            raise ConnectionError("Login request failed")
        self.__is_loggedIn=True
        return post_login_response.json().get("status","NOT_OK")
                
    def logout(self):
        self.raiseForLogin()
        print("Logging Out...")
        HEADERS = {
            "Cookie": f"cSupport=1; sysauth={self.sysauth}"
            }

        logout_payload = Payload(
            method = "logout"
        )
        
        logout_response = SESSION.post(
            URL,
            headers=HEADERS,
            json=logout_payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        return logout_response.json().get("status","NOT_OK")
    
    def getInfo(self,method=None,params=None,info_payload=None):
        self.raiseForLogin()
        HEADERS = {
            "Cookie": f"cSupport=1; sysauth={self.sysauth}",
            "Authorization": f"Bearer {self.token}",
        }
        if (not info_payload):
            info_payload = Payload(
                method = method if method else "",
                params = params if params else {},
            )

        info_response = requests.post(
            URL,
            headers=HEADERS,
            json=info_payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        if (info_response.headers.get("Content-Type") != "application/json"):
            return info_response.content
        else:
            return info_response.json()
    def changePassword(self,newpass):
        self.raiseForLogin()
        wireless_config=self.getInfo("getWirelessConfiguration")
        if (isinstance(wireless_config,dict) and wireless_config["status"] != "OK"):
            raise ConnectionError("Error Getting WirelessConfiguration!")
        if isinstance(wireless_config,dict):
            results = wireless_config["results"]
            ssid = results["ssid"]
            security = results["security"]
            recordId = results["recordId"]
            pararms={
                "recordId":recordId,
                "ssid":ssid,
                "security":security,
                "password":newpass
                }
            passchange_payload = Payload(
                method="setWirelessConfiguration",
                params=pararms
            )
            passchange_response = self.getInfo(info_payload=passchange_payload)
            if (isinstance(passchange_response,dict) and passchange_response["status"]=="OK"):
                print("Password Successfully Changed")
                with open("newpass.txt","w") as file:
                    file.write(newpass)
                print(f"New Password: {newpass}")
        else:
            raise ValueError("Type Mismatch")
    def change_admin_password(self):
        self.raiseForLogin()
        password = input("Enter New Password for ADMIN: ")
        users = self.getInfo("getUsers")
        if (isinstance(users,dict) and users["results"]):
            print(f"Changing Admin Password to '{password}'")
            result = users["results"]
            admin = result[0] if result[0]["username"]=="admin" else result[1]
            recordId = admin["recordId"]
            userType = admin["userType"]
            params = {
                "password":password,
                "recordId":recordId,
                "userType":userType
            }
            result = self.getInfo("changeUserPassword",params=params)
            if (isinstance(result,dict) and result["status"] == "ERROR"):
                print("Enter A Valid Password!")
                return self.change_admin_password()
            with open(CREDENTIAL_PATH,"w") as json_file:
                data = {
                    "username": "admin",
                    "password": password
                }
                json.dump(data,json_file)
            
        
    def capture_packet(self,interface,size,file_name="capture.pcap"):
        self.raiseForLogin()
        self.getInfo("startCapturePackets",params={"interface":interface,"size":size})
        print("Packet Capture Started.")
        input("Press Enter To Stop Capturing Packets...")
        self.getInfo("stopCapturePackets")
        contents=self.getInfo("downloadCapturePactets",params={"fileDownload": "yes"})
        with open(file_name, "wb") as f:
            f.write(contents)
        print(f"Packet capture saved as {file_name}")

def main():
    print("Logging In...")
    if (not CREDENTIAL_PATH.exists()):
        raise FileNotFoundError("Credential File Not Found")
    with open(CREDENTIAL_PATH) as json_file:
        login_data = json.load(json_file)
    connection=routerConnection(login_data)
    # pprint(connection.request("preLogin"))
    status=connection.initialise_connection()
    if (status=="OK"):
        print("Logged in successfully.")
    # connection.change_admin_password()
    # newpass= getNewPassword()
    # connection.changePassword(newpass)
    # connection.capture_packet(interface="any",size=5)
    # pprint(connection.getInfo("setFactoryDefaults"))
    # pprint(connection.getInfo("getLanClients"))
    # pprint(connection.getInfo("getMemoryUtilisation"))
    # pprint(connection.getInfo("getSystemStatus"))
    # pprint(connection.getInfo("getStorageDevices"))
    # pprint(connection.getInfo("getCpuUtilisation"))
    # pprint(connection.getInfo("getApplicationsStatus"))
    # pprint(connection.getInfo("getSystemInformation"))
    # pprint(connection.getInfo("getApplicationsStatus"))
    # pprint(connection.getInfo("getSystemDateTime"))
    # pprint(connection.getInfo("getWirelessConfiguration"))
    # pprint(connection.getInfo("getWanStatus"))
    # pprint(connection.getInfo("setReboot"))
    # pprint(connection.getInfo("getLanStatus",params={"wanType":""}))
    connection.logout()

    
if (__name__=="__main__"):
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")