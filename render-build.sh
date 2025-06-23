#!/usr/bin/env bash
set -o errexit

apt-get update && apt-get install -y wget unzip curl gnupg2

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Get full Chrome version (like 124.0.6367.207)
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
echo "Chrome version: $CHROME_VERSION"

# Get matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "Matching ChromeDriver version: $CHROMEDRIVER_VERSION"

# Fallback if matching version not found
if [ -z "$CHROMEDRIVER_VERSION" ]; then
  echo "Falling back to default ChromeDriver version"
  CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
fi

# Download and install ChromeDriver
wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/chromedriver

echo "ChromeDriver installed at: $(which chromedriver)"
echo "Chrome installed at: $(which google-chrome)"

# Install Python packages
pip install -r requirements.txt
