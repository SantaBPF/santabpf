#!/bin/bash

export VIRTUALIZATION=$(systemd-detect-virt -v)

docker-compose -p santa up -d --remove-orphans --build
