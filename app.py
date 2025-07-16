import os
import uuid
import subprocess
import logging
from flask import Flask, render_template, request, send_file, after_this_request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Directory to store downloaded videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True) # Ensure the directory exists

# --- NEW: Path to your YouTube cookies file ---
# You will need to create this file on your server.
# See instructions below on how to get your cookies.
# If you don't want to use cookies, you can set this to None or an empty string.
COOKIES_FILE = "youtube_cookies.txt" 
# Ensure the cookies file path is absolute or relative to where app.py is run
# Example: COOKIES_FILE = "/path/to/your/youtube_cookies.txt"
# For this example, we assume it's in the same directory as app.py

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        # Get the URL from the form, strip whitespace
        url = request.form.get("symbol", "").strip()

        if not url:
            message = "❌ Please enter a valid YouTube URL."
            return render_template("index.html", message=message)

        # Basic URL validation (you might want more robust validation)
        if "youtube.com/" not in url and "youtu.be/" not in url:
            message = "❌ Please enter a valid YouTube video URL."
            return render_template("index.html", message=message)

        downloaded_filepath = None # Initialize to None

        try:
            # Generate a unique filename for the downloaded video
            # Using uuid to prevent conflicts and make filenames unpredictable
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            downloaded_filepath = filepath # Store for cleanup

            logging.info(f"Attempting to download URL: {url} to {filepath}")

            # Build the yt-dlp command
            # -f best[ext=mp4]/best: Prioritize best quality MP4, fallback to best available
            # -o filepath: Output the file to the specified path
            # --no-warnings: Suppress non-critical warnings from yt-dlp
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                "--no-warnings", # Suppress warnings to keep stderr cleaner for error checking
            ]

            # --- NEW: Add cookies argument if COOKIES_FILE is specified and exists ---
            if COOKIES_FILE and os.path.exists(COOKIES_FILE):
                cmd.extend(["--cookies", COOKIES_FILE])
                logging.info(f"Using cookies from: {COOKIES_FILE}")
            elif COOKIES_FILE and not os.path.exists(COOKIES_FILE):
                logging.warning(f"Cookies file not found at {COOKIES_FILE}. Proceeding without cookies. This may lead to 429 errors.")

            cmd.append(url) # Add the URL at the end

            # Execute the yt-dlp command
            # capture_output=True: Captures stdout and stderr
            # text=True: Decodes stdout and stderr as text
            # check=False: Do not raise CalledProcessError for non-zero exit codes; we handle it manually
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            # Log yt-dlp's stdout and stderr for debugging
            if result.stdout:
                logging.info(f"yt-dlp STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.error(f"yt-dlp STDERR:\n{result.stderr}")

            # Check if yt-dlp command was successful
            if result.returncode != 0:
                # If yt-dlp failed, raise an exception with its error output
                error_detail = result.stderr.strip() if result.stderr else "Unknown yt-dlp error."
                logging.error(f"yt-dlp failed with return code {result.returncode}: {error_detail}")
                raise Exception(f"Video download failed. Details: {error_detail}")

            # Check if the file was actually created
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logging.error(f"yt-dlp reported success but no file or empty file found at {filepath}")
                raise Exception("Video download failed: File not created or is empty.")

            logging.info(f"Successfully downloaded video to {filepath}")

            # Use after_this_request to clean up the file once the response is sent
            @after_this_request
            def remove_file(response):
                try:
                    if downloaded_filepath and os.path.exists(downloaded_filepath):
                        os.remove(downloaded_filepath)
                        logging.info(f"Cleaned up downloaded file: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up file {downloaded_filepath}: {e}")
                return response

            # Send the downloaded video file to the user
            # as_attachment=True: Forces browser to download the file
            # download_name: Suggested filename for the user's download
            # mimetype: Specifies the file type
            return send_file(
                filepath,
                as_attachment=True,
                download_name="youtube_video.mp4", # You can make this dynamic based on video title
                mimetype="video/mp4" # More specific MIME type for MP4 videos
            )

        except FileNotFoundError:
            message = "❌ Error: 'yt-dlp' command not found. Please ensure yt-dlp is installed and in your system's PATH."
            logging.error(message)
        except Exception as e:
            # Catch any other exceptions during the process
            message = f"❌ An error occurred: {str(e)}"
            logging.error(f"Application error: {e}", exc_info=True)
        finally:
            # This block is crucial for cleanup if an error occurs BEFORE send_file
            # If send_file is called, @after_this_request handles cleanup.
            # This handles cases where download_filepath was set, but an error prevented send_file.
            if downloaded_filepath and os.path.exists(downloaded_filepath) and not request.routing_exception:
                # Only clean up here if the file wasn't sent (i.e., an error occurred before send_file)
                # request.routing_exception check is a heuristic to avoid double-cleanup if send_file fails internally
                try:
                    os.remove(downloaded_filepath)
                    logging.info(f"Cleaned up orphaned file due to error: {downloaded_filepath}")
                except Exception as e:
                    logging.error(f"Error cleaning up orphaned file {downloaded_filepath}: {e}")


    # Render the index page with any messages
    return render_template("index.html", message=message)

if __name__ == "__main__":
    # In a production environment, you would use a WSGI server like Gunicorn or uWSGI
    # debug=True is good for development but should be False in production
    app.run(debug=True, host='0.0.0.0', port=5000) # Listen on all interfaces
