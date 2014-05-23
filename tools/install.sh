#!/bin/bash

#check if java has been installed
function hasJava {
    v=`java -version 2>&1`

    echo 'check java platform...'

    pos=`expr match "$v" 'java version \"1.7.0_51\"'`
    if [ $pos -gt 0 ]
    then
    return 1
    else
    return 0
    fi
}

set -x
#install java
hasJava
r=$?
if [ $r -eq 1 ]
then
	echo "java was installed"
else
	echo "java was not installed"
	sudo add-apt-repository ppa:webupd8team/java
	apt-get update
	sudo apt-get install oracle-java7-installer -y
fi

#install es lib
mkdir ~/install
cd ./install
wget http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.1.0.zip
sudo unzip elasticsearch-1.1.0.zip -d /usr/local/elasticsearch
cd /usr/local/elasticsearch/elasticsearch-1.1.0

#install plugin
sudo bin/plugin -install elasticsearch/elasticsearch-cloud-aws/2.1.0
sudo bin/plugin -install polyfractal/elasticsearch-inquisitor
sudo bin/plugin -install lukas-vlcek/bigdesk/2.4.0
sudo bin/plugin -install mobz/elasticsearch-head
sudo bin/plugin -install elasticsearch/elasticsearch-mapper-attachments/2.0.0

#install as service
cd ~/install
sudo wget https://github.com/elasticsearch/elasticsearch-servicewrapper/zipball/master
sudo unzip master
#filelist=`ls ~/install`
#PREFIX=elasticsearch-elasticsearch-servicewrapper
#for filename in $filelist
#do
#	if [[ $filename == $PREFIX* ]]
#	then
#		break
#	fi
#done
#sudo mv $filename/service/  /usr/local/elasticsearch/elasticsearch-1.1.0/bin/
sudo mv *servicewrapper*/service/ /usr/local/elasticsearch/elasticsearch-1.1.0/bin/
rm -Rf *servicewrapper*
cd /usr/local/elasticsearch/elasticsearch-1.1.0/
sysbit=`getconf LONG_BIT`
if [ $sysbit -eq 64 ]
then
	echo "install elasticsearch64"
    sudo bin/service/elasticsearch64 install
else
	echo "install elasticsearch32"
	sudo bin/service/elasticsearch32 install
fi
echo "install complete successfully!"
