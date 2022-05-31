#!/bin/bash

# Kill all running Vagrant boxes
for i in `vagrant global-status | grep virtualbox | awk '{ print $1 }'` ; do vagrant destroy $i ; done

cd /tmp/nso-install

## Extracting version of NSO
NSO_SIGNED_BIN=$(ls nso*signed.bin)
regex="(nso-)([0-9|.]*)"
if [[ $NSO_SIGNED_BIN =~ $regex ]]; then
  NSO_VERSION=$(echo ${BASH_REMATCH[2]} | rev | cut -c 2- | rev)
  NSO_DIR=/opt/ncs-$NSO_VERSION
else
  NSO_DIR=/opt/ncs
fi

## Unpacking NSO
if [ ! -d $NSO_DIR ]; then
  bash $NSO_SIGNED_BIN
  NSO_BIN=$(ls nso*installer.bin)
  bash $NSO_BIN $NSO_DIR --local-install
else
  echo "NSO already unpacked"
fi
source $NSO_DIR/ncsrc


## Installing NSO
NCS_INSTALL_DIR=/opt/ncs-run
if [ ! -f /opt/ncs-run/ncs.conf ]; then
  source $NSO_DIR/ncsrc
  ncs-setup --dest $NCS_INSTALL_DIR
else
  echo "NSO installed"
fi


## Installing NEDs
ncs --stop
cd /tmp/neds
NEDS=$(ls *.signed.bin)
for NED in $NEDS; do
  cd /tmp/neds/
  cp /tmp/neds/$NED /tmp/build
  cd /tmp/build
  bash $NED
  tar zxvf *tar.gz -C /opt/ncs-run/packages
  rm -rf /tmp/build/*
done


## Source and go to directory
echo "source $NSO_DIR/ncsrc" >> /root/.bashrc
echo "cd /opt" >> /root/.bashrc


## Start NSO
cd $NCS_INSTALL_DIR
ncs --with-package-reload-force 


## Setup Netsim, sync-from and check-sync
cd /tmp/netsim
NETSIM=$(ls *.txt)
cp $NETSIM /opt/ncs-run
cd /opt/ncs-run
rm -rf /netsim
NETSIM=$(ls *.txt)
if [ -f $NETSIM ]; then
  ncs-netsim delete-network
  counter=0
  while read device; do
    devices=($device)
      if [[ "$counter" = 0 ]];then
          ncs-netsim create-device /opt/ncs-run/packages/${devices[0]} ${devices[1]}
      else
          ncs-netsim add-device /opt/ncs-run/packages/${devices[0]} ${devices[1]}
      fi
      counter=$((counter +1))
  done <netsim.txt
  ncs-netsim start 
  ncs-netsim ncs-xml-init > devices.xml 
  ncs_load -l -m devices.xml
  echo '  
  <devices xmlns="http://tail-f.com/ns/ncs">
  <device>
    <name>IOS_XR0</name>
    <authgroup>default</authgroup>
    <config>
      <interface xmlns="http://tail-f.com/ned/cisco-ios-xr">
        <GigabitEthernet>
          <id>0/0</id>
        </GigabitEthernet>
        <GigabitEthernet>
          <id>0/1</id>
        </GigabitEthernet>
        <GigabitEthernet>
          <id>0/2</id>
        </GigabitEthernet>
      </interface>
    </config>
  </device>
  <device>
    <name>IOS_XR1</name>
    <authgroup>default</authgroup>
    <config>
      <interface xmlns="http://tail-f.com/ned/cisco-ios-xr">
        <GigabitEthernet>
          <id>0/0</id>
        </GigabitEthernet>
        <GigabitEthernet>
          <id>0/1</id>
        </GigabitEthernet>
        <GigabitEthernet>
          <id>0/2</id>
        </GigabitEthernet>
        <GigabitEthernet>
          <id>0/3</id>
        </GigabitEthernet>
      </interface>
    </config>
  </device>
  </devices>
  ' > xr.xml
  counter=0
  while read device; do
    devices=($device)
      if [[ "${devices[0]}" = "juniper-junos" ]];then
          ncs_cmd -o -c "set /devices/device{"${devices[1]}"}/platform/name junos"
          ncs_cmd -o -c "set /devices/device{"${devices[1]}"}/platform/version 4.2.7"
          ncs_cmd -o -c "set /devices/device{"${devices[1]}"}/platform/model NETSIM"
          ncs_cmd -o -c "set /devices/device{"${devices[1]}"}/platform/serial-number "${devices[1]}
      fi
      counter=$((counter +1))
  done <netsim.txt
  echo "devices sync-from" | ncs_cli -C -u admin
  ncs_load -l -m -u admin xr.xml
  echo "devices check-sync" | ncs_cli -C -u admin
fi


## Keep running with logs
sleep 5
tail -f /opt/ncs-run/logs/ncs.log
