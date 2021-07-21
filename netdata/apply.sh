#!/usr/bin/env bash

set -x

helm upgrade -f values.yaml netdata ./netdata

