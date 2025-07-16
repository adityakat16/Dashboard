import os
import uuid
from flask import Flask, render_template, request, send_file
from pytube import YouTube

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        url = request.form.get("symbol", "").strip()
        if not url:
            message = "No URL provided."
        else:
            try:
                yt = YouTube(url)
                stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

                filename = f"{uuid.uuid4()}.mp4"
                filepath = os.path.join("downloads", filename)

                os.makedirs("downloads", exist_ok=True)
                stream.download(output_path="downloads", filename=filename)

                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=f"{yt.title}.mp4",
                    mimetype="application/octet-stream"
                )
            except Exception as e:
                message = f"Error: {e}"
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
