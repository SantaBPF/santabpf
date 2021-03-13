#!/bin/bash

tmpdir=`mktemp -d -t test_santabpf_XXXXX`
tmp=`mktemp -p $tmpdir`
size=$(free -m | awk '/^Mem/{print int($7*0.8)}')

sudo mount -t tmpfs none -o size=${size}M "$tmpdir"

free -h
head -c ${size}M </dev/zero | tr '\0' 1 >$tmp
free -h

echo "$tmp is generated with ${size}MB"
