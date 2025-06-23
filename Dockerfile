# Use a lightweight base image with Python and required libs
FROM python:3.11-slim

# Disable prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    ca-certificates fonts-liberation \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils --no-install-recommends && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install a specific ChromeDriver version (matching Chrome 125+)
RUN CHROMEDRIVER_VERSION=125.0.6422.112 && \
    wget -q -O chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver.zip && mv chromedriver /usr/local/bin/ && chmod +x /usr/local/bin/chromedriver && rm chromedriver.zip

# Set display env for headless Chrome
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["gunicorn", "app:app"]
