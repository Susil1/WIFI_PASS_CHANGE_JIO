from configparser import ConfigParser
from urllib.parse import quote
from utils.paths import DB_CONFIG_FILE
config = ConfigParser()
config.read(DB_CONFIG_FILE)

def get_connection_string() -> str:
    data = config["mongo"]
    user = data["user"]
    appname = data["appname"]
    url_encoded_password = quote(data["password"])  # URL encoded
    conn_str = f"mongodb+srv://{user}:{url_encoded_password}@{appname}.blup5fc.mongodb.net/?appName={appname}"
    return conn_str
    
    