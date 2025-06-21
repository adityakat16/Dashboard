#!/usr/bin/env bash

apt-get update && apt-get install -y wget gnupg unzip curl

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Symlink Chrome to PATH
ln -s /usr/bin/google-chrome /usr/local/bin/google-chrome
