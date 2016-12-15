import optparse
import socket
import json
import hashlib
import  os

STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
}
class FTPClient(object):
    def __init__(self):
        parser = optparse.OptionParser()
        parser.add_option("-s","--server",dest="server",help="ftp server ip address")
        parser.add_option("-P","--port",dest = "port" ,help="port")
        parser.add_option("-u","--username", dest="username",help = "username")
        parser.add_option("-p","--password",dest="password",help="password")
        self.option,self.args = parser.parse_args()
        print(self.option,self.args)
        self.verify_args(self.option,self.args)
        self.make_connection()
    def make_connection(self):
        self.sock = socket.socket()
        self.sock.connect((self.option.server,int(self.option.port)))

    def verify_args(self,options,args):
        if options.username is not None and options.password is not None:
            pass
        elif options.username is None and options.password is None:
            pass
        else:
            exit("Err: username and password must be provided together..")

        if int(options.port) > 0 and int(options.port) < 65535:
            return  True
        else:
            exit("Err:host port must in 0-65535")

    def authenticate(self):
        if self.option.username:
            print(self.option.username,self.option.password)
            return self.get_auth_result(self.option.username,self.option.password)
        else:
            retry_count = 0
            while retry_count <3:
                username = input("username:").strip()
                password = input("password:").strip()
                return self.get_auth_result(username,password)

    def get_auth_result(self,username,password):
        data = {"action":"auth",
                "username":username,
                "password":password}
        self.sock.send((json.dumps(data)).encode())
        print("信息已发送，等待返回")
        response = self.get_response()
        print("recv:",response)
        if response.get("status_code") == 254:
            print("Passed authentication!")
            self.user = username
            return  True
        else:
            print(response.get("status_msg"))


    def get_response(self):
        data = self.sock.recv(1024)
        print("server res",data)
        data = json.loads(data.decode())
        return data
    def _get(self,cmd_list):
        print("get-->",cmd_list)
        if len(cmd_list) == 1:
            print("没有输入要下载的文件名")
            return
        data_header = {"action":"get","filename":cmd_list[1]}
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()
        if response.get("status_code") == 257:
            self.sock.send(b"a")
            remote_file_size = response.get("file_size")
            received_size = 0
            base_file_name = cmd_list[1].split()[-1]
            f = open(base_file_name,"wb")
            m = hashlib.md5()
            while received_size < remote_file_size:
                data = self.sock.recv(1024)
                received_size += len(data)
                f.write(data)
                m.update(data)

            else:
                print("file is received done!")
                local_md5 = m.hexdigest()
                remote_md5 = self.sock.recv(1024).decode()
                print(local_md5,remote_md5)
                if local_md5 == remote_md5:print("文件一致性校验成功！")
                else:print("文件一致性校验失败，数据可能不完整！")
        else:
            print(response.get("status_msg"))


    def _put(self,cmd_list):
        if len(cmd_list) == 1:
            print("没有输入要上传的文件名")
            return
        filename = cmd_list[1].split("/")[-1]
        filename_abs = cmd_list[2]

        local_abs_file = cmd_list[1]
        if os.path.isfile(filename):
            print("is file")
            file_size = os.path.getsize(filename)
            data_header = {"action":"put","filename":filename,"file_size":file_size}
            self.sock.send(json.dumps(data_header).encode())
            data = self.get_response()
            print("返回状态:",data)
            if data.get("status_code") == 200:
                m = hashlib.md5()
                f = open(local_abs_file,"rb")
                for line in f:
                    self.sock.send(line)
                    m.update(line)
                else:
                    print("file upload done!")
                    data = self.get_response()
                    local_md5 = m.hexdigest()
                    print("本地文件的大小: %s 上传到服务器上文件的大小: %s "%(file_size,data.get("received_size")))
                    print("本地MD5: %s  远程MD5: %s"%(local_md5,data.get("md5")))
        else:
            print("文件不存在")


    def _ls(self,cmd_list):
        data = cmd_list
        msg={"action":data[0],"dir":data[1]}
        self.sock.send(json.dumps(msg).encode())
        data = self.get_response()
        file_list = data.get("file_list")
        print( file_list)
        return file_list

    def _cd(self,cmd_list):
        data = cmd_list
        msg = {"action":data[0],"mv_to":data[1]}
        self.sock.send(json.dumps(msg).encode())
        data = self.get_response()
        if data.get("status_code") == 199:
            print("Not a directory")
            cour_dir = ""
        else:
            cour_dir = data.get("cour_dir")
        return cour_dir

    def _process(self):



    def interactive(self):
        if self.authenticate():
            print("---start interactive with %s---" % self.user)
            while True:
                choice = input("[%s/]:"%self.user).strip()
                if len(choice) == 0:continue
                cmd_list = choice.split()
                if hasattr(self,"_%s"%cmd_list[0]):
                    func = getattr(self,"_%s"%cmd_list[0])
                    func(cmd_list)
                else:
                    print("Invalid cmd")




if __name__ =="__main__":
    ftp = FTPClient()
    ftp.interactive()
