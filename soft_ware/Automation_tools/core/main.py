import  optparse
import paramiko
import configparser
from  conf import settings
from multiprocessing import  Process
import  logging
from  logging import  handlers



server_list = []
tmp_ser_list = []
class  Auto_tools(object):
    def __init__(self):
        parser = optparse.OptionParser()
        parser.add_option("-s", "--server", dest="server", help="servername")
        parser.add_option("-g", "--servergroup", dest="servergroup", help="a server group")
        parser.add_option("-c", "--cmd", dest="cmd", help="command")
        self.options,self.args = parser.parse_args()
        if self.options.server:
            self.server_list = self.options.server.split(",")
        if self.options.servergroup:
            self.server_group_list = self.options.servergroup.split(",")
        self.cmd = self.options.cmd

    def config_group(self,groupname):
        config = configparser.ConfigParser()
        config.read(settings.GROUP_FILE)
        config.sections()
        for i in config[groupname]:
            print(config[groupname][i])
            tmp_ser_list.append(config[groupname][i])


    def config_arg(self,servername):
        config = configparser.ConfigParser()
        config.read(settings.HOST_FILE)
        config.sections()
        try:
            self.ip = config[servername]["ip"]
            self.port = int(config[servername]["port"])
            self.username = config[servername]["username"]
            self.password = config[servername]["password"]
            self.optp = config.sections()
        except KeyError as e:
            print("no host: %s"%e)

    def log(self,msg):
        logger = logging.getLogger("test.log")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(settings.DEBUG_LOG, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter('%(asctime)s  %(filename)s:%(lineno)d   - %(levelname)s: %(message)s')
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)
        logger.debug(msg)


    def ssh_cmd(self,ip,port,username,password,cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip,port,username,password)
            stdin, stdout ,stderr = ssh.exec_command(cmd)
            result = stdout.read()
            print(result.decode())
            ssh.close()
        except Exception as e:
            print("ssh err")
        return result

    def do_cmd(self):
        self.ssh_cmd(self.ip, self.port, self.username, self.password, self.cmd)



    def run(self):
        if  self.options.server:

            for i in self.server_list:
                server_list.append(i)
                self.config_arg(i)
                if i in self.optp:
                    msg = "%s ---> %s"%(i,self.cmd)
                    self.log(msg)
                    print("-----------------------------server name : %s ----------------------------"%i)
                    i = Process(target=self.do_cmd)
                    i.start()
                    i.join()
        if self.options.servergroup:
            for j in self.server_group_list:
                tmp = []
                self.config_group(j)
                for i in tmp_ser_list:
                    self.config_arg(i)
                    tmp.append(i)
                    # tmp_ser_list.remove(i)
                    print("######################## server name %s##########################"%i)
                    i = Process(target=self.do_cmd)
                    i.start()
                    i.join()

                else:

                    for i in tmp:
                        tmp_ser_list.remove(i)






if __name__ =="__main__":
    a = Auto_tools()
    a.run()