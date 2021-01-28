#!/bin/bash -x

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# safety logic
trap 'tc qdisc del dev eth0 root; rm 32M; exit' INT

pushd test-app

# for generating high load
sh gen_dummy_data.sh 32M
docker build -t 2-httpd_max_clients .

# tc for emulating tcp congestion
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
docker run -it --rm --name 2-httpd_max_clients -p 5001:80 2-httpd_max_clients
tc qdisc del dev eth0 root
rm ./32M
