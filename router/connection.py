import urllib3
import requests

from router.file_handler import updateLoginData,updateRouterPassword,downloadPacket

from utils.utility import getNewPassword,Payload,Response,LogConsole
from utils.constants import URL
from utils.paths import LOGGER_PATH
# Disable the warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Initialise the session
SESSION = requests.Session()

class routerConnection:
    def __init__(self,login_data,console_log = True):
        self.login_data = login_data
        self.__is_loggedIn = False
        self.logger = LogConsole(logger_file=LOGGER_PATH,console=console_log)
    
    def raiseForLogin(self):
        if (not self.__is_loggedIn):
            raise Exception(f"You Are Not Logged In!")
        
    def _headers(self, auth=False):
        headers = {"Cookie": "cSupport=1;"}
        if auth:
            headers["Cookie"] += f" sysauth={self.sysauth}"
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    def request(self,payload:Payload,handler,auth):
        self.logger.log(f"getting request for '{payload.method}'")
        HEADERS = self._headers(auth)
        response = handler.post(
            URL,
            headers=HEADERS,
            json=payload.json(),
            verify=False,  # router uses self-signed cert
            timeout=10
        )
        response.raise_for_status()
        self.logger.log(f"Request completed for '{payload.method}'")
        
        return response

    def initialise_connection(self,params=None,times=0):        
        if not params:
            login_payload:Payload = Payload(
                method = "login",
                params = self.login_data,
            )
        else:
            login_payload:Payload = Payload(
                method = "login",
                params = params,
            )
        login_response = self.request(login_payload,handler=SESSION,auth=False)
        login_result = login_response.json()
        code:str = login_result["code"]
        
        if (code == "ERR_LOGIN_ACCOUNT_LOCKED"):
            raise Exception("Too Many Wrong Attempts")
        if (code == "ERR_LOGIN_CREDENTIALS_FAIL" and times>=1):
            raise Exception("Invalid Credentials!")
        if (code == "ERR_LOGIN_CREDENTIALS_FAIL"):
            self.logger.log("Invalid Credentials!",err=True)
            default_login_data = {
                "username": "admin",
                "password": "Jiocentrum"
            }
            self.logger.log("Entering default credentials...")
            return self.initialise_connection(params=default_login_data,times=times+1)
            
        if "results" not in login_result:
            raise ValueError("Unexpected login response")
        
        if_logged_in = login_result.get("forcedLogin",False)
        loggedId = login_result["results"].get("loggedId",None)
        
        #Adding DATA 
        self.sysauth=login_response.cookies.get("sysauth")
        self.token = login_result["results"].get("token")
        
        if not self.token:
            raise ValueError("Token not received from router")
        
        if (if_logged_in):
            self.logger.log("Already Logged In")
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

        post_login_response = self.request(post_login_payload,SESSION,auth=True).json()
        
        if (post_login_response["code"] == "ERR_POSTLOGIN_FACTORY_RESET"):
            self.logger.log("Device in factory default mode.")
            password = self.login_data["password"]
            params = {
                "adminPassword": password,
                "guestPassword": password,
                "confirmAdminPassword": password,
                "confirmGuestPassword": password
                }
            self.getInfo("setFactoryReset",params=params,errorForNotLogin=False)
            return self.initialise_connection()

        self.__is_loggedIn=True
        return post_login_response.get("status","NOT_OK")
    def reconnect(self):
        session_status:Response = self.getInfo("getSessionStatus")
        if not (session_status.code == "OK_SESSION_LOGGGED"):
            self.initialise_connection()
            
    def logout(self):
        self.raiseForLogin()
        self.logger.log("Logging Out")
        logout_payload = Payload(
            method = "logout"
        )
        
        logout_response = self.request(logout_payload,SESSION,auth=True).json()
        status = logout_response.get("status","NOT_OK")
        if (status == "OK"):
            self.logger.log("Logout successfully")
        return status
    
    def getInfo(self,method="",params={},info_payload=None,auth=True,errorForNotLogin = True)->Response:
        self.raiseForLogin() if errorForNotLogin else None
        
        if (not info_payload):
            info_payload = Payload(
                method = method,
                params = params,
            )

        info_response = self.request(info_payload,requests,auth=auth)
        
        response = info_response.json()
        code = response["code"]
        message = response["message"]
        status = response["status"]
        results = response.get("results",{})
    
        return Response(code=code,message=message,status=status,results=results)
    def changePassword(self,newpass):
        self.raiseForLogin()
        
        wireless_config=self.getInfo("getWirelessConfiguration")
        if (wireless_config.status != "OK"):
            return wireless_config.status
        
        results = wireless_config.results
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
        if (passchange_response.status=="OK"):
            self.logger.log(f"wifi password changed successfully pass: {newpass}")
            updateRouterPassword(newpass)
        return passchange_response.status
    def change_admin_password(self,password):
        self.raiseForLogin()
        users = self.getInfo("getUsers")
        result = users.results
        if (result):
            self.logger.log(f"Changing Admin Password to '{password}'")
            
            admin = result[0] if result[0]["username"]=="admin" else result[1]
            recordId = admin["recordId"]
            userType = admin["userType"]
            
            params = {
                "password":password,
                "recordId":recordId,
                "userType":userType
            }
            result = self.getInfo("changeUserPassword",params=params)
            
            if (result.status == "ERROR"):
                return result
            data = {
                    "username": "admin",
                    "password": password
                }
            self.logger.log("Admin password changed successfully")
            updateLoginData(data)
            return result
        return Response(
            code="404",
            message="error getting results",
            status="ERROR",
            results=[]
        )
    def __download_data(self,file_name):
        self.raiseForLogin()
        
        payload = Payload(
            method = "downloadCapturePactets",
            params={"fileDownload": "yes"}
        )
        
        response = self.request(payload,requests,auth=True)
        
        downloadPacket(file_name,content=response.content)
        self.logger.log(f"Packet capture saved as {file_name}")
        
    def capture_packet(self,interface,size,file_name="capture.pcap"):
        self.raiseForLogin()
        self.getInfo("startCapturePackets",params={"interface":interface,"size":size})
        self.logger.log("Packet Capture Started.")
        input("Press Enter To Stop Capturing Packets...")
        self.getInfo("stopCapturePackets")
        self.__download_data(file_name)
