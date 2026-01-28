# Constants
from router.file_handler import config

IP_ADDRESS = config["IP"]["ip"]
URL = f"https://{IP_ADDRESS}/WCGI"

DATE_FMT = "%Y-%m-%d %H:%M:%S"
MAX_ATTEMPTS = 5
