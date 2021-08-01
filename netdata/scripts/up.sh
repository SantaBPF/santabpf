#!/usr/bin/env bash
cd "$(dirname "$0")" && cd ..

set -x

kubectl apply -f ./yamls/storage-class.yaml

sudo mkdir /mnt/netdata
sudo chown 201:201 /mnt/netdata
kubectl patch storageclass local-storage -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

helm install -f values.yaml netdata ./chart
kubectl apply -f ./yamls/pv.yaml
