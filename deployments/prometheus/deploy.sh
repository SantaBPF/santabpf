#!/bin/bash
docker run -d --name=prometheus --restart unless-stopped -p 19090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
