from pytube import YouTube

def download_youtube_video(url, path="."):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()  # You can choose audio-only or lower resolution too
        print(f"Downloading: {yt.title}")
        stream.download(output_path=path)
        print("Download completed!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
video_url = input("Enter YouTube video URL: ")
download_youtube_video(video_url)
