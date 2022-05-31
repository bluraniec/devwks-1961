#!/bin/bash
for i in `vagrant global-status | grep virtualbox | awk '{ print $1 }'` ; do vagrant destroy $i ; done
docker container stop $(docker container ls -aq)
docker-compose rm -f
docker-compose down
cd nso
rm -rf ncs-run
mkdir ncs-run
cd ..
docker-compose build
docker-compose up --force-recreate