#!/bin/bash

for f in /usr/sbin/*-bpfcc; do sudo ln $f ${f%-bpfcc}; done
