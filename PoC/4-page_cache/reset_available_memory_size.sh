#!/bin/bash

sudo umount /tmp/test_santabpf* || true
rm -rf /tmp/test_santabpf* || true
free -h
