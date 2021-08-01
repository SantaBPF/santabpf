#!/usr/bin/env bash
cd "$(dirname "$0")" && cd ..

set -x

helm delete netdata
kubectl delete -f ./yamls/pv.yaml &
sudo rm -rf /mnt/netdata/*
