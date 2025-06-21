echo "Checking Chrome install..."
google-chrome --version || echo "Chrome not found"

echo "Checking Chromedriver install..."
ls -l /usr/bin/chromedriver || echo "Chromedriver not found"
