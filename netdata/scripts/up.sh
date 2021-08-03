#!/usr/bin/env bash
cd "$(dirname "$0")" && cd ..

set -x

eval $(sed -nr '/^image:/{:a; n; h; s/^  (repository|tag): (.+)/SANTABPF_\U\1\E=\2/gp; g; /^ /ba;}' yamls/values.yaml)
DOCKER_IMAGE=$SANTABPF_REPOSITORY:$SANTABPF_TAG
docker build -t $DOCKER_IMAGE ./santabpf && docker push $DOCKER_IMAGE

kubectl apply -f ./yamls/storage-class.yaml

sudo mkdir /mnt/netdata
sudo chown 201:201 /mnt/netdata
kubectl patch storageclass local-storage -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

helm install -f yamls/values.yaml netdata ./chart
kubectl apply -f ./yamls/pv.yaml
