#!/usr/bin/env bash

apt-get update && \
apt-get install -y chromium chromium-driver

# Optional: confirm chromium is installed
which chromium
