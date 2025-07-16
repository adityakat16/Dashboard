import os
import uuid
from flask import Flask, render_template, request, send_file
from pytube import YouTube

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join("/tmp", filename)
            stream.download(output_path="/tmp", filename=filename)

            # Send the file as an attachment so mobile prompts "Download"
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"{yt.title}.mp4",
                mimetype="video/mp4"
            )
        except Exception as e:
            message = f"Error: {e}"
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
