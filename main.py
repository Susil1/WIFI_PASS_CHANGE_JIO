from utils.utility import print_response
from utils.colors import RED,RESET

from router.file_handler import getLoginData
from router.connection import routerConnection

def main():
    print("Logging In...")
    login_data = getLoginData()
    connection=routerConnection(login_data)
    # pprint(connection.getInfo("preLogin",auth=False))
    status=connection.initialise_connection()
    if (status=="OK"):
        print("Logged in successfully.")
    # connection.change_admin_password()
    # newpass= getNewPassword()
    
    # connection.changePassword(newpass)
    # pprint(connection.getInfo("setFactoryDefaults"))
    # pprint(connection.getInfo("setReboot"))
    
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
        print(f"{RED}Error: {RESET}{e}")