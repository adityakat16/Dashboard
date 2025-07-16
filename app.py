import os
import uuid
import subprocess
import logging
from flask import Flask, render_template, request, send_file, after_this_request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Auto-update yt-dlp to stay ahead of YouTube's fascist bots
try:
    subprocess.run(["yt-dlp", "-U"], check=True)
    logging.info("yt-dlp updated successfully, you sneaky bastard.")
except Exception as e:
    logging.warning(f"Failed to update yt-dlp: {e}.{e}. Proceed at your own risk, dipshit.")

app = Flask(__name__)

# Directory to store downloaded videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure the directory exists

# --- UPDATED: Get cookies content from environment variable ---
# Render will provide this environment variable.
# The content of your youtube_cookies.txt file should be stored here.
COOKIES_CONTENT = os.environ.get("YOUTUBE_COOKIES_CONTENT")
COOKIES_FILE_NAME = "youtube_cookies.txt"  # Name of the file to create dynamically

# Create the cookies file if content is available
if COOKIES_CONTENT:
    try:
        # Create the cookies file in the same directory as the app
        with open(COOKIES_FILE_NAME, "w") as f:
            f.write(COOKIES_CONTENT)
        logging.info(f"Successfully created cookies file: {COOKIES_FILE_NAME}")
    except Exception as e:
        logging.error(f"Error creating cookies file {COOKIES_FILE_NAME}: {e}")
{e}")
        COOKIES_CONTENT = None  # Disable cookies if creation failed
else:
    logging.warning("YOUTUBE_COOKIES_CONTENT environment variable not set. Proceeding without cookies. This may lead to 429 errors.")


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()  # Fixed this shit from "symbol" to "url" – assuming your form uses name="url"

        if not url:
            message = "❌ Please enter a valid YouTube URL, you dumb fuck."
            return render_template("index.html", message=message)

        if "youtube.com/" not in url and "youtu.be/" not in url:
            message = "❌ Please enter a valid YouTube video URL (e.g., from youtube.com or youtu.be), asshole."
            return render_template("index.html", message=message)

        downloaded_filepath = None

        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath

            logging.info(f"Attempting to download URL: {url}{url} to {filepath}")

{filepath}")

            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings",
                "-v",  # Verbose mode to trick detection, you sneaky fuck
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Fake being a normie browser
                "--retries", "infinite",  # Keep hammering like a persistent cocksucker
                "--retry-sleep", "5:10",  # Random delays between 5-10s for retries
                "--max-filesize", "500M"  # Cap at 500MB to avoid server rape
            ]

            # --- Optional Proxy: Set PROXY_URL env var to use (e.g., http://user:pass@proxy.example.com:8080) ---
            proxy_url = os.environ.get("PROXY_URL")
            if proxy_url:
                cmd.extend(["--proxy", proxy_url])
                logging.info(f"Using proxy: {proxy_url} to dodge IP bans, smart move.")
            else:
                logging.warning("No PROXY_URL set. If you get IP-blocked, add one you lazy shit.")

            # --- Use the dynamically created cookies file ---
            if COOKIES_CONTENT and os.path.exists(COOKIES_FILE_NAME):
                cmd.extend(["--cookies", COOKIES_FILE_NAME])
                logging.info(f"Using cookies from: {COOKIES_FILE_NAME}")
            else:
                logging.warning("No valid cookies file found. Downloads may fail due to YouTube's bot detection.")
                # Only show this warning to the user if it wasn't already shown at startup
                if "⚠️ Warning: Cookies file not found" not in message:
                    message = "⚠️ Warning: Cookies not configured. Downloads may fail due to YouTube's bot detection."

            cmd.append(url)

            # --- IMPORTANT: Add a timeout to subprocess.run ---
            # Set a timeout for the yt-dlp process itself (e.g., 10 minutes = 600 seconds)
            # This should be less than or equal to your Gunicorn timeout.
            process_timeout = 600

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=process_timeout  # Add timeout here
            )

            if result.stdout:
                logging.info(f"yt-dlp STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.error(f"yt-dlp STDERR:\n{result.stderr}")

{result.stderr}")

            if result.returncode != 0:
                error_detail = result.stderr.strip() if result.stderr else "Unknown yt-dlp error."
                logging.error(f"yt-dlp failed with return code {result.returncode}: {error_detail}")
{error_detail}")
                raise Exception(f"Video download failed. Details: {error_detail}")

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logging.error(f"yt-dlp reported success but no file or empty file found at {filepath}")
{filepath}")
                raise Exception("Video download failed: File not created or is empty.")

            logging.info(f"Successfully downloaded video to {filepath}")

            @after_this_request
            def remove_file(response):
                try:
                    if downloaded_filepath and os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Cleaned up downloaded file: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up file {downloaded_filepath}: {e}")
{e}")
                return response

            return send_file(
                filepath,
                as_attachment=True,
                download_name="youtube_video.mp4",
                mimetype="video/mp4"
            )

        except FileNotFoundError:
            message = "❌ Error: 'yt-dlp' command not found. Please ensure yt-dlp is installed and in your system's PATH, moron."
            logging.error(message)
        except subprocess.TimeoutExpired:  # Catch specific timeout error from subprocess
            message = f"❌ Error: Video download timed out after {process_timeout} seconds. The video might be too large or the connection too slow, you impatient prick."
            logging.error(message)
            # If a timeout occurs, the process might still be running.
            # It's good practice to terminate it if it didn't finish.
            # This requires storing the process object if you want to terminate it explicitly,
            # but Gunicorn's worker timeout will typically handle this by killing the worker.
            # For simplicity, we just report the error.
            if downloaded_filepath and os.path.exists(downloaded_filepath):
                try:
                    os.remove(downloaded_filepath)  # Clean up partial download
                    logging.info(f"Cleaned up partial download after timeout: {downloaded_filepath}")
{downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up partial file {downloaded_filepath}: {e}")
{e}")
        except Exception as e:
            message = f"❌ An error occurred: {str(e)}{str(e)}"
            logging.error(f"Application error: {e}",{e}", exc_info=True)
        finally:
            if downloaded_filepath and os.path.exists(downloaded_filepath) and not request.routing_exception:
                try:
                    os.remove(downloaded_filepath)
                    logging.info(f"Cleaned up orphaned file due to error: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up orphaned file {downloaded_filepath}: {e}")

{e}")

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
