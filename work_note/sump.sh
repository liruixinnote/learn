#! /bin/bash

#判断是否为空
if [ -z $1 ]
then
        echo "请输入需同步的目的,如：sh [cnapp].sh qa1"
        exit 0
fi


#进入环境root@10.10.3.130
#需同步的主机和IP地址
list="/data/yunweisvn/sh/allinoneqa/list.txt"
test=$(cat $list|grep -w ^$1 | awk -F " " '{print $2}')
testip=$(cat $list|grep -w ^$1 | awk -F " " '{print $3}')
jenkname=$(cat $list |grep -w ^$1 | awk -F'.' '{print $1}' | awk -F' ' '{print $2}')_sump
localdir="/data/sh/script_test/"
mkdir -p ${localdir}${jenkname}


echo "test=$test"
echo "testip=$testip"
echo "jenkname=$jenkname"
today=`date +%Y%m%d%H%M`


#取bsbsump.war并解压
cd /data/sh/
mkdir -p ${localdir}${jenkname}/bsbsump
#\cp /data/jenkins/workspace/$jenkname/source/systems/bsbsump/target/bsbsump.war ./bsbsump
\cp /data/jenkins/workspace/$jenkname/source/systems/bsbsump/target/bsbsump.war ${localdir}${jenkname}/bsbsump 
cd ${localdir}${jenkname}/bsbsump
/usr/java/jdk1.7.0_60/bin/jar xf bsbsump.war
rm -rf bsbsump.war


#同步sump后台运营管理平台

#定义sump配置文件路径
meportconf=${localdir}${jenkname}/bsbsump/WEB-INF/classes/report.properties
sumpdbconf=${localdir}${jenkname}/bsbsump/WEB-INF/classes/jdbc.properties


###关闭sump进程
ssh tomcat@$testip "cd /home/tomcat && ps aux| grep -v grep | grep /data/mag-instances/sump-qa28080/conf | awk '{print \$2}' >> /home/tomcat/sumppid"
PID=`ssh tomcat@$testip "cat  /home/tomcat/sumppid"`
ssh tomcat@$testip "kill -9 $PID"
if [ $? -eq 0 ]
then
	echo "sump进程已关闭"
else
	echo "sump进程关闭失败"
	exit 0 
fi

ssh tomcat@$testip "rm -rf /home/tomcat/sumppid"

#备份原sump
ssh tomcat@$testip "cd /data/mag-instances/sump-qa28080/webapps/ && tar zcf bsbsump.bak${today}.tar.gz bsbsump"
if [ $? -eq 0 ]
then
        echo "sump备份成功"
else
        echo "sump备份失败"
fi


#sump打包和替换配置文件
cd ${localdir}${jenkname}

##修改配置文件report.properties
sed -i "s@^login_url=".*$"@login_url=http://127.0.0.1:28081/jasperserver/rest/login?j_username=jasperadmin\&j_password=jasperadmin@" $reportconf
sed -i "s@^rpt_baseurl=".*$"@rpt_baseurl=http://127.0.0.1:28081/jasperserver/rest_v2/reports/ReportTemplate/hfaxTemplate/@" $reportconf

##修改配置文件jdbc.properties
sed -i "s/^jdbc_url=".*$"/jdbc_url=jdbc:oracle:thin:@127.0.0.1:1521:prod/" $sumpdbconf
sed -i "s@^jdbc_username=".*$"@jdbc_username=sump@" $sumpdbconf
sed -i "s@^jdbc_password=".*$"@jdbc_password=smp123~ab@" $sumpdbconf


tar zcf ${localdir}${jenkname}/bsbsump.tar.gz bsbsump
if [ $? -eq 0 ]
then
	echo "bsbsump.tar.gz打包完毕"
else
	echo "bsbsump.tar.gz打包失败"
	rm -rf ${localdir}${jenkname}/bsbsump.tar.gz
	exit 0
fi


chown -R tomcat:tomcat ${localdir}${jenkname}
rm -rf ${localdir}${jenkname}/bsbsump

###
cd ${localdir}${jenkname}

#复制sump的最新bsbsump.tar.gz
scp bsbsump.tar.gz tomcat@$testip:/data/mag-instances/sump-qa28080/webapps/bsbsump.tar.gz
if [ $? -eq 0 ]
then
        echo "bsbsump.tar.gz已传到${testip}"
else
        echo "bsbsump.tar.gz未传送到${testip}"
fi

#####删除原来的bsbsump目录
ssh tomcat@$testip "rm -rf /data/mag-instances/sump-qa28080/webapps/bsbsump"
if [ $? -eq 0 ]
then
        echo "原bsbsump程序清除成功"
else
        echo "原bsbsump程序清除失败"
fi


###清除缓存
ssh tomcat@$testip "rm -rf /data/mag-instances/sump-qa28080/temp/ehcache"


###远程解包bsbsump.tar.gz
ssh tomcat@$testip "cd /data/mag-instances/sump-qa28080/webapps/ && tar zxf /data/mag-instances/sump-qa28080/webapps/bsbsump.tar.gz"
if [ $? -eq 0 ]
then
        echo "bsbsump解包完毕"
else
        echo "bsbsump解包失败"
        exit 0
fi

###启动服务
ssh tomcat@$testip "cd /data/mag-instances && ./start_sump_qa28080.sh" &
sleep 3 && kill -9 $(ps aux | grep -v grep | grep "ssh tomcat@$testip cd /data/mag-instances \&\& ./start_sump_qa28080.sh" | awk '{print $2}')

if [ $? -eq 0 ]
then
        echo "sump发布完毕."
else
        echo "sump发布失败!!!"
fi


###删除本地bsbsump.tar.gz包

rm -f ${localdir}${jenkname}/bsbsump.tar.gz

###删除本地代码

rm -rf /data/jenkins/workspace/$jenkname/*

exit 0


