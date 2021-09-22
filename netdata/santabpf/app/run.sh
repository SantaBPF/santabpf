#!/usr/bin/env bash

if [ "$SANTABPF_ROLE" == "parent" ]
then
  sudo -u netdata uvicorn --port 20000 --host 0.0.0.0 app:app &
fi

exec /usr/sbin/run.sh