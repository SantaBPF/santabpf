#!/bin/bash

trap 'kill $(cat /tmp/dd_pid); exit' INT

while :
do
	(dd if=/dev/urandom & echo $! >&3) 3>/tmp/dd_pid | bzip2 -9 >> /dev/null &
	sleep 0.9

	kill $(cat /tmp/dd_pid)
	sleep 2
done
