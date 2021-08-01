#!/usr/bin/env bash
cd "$(dirname "$0")" && cd ..

set -x

helm upgrade -f ./yamls/values.yaml netdata ./chart
kubectl get po -w
