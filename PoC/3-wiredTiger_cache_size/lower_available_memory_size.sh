#!/bin/bash

mkdir -p /tmp/foo
sudo mount -t tmpfs none -o size=$(free -m | awk '/^Mem/{print $7}')M /tmp/foo

rm -f /tmp/foo/*

while [[ $(free -m | awk '/^Mem/{print $7}' | tr -cd '[0-9]') -gt 100 ]]
do
	dd if=/dev/urandom of=/tmp/foo/1 oflag=append conv=notrunc bs=90M count=1
	free -h
	sleep 0.2
done
