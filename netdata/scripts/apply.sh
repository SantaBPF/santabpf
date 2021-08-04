#!/usr/bin/env bash
cd "$(dirname "$0")" && cd ..

set -x

eval $(sed -nr '/^image:/{:a; n; h; s/^  (repository|tag): (.+)/SANTABPF_\U\1\E=\2/gp; g; /^ /ba;}' yamls/values.yaml)
DOCKER_IMAGE=$SANTABPF_REPOSITORY:$SANTABPF_TAG
docker build -t $DOCKER_IMAGE ./santabpf && docker push $DOCKER_IMAGE

helm upgrade -f ./yamls/values.yaml netdata ./chart
kubectl rollout restart daemonset netdata-child
kubectl get po -w
