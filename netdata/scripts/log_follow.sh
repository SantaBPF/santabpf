#!/bin/bash
kubectl logs $(kubectl get po -l app=netdata,role=$1 -o name | cut -d/ -f2) netdata -f
