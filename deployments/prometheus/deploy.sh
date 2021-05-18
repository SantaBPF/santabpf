#!/bin/bash
docker run -d --name=prometheus --restart unless-stopped -p 19090:9090 -v $(pwd):/etc/prometheus prom/prometheus
