from flask import Flask, render_template, request
from pytube import YouTube

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ""
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path="downloads")  # creates folder in Render
            msg = f"Downloaded: {yt.title}"
        except Exception as e:
            msg = f"Error: {e}"
    return render_template('index.html', message=msg)

if __name__ == '__main__':
    app.run(debug=True)
