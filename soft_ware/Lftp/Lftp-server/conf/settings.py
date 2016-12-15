
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


USER_HOME = "%s/home" % BASE_DIR
LOG_DIR =  "%s/logs" % BASE_DIR
LOG_LEVEL = "DEBUG"

ACCOUNT_FILE = "%s/conf/accounts.cfg" % BASE_DIR


HOST = "0.0.0.0"
PORT = 9248


#     python   Lftp-client.py   -s localhost -P 9248 -u alex -p abc