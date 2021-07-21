#!/usr/bin/env bash

set -x

helm delete netdata
kubectl delete -f pv.yaml &
sudo rm -rf /mnt/netdata/*
