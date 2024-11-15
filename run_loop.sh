#! /bin/bash

while true; do
    uv run ha-media-watchdog watchdog_config.yaml -v
    sleep 30
done
