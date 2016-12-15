import socketserver
import configparser
from conf import settings
import os
import hashlib

STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "ready to send file",
    258 : "md5 verification",
    259:"Authentication failure",
    200:"OK",
    199:"dir not found"
}

import json
class FTPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            self.data = self.request.recv(1024).strip()
            print("recv:",self.data)
            print("client addr:-->",self.client_address[0])
            print(self.data)
            if not self.data:
                print("client closed......")
                break
            data  = json.loads(self.data.decode())
            if data.get('action') is not None:
                print("---->",hasattr(self,"_auth"))
                if hasattr(self,"_%s"%data.get("action")):
                    func = getattr(self,"_%s"%data.get("action"))
                    func(data)
                else:
                    print("Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}")
                    self.send_response(250)
            else:
                print("Invalid cmd")
                self.send_response(251)

    def send_response(self,status_code,data = None):
        response = {"status_code":status_code,"status_msg":STATUS_CODE[status_code]}
        if data:
            response.update(data)
        self.request.send(json.dumps(response).encode())

    def _auth(self,*args,**kwargs):
        data = args[0]
        user = self.authenticate(data.get("username"),data.get("password"))
        if user is None:
            print("Authentication failure")
            self.send_response(259)
        else:
            print("%s Passed authentication"%user["User"])
            self.user = user
            self.send_response(254)

    def authenticate(self,username,password):
        config = configparser.ConfigParser()
        config.read(settings.ACCOUNT_FILE)
        if username in config.sections():
            if password == config[username]["Password"]:
                config[username]["User"] = username
                return config[username]

    def _get(self,*args,**kwargs):
        print("-->get")
        data = args[0]
        file_name = data.get("filename")
        print("获取的文件名:",file_name)
        self.user_home_dir = "%s/%s"%(settings.USER_HOME,self.user["User"])
        self.file_abs_dir = "%s/%s"%(self.user_home_dir,file_name)
        print("file abs  path:",self.file_abs_dir)
        if os.path.isfile(self.file_abs_dir):
            file_size = os.path.getsize(self.file_abs_dir)
            datas = {"file_size":file_size}
            self.send_response(257,datas)
            print("ready to send file")
            self.request.recv(1024)
            file_obj = open(self.file_abs_dir,"rb")
            m = hashlib.md5()
            for line in file_obj:
                self.request.send(line)
                m.update(line)
            else:
                file_obj.close()
                md5 = m.hexdigest()
                print("file send finish")
                print("MD5值:",md5)
                self.request.send(md5.encode())

        else:
            print("remote file not found")
            self.send_response(256)


    def _put(self,*args):

        data = args[0]
        print("recv:",data)
        self.send_response(200)
        file_total_size = data.get("file_size")
        received_size = 0
        user_home_dir = "%s/%s" % (settings.USER_HOME, self.user["User"])
        m = hashlib.md5()
        f = open("%s/%s"%(user_home_dir,data.get("filename")),"wb")
        while received_size < file_total_size:
            msg= self.request.recv(1024)
            m.update(msg)

            received_size += len(msg)
            f.write(msg)
        else:
            md5 = m.hexdigest()
            f.close()
            print("file upload done!")
            self.send_response(200,data={"received_size":received_size,"md5":md5})






    def _ls(self,*args):
        default_path = "%s/%s" % (settings.USER_HOME, self.user["User"])
        data = args[0]
        cmd = data.get("action")
        dir = data.get("dir")
        if dir == "." or dir =="":
            pass
        elif dir == "/":
            file_list = os.listdir(default_path)
            self.send_response(200,data ={"file_list":file_list})

    def _cd(self,*args):
        data = args[0]
        default_path = "%s/%s" % (settings.USER_HOME, self.user["User"])
        print(data)
        mv_to = data.get("mv_to")
        if mv_to in os.listdir(default_path):
            if os.path.isfile("%s/%s"%(default_path,mv_to)):
                print("dir not found")
                self.send_response(199)
            else:
                cour_dir = "/%s"%mv_to
                self.send_response(200,data={"cour_dir":cour_dir})
        elif mv_to == "..":
            cour_dir = default_path.split("/")[0:-1]
            self.send_response(200,data={"cour_dir":cour_dir})
        else:
            print("dir not found")
            self.send_response(199)

