#!/bin/bash

kubectl logs $(kubectl get po -l app=netdata,role=parent -o name | cut -d/ -f2) netdata | grep -iw --color $1
kubectl logs $(kubectl get po -l app=netdata,role=child -o name | cut -d/ -f2) netdata | grep -iw --color $1
