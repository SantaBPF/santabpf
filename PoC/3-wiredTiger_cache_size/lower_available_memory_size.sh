#!/bin/bash

rm /tmp/foo/*

while [[ $(free -h | awk '/^Mem/{print $7}' | tr -cd '[0-9]') -gt 100 ]]
do
	dd if=/dev/urandom of=/tmp/foo/1 oflag=append conv=notrunc bs=10M count=1
	free -h
	sleep 0.7
done
