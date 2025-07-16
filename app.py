import os
import uuid
import subprocess
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        url = request.form.get("symbol", "").strip()

        if not url:
            message = "❌ Please enter a valid YouTube URL."
            return render_template("index.html", message=message)

        try:
            # Generate unique filename and path
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            # Build yt-dlp command
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", filepath,
                url
            ]

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(result.stderr)

            # Send the downloaded video
            return send_file(
                filepath,
                as_attachment=True,
                download_name="video.mp4",
                mimetype="application/octet-stream"
            )

        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
