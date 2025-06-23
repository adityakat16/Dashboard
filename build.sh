#!/usr/bin/env bash
set -o errexit
set -o nounset

echo "🔧 Installing system dependencies..."
apt-get update && apt-get install -y wget unzip curl gnupg2 ca-certificates

echo "📦 Installing Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
google-chrome --version

echo "🔍 Finding Chrome version..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
echo "🧠 Chrome version: $CHROME_VERSION"

echo "📦 Fetching matching ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" \
  | grep -A 6 "\"version\": \"$CHROME_VERSION\"" \
  | grep "linux64" \
  | grep -oP 'https://[^"]+')

if [ -z "$CHROMEDRIVER_VERSION" ]; then
  echo "⚠️ Fallback: Fetching latest ChromeDriver version"
  CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
  wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
else
  echo "🔽 Downloading: $CHROMEDRIVER_VERSION"
  wget -O chromedriver.zip "$CHROMEDRIVER_VERSION"
fi

echo "📦 Installing ChromeDriver..."
unzip chromedriver.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/chromedriver
which chromedriver
chromedriver --version

echo "✅ Setup complete"

pip install -r requirements.txt
