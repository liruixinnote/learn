import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR =  "%s/logs" % BASE_DIR
LOG_LEVEL = "DEBUG"
HOST_FILE = "%s/conf/host.cfg" % BASE_DIR
GROUP_FILE = "%s/conf/group.cfg" % BASE_DIR
DEBUG_LOG = "%s/debug.log"%LOG_DIR

