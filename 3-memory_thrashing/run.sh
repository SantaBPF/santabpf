#!/bin/bash

pushd test-app

docker build -t 3-memory_thrashing .

docker run -it --rm -p 5001:27017 --name 3-memory_thrashing 3-memory_thrashing
