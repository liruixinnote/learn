import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core.main import Auto_tools

if __name__ =="__main__":
    a = Auto_tools()
    a.run()