#!/bin/bash
set -x

APTCLONEDIR=/local/repository/cloudlab_c6220_JobManager_Ubuntu22_5.15.0-69-generic_10_18_2023.apt-clone.tar.apt-clone.tar.gz
WORKDIR=/local/repository/experiment-scripts/cloudlab_setup/c6220

sudo apt-get update -y
sudo apt-get install -y apt-clone

cp /mydata/*.tar.gz .

tar -xf experiment-scripts.tar.gz
mv experiment-scripts tmp-scripts

git clone --recursive https://github.com/EEStrmCmptng/experiment-scripts.git

# copy over pre-built flink-simplified jar files
mv tmp-scripts/flink-simplified experiment-scripts/

# reloading system libraries needed
sudo apt-clone restore $APTCLONEDIR

# disable HyperThreads
echo off | sudo tee /sys/devices/system/cpu/smt/control

# disable TurboBoost
echo "1" | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# flink related python libraries
pip install -r $WORKDIR/requirements.txt

# disable irq rebalance
sudo killall irqbalance

# set irq affinity - make sure receive/transmit queues are mapped to the same core
ieth=$(ifconfig | grep -B1 10.10.1 | grep -o "^\w*")
sudo $WORKDIR/intel_set_irq_affinity.sh -x all ${ieth}

# list current status
sudo ufw status

# setup firewall
# allow ssh
sudo ufw allow ssh

# allow connections from the following IP
sudo ufw allow from 10.10.1.1
sudo ufw allow from 10.10.1.2
sudo ufw allow from 10.10.1.3
sudo ufw allow from 10.10.1.4

# clear current ports just in case
sudo ufw delete allow 11211
sudo ufw delete allow 8081
sudo ufw delete allow 6123
sudo ufw delete allow 80
sudo ufw delete allow 443

# mcd port
sudo ufw allow from 10.10.1.1 to any port 11211 proto tcp
sudo ufw allow from 10.10.1.2 to any port 11211 proto tcp
sudo ufw allow from 10.10.1.3 to any port 11211 proto tcp
sudo ufw allow from 10.10.1.4 to any port 11211 proto tcp

# only allow our testing nodes IP to use Flink ports
sudo ufw allow from 10.10.1.1 to any port 8081 proto tcp
sudo ufw allow from 10.10.1.2 to any port 8081 proto tcp
sudo ufw allow from 10.10.1.3 to any port 8081 proto tcp
sudo ufw allow from 10.10.1.4 to any port 8081 proto tcp

sudo ufw allow from 10.10.1.1 to any port 6123 proto tcp
sudo ufw allow from 10.10.1.2 to any port 6123 proto tcp
sudo ufw allow from 10.10.1.3 to any port 6123 proto tcp
sudo ufw allow from 10.10.1.4 to any port 6123 proto tcp

sudo ufw allow from 10.10.1.1 to any port 80 proto tcp
sudo ufw allow from 10.10.1.2 to any port 80 proto tcp
sudo ufw allow from 10.10.1.3 to any port 80 proto tcp
sudo ufw allow from 10.10.1.4 to any port 80 proto tcp

sudo ufw allow from 10.10.1.1 to any port 443 proto tcp
sudo ufw allow from 10.10.1.2 to any port 443 proto tcp
sudo ufw allow from 10.10.1.3 to any port 443 proto tcp
sudo ufw allow from 10.10.1.4 to any port 443 proto tcp

# deny everything else
sudo ufw default allow outgoing
sudo ufw default deny incoming

# enable ufw
echo "y" | sudo ufw enable
sudo ufw status

# disable redundant logging messages
sudo ufw logging off

# setup rapl-service
git clone --recursive https://github.com/handong32/rapl-service.git
pushd rapl-service
./setup.sh
popd

pushd experiment-scripts
git clone --recursive https://github.com/EEStrmCmptng/flink-benchmarks.git

pushd flink-benchmarks
mvn clean package
popd

popd

# enable MSR to set DVFS statically
sudo modprobe msr
# lets run without sudo
sudo setcap cap_sys_rawio=ep /usr/sbin/rdmsr 
sudo setcap cap_sys_rawio=ep /usr/sbin/wrmsr
sudo setcap cap_net_admin+ep /usr/sbin/ethtool

mv /local/repository/experiment-scripts ~/
