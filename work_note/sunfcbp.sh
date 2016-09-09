#!/bin/bash


#判断是否为空
if [ -z $1 ]
then
        echo "请输入需同步的目的,如：sh [cnapp].sh qa1"
        exit 0
fi


#定义时间
today=`date +%Y%m%d%H`

#进入环境root@10.10.3.130
#需同步的主机和IP地址
list="/data/yunweisvn/sh/allinoneqa/list.txt"
ideip=10.77.3.10
test=$(cat $list|grep -w ^$1 | awk -F " " '{print $2}')
testip=$(cat $list|grep -w ^$1 | awk -F " " '{print $3}')
jenkname=$(cat $list |grep -w ^$1 | awk -F'.' '{print $1}' | awk -F' ' '{print $2}')_sunfcbp
localdir="/data/sh/ide_test/"
mkdir -p ${localdir}${jenkname}

echo "test=$test"
echo "testip=$testip"
echo "jenkname=$jenkname"


#更新配置文件
cd /data/yunweisvn/package
svn update

#同步sunfcbp---bin目录

#定义配置文件路径
dmbconf=/data/yunweisvn/package/sunfcbp/allinone/dmb-client.properties
inconf=/data/yunweisvn/package/sunfcbp/allinone/in.adpt
outconf=/data/yunweisvn/package/sunfcbp/allinone/out.adpt
dbconf=/data/yunweisvn/package/sunfcbp/allinone/dbconf.xml
sunfcbpconf=/data/yunweisvn/package/sunfcbp/allinone/settings.properties
logconf=/data/yunweisvn/package/sunfcbp/allinone/log4j.xml

######ide远程打包bin.tar.gz
ssh root@$ideip "cd /home/SambaServer && tar zcf /data/ide/bin.tar.gz bin"
if [ $? -eq 0 ]
then
	echo "bin.tar.gz已压缩完成"
else
	echo "bin.tar.gz压缩失败"
	ssh root@$ideip "rm -f /data/ide/sunif.tar.gz"
	exit 0
fi

###复制最新的bin.tar.gz到本地
cd /data/jenkins/workspace/$jenkname
scp root@$ideip:/data/ide/bin.tar.gz ./bin.tar.gz
if [ $? -eq 0 ]
then
	echo "bin.tar.gz已传到本地"
else
	echo "bin.tar.gz传输失败"
	rm -f bin.tar.gz
	exit 0
fi

###本地解压bin.tar.gz
cd /data/jenkins/workspace/$jenkname
rm -rf bin
tar zxf bin.tar.gz
if [ $? -eq 0 ]
then
	echo "bin.tar.gz已解压完成"
	rm -f bin.tar.gz
else
	echo "bin.tar.gz解压失败"
	rm -rf bin
	exit 0
fi

####################################发布sunfcbp###############################################


###关闭sunfcbp进程
sleep 5
ssh sunfcbp@$testip "cd /home/sunfcbp/sunflow && ./stopall"
sleep 10
ssh sunfcbp@$testip "netstat -anput |grep 7005"
if [ $? -ne 0 ]
then
	echo "sunfcbp进程已关闭"
	sleep 60
else
	echo "sunfcbp进程未关闭"
	exit 0
fi

###备份
ssh sunfcbp@$testip "cd /home/sunfcbp/sunflow && tar zcf bin.${today}.tar.gz bin"
if [ $? -eq 0 ]
then
	echo "bin备份完成"
else
	echo "bin没有备份成功,请重新执行"
        exit 0
fi



##替换配置
\cp -f $dmbconf /data/jenkins/workspace/$jenkname/bin/dmb-client.properties
\cp -f $inconf /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/in.adpt
\cp -f $outconf /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/out.adpt
\cp -f $dbconf /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/dbconf.xml
\cp -f $sunfcbpconf /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/settings.properties
\cp -f $logconf /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/log4j.xml
rm -f /data/jenkins/workspace/$jenkname/bin/sunline/out/ChinaPay/etc/key/*.key
\cp -f /data/yunweisvn/package/sunfcbp/allinone/MerPrK_808080211389886_20151203162656.key /data/jenkins/workspace/$jenkname/bin/sunline/out/ChinaPay/etc/key/MerPrK_808080211389886_20151203162656.key
\cp -f /data/yunweisvn/package/sunfcbp/allinone/MerPrK_808080211389885_20151203162635.key /data/jenkins/workspace/$jenkname/bin/sunline/out/ChinaPay/etc/key/MerPrK_808080211389885_20151203162635.key

\cp -f /data/yunweisvn/package/sunfcbp/allinone/PgPubk.key /data/jenkins/workspace/$jenkname/bin/sunline/out/ChinaPay/etc/key/PgPubk.key
\cp -f /data/yunweisvn/package/sunfcbp/allinone/cert/20060400000044502.p12 /data/jenkins/workspace/$jenkname/bin/sunline/out/payplat/etc/cert/20060400000044502.p12
\cp -f /data/yunweisvn/package/sunfcbp/allinone/cert/20060400000044502.cer /data/jenkins/workspace/$jenkname/bin/sunline/out/payplat/etc/cert/20060400000044502.cer

\cp -f /data/yunweisvn/package/sunfcbp/allinone/cert/TLCert-test.cer /data/jenkins/workspace/$jenkname/bin/sunline/out/payplat/etc/cert/TLCert-test.cer


#替换前后台回调地址
sed -i "s@^allinpay.pickupUrl=".*$"@allinpay.pickupUrl=https://$test/frontPaymentResults.do@" /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/settings.properties
sed -i "s@^allinpay.receiveUrl=".*$"@allinpay.receiveUrl=https://$test/backPaymentResults.do@" /data/jenkins/workspace/$jenkname/bin/sunline/common/etc/settings.properties


if [ $? -eq 0 ]
then
	echo "配置文件已替换完毕"
else
	echo "配置文件替换失败"
	exit 0
fi

chown -R jenkins.jenkins /data/jenkins/workspace/$jenkname

#打包
cd /data/jenkins/workspace/$jenkname/
tar zcf ${localdir}${jenkname}/bin.tar.gz bin
if [ $? -eq 0 ]
then
        echo "bin打包完毕"
else
        echo "bin打包失败"
        rm -rf ${localdir}${jenkname}/bin.tar.gz
        exit 0
fi



cd ${localdir}${jenkname}
#复制 bin的最新bin.tar.gz到allinone环境
scp bin.tar.gz sunfcbp@$testip:/home/sunfcbp/sunflow/
if [ $? -eq 0 ]
then
        echo "bin.tar.gz已传到$testip"
else
        echo "bin.tar.gz未传送到$testip"
        exit 0
fi


##解压远端bin.tar.gz包
ssh sunfcbp@$testip "cd /home/sunfcbp/sunflow && rm -rf bin && tar zxf bin.tar.gz"
if [ $? -eq 0 ]
then
        echo "bin.tar.gz解压完毕"
else
        echo "bin.tar.gz解压失败!!!"
        exit 0
fi


###启动远端sunfcbp服务
ssh sunfcbp@$testip "cd /home/sunfcbp && source .bash_profile &&source /etc/profile && cd /home/sunfcbp/sunflow && ./runall"

sleep 3 && kill -9 $(ps aux |grep -v grep | grep "./runall" | awk '{print $2}' | sort -n | head -n 1)

###删除本地bin.tar.gz包
rm -rf /data/jenkins/workspace/$jenkname/bin*
rm -f ${localdir}${jenkname}/bin.tar.gz

exit 0







