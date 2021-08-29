#!/bin/bash

pushd /etc/ssmtp
envsubst < _ssmtp.conf > ssmtp.conf
popd

sh /usr/sbin/run.sh
