#!/bin/bash

cd /tmp

mongod --fork --logpath /var/log/mongodb.log --bind_ip_all

./mgodatagen -f dummy-data.json

tail -f /var/log/mongodb.log
