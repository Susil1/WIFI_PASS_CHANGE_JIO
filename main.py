from utils.utility import print_response
from utils.colors import RED,RESET

from router.file_handler import getLoginData,logger
from router.connection import routerConnection

def main():
    logger.log("Logging in")
    login_data = getLoginData()
    connection=routerConnection(login_data)
    logger.log("login data fetched. initialising connection")
    status=connection.initialise_connection()
    if (status=="OK"):
        logger.log("Logged in successfully")
    # print_response(connection.change_admin_password(password="1"))
    # newpass= getNewPassword()
    
    # connection.changePassword(newpass)
    # print_response(connection.getInfo("setFactoryDefaults"))
    # print_response(connection.getInfo("setReboot"))
    
    # connection.capture_packet(interface="any",size=5)
    
    # print_response(connection.getInfo("getLanClients"))
    # print_response(connection.getInfo("getMemoryUtilisation"))
    # print_response(connection.getInfo("getSystemStatus"))
    # print_response(connection.getInfo("getStorageDevices"))
    # print_response(connection.getInfo("getCpuUtilisation"))
    # print_response(connection.getInfo("getApplicationsStatus"))
    # print_response(connection.getInfo("getSystemInformation"))
    # print_response(connection.getInfo("getApplicationsStatus"))
    # print_response(connection.getInfo("getSystemDateTime"))
    # print_response(connection.getInfo("getWirelessConfiguration"))
    # print_response(connection.getInfo("getWanStatus"))
    # print_response(connection.getInfo("getLanStatus",params={"wanType":""}))
    connection.logout()

    
if (__name__=="__main__"):
    try:
        main()
    except Exception as e:
        logger.log(f"{e}",err=True)