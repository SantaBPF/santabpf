#!/usr/bin/env bash

set -x

kubectl apply -f storage-class.yaml

sudo mkdir /mnt/netdata
sudo chown 201:201 /mnt/netdata
kubectl patch storageclass local-storage -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

helm install -f values.yaml netdata ./netdata
kubectl apply -f pv.yaml
