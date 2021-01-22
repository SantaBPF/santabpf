#!/bin/bash
< /dev/urandom tr -cd '[:alpha:]' | head -c $1 > $1
