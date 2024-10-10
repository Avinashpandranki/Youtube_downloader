from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import yt_dlp
import re

app = FastAPI()

# Enhanced YouTube URL validation regex
YOUTUBE_URL_REGEX = (
    r'^(https?://)?(www\.)?'
    r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
    r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
)

@app.post("/download", response_class=HTMLResponse)
async def download_youtube_video(url: str = Form(...)):
    # Validate URL format
    if not re.match(YOUTUBE_URL_REGEX, url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format")

    # Set options for yt-dlp with fallback formats
    ydl_opts = {
        'format': 'best',  # Try the best format first
        'outtmpl': '%(id)s.%(ext)s',  # Save file as video ID
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get information about available formats
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", None)
            
            if not formats:
                raise HTTPException(status_code=400, detail="No available formats for this video")
            
            # Safely access 'format_note' and handle missing values
            available_formats = "\n".join(
                [f"{f['format_id']} - {f.get('format_note', 'Unknown')}" for f in formats]
            )

            try:
                # Attempt to download the best available format
                ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                # If the 'best' format is not available, list the formats
                raise HTTPException(
                    status_code=400, 
                    detail=f"Requested format is not available. Available formats:\n{available_formats}"
                )

            return f"<h1>Download complete! Video saved as: {info.get('title')}</h1>"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>YouTube Downloader</title>
        </head>
        <body>
            <h1>YouTube Video Downloader</h1>
            <form action="/download" method="post">
                <label for="url">Enter YouTube Video URL:</label><br>
                <input type="text" id="url" name="url" required><br><br>
                <button type="submit">Download Video</button>
            </form>
        </body>
    </html>
    """
