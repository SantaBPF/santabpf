#!/bin/bash

mkfifo pipe-wt
mongo <pipe-wt &
exec 3>pipe-wt

echo use datagen_it_test >&3

while true
do
	echo 'db.runCommand({collStats:"test_bson", scale:1024})["wiredTiger"]["cache"]["bytes currently in the cache"]' >&3
	sleep 1
done

