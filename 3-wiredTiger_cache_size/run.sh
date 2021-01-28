#!/bin/bash

pushd test-app

docker build -t 3-wt_cache_size .

docker run -it --rm -p 5001:27017 --name 3-wt_cache_size 3-wt_cache_size
