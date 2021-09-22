#!/bin/bash

ROLE=="${1:-child}"

kubectl exec -it $(kubectl get po -l app=netdata,role=$ROLE -o name | cut -d/ -f2) -- bash
