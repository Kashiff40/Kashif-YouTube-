import os
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy import VideoFileClip, vfx

SEARCH_QUERIES = [
    "cricket highlights shorts",
    "football goals shorts",
    "sports moments shorts",
    "best sports highlights",
]


def download_and_edit_video():
    from yt_dlp import YoutubeDL

    for file_name in ("raw_video.mp4", "final_video.mp4"):
        if os.path.exists(file_name):
            os.remove(file_name)

    queries = SEARCH_QUERIES.copy()
    random.shuffle(queries)

    downloaded = False

    for query in queries:
        search_target = f"ytsearch5:{query}"
        print(f"Search aur download ki koshish: {search_target}")

        ydl_opts = {
            # 60 second se choti videos ko tarjeeh (Shorts ke liye behtar)
            "match_filter": lambda info: None
            if (info.get("duration") is None or info.get("duration") <= 90)
            else "Video too long",
            "format": "best[ext=mp4][height<=720]/best[ext=mp4]/best",
            "outtmpl": "raw_video.mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_target])

            if os.path.exists("raw_video.mp4") and os.path.getsize("raw_video.mp4") > 50000:
                downloaded = True
                print(f"Video download ho gayi! Query: {query}")
                break
        except Exception as e:
            print(f"Query '{query}' mein error aayi: {e}")
            if os.path.exists("raw_video.mp4"):
                os.remove("raw_video.mp4")

    if not downloaded or not os.path.exists("raw_video.mp4"):
        raise RuntimeError(
            "Koi bhi sports video download nahi ho saki. Dobara run karke dekhein ya query badlein."
        )

    print("Video editing aur processing shuru...")
    clip = VideoFileClip("raw_video.mp4")

    # Agar clip 55 seconds se lambi ho toh pehle 55 seconds cut karna
    if clip.duration and clip.duration > 55:
        clip = clip.subclipped(0, 55)

    try:
        modified_clip = clip.with_effects([vfx.MultiplySpeed(1.05)])
    except Exception:
        try:
            modified_clip = clip.fx(vfx.speedx, 1.05)
        except Exception:
            modified_clip = clip

    modified_clip.write_videofile(
        "final_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
    )

    clip.close()
    if modified_clip is not clip:
        modified_clip.close()

    print("Video successfully process aur tayar ho chuki hai: final_video.mp4")


def upload_to_youtube():
    print("YouTube par upload ki tayari...")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise ValueError(
            "Error: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, ya YOUTUBE_REFRESH_TOKEN missing hain!"
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": "Trending Sports Highlight #Shorts",
            "description": "Automated sports highlight via Python & GitHub Actions. #sports #shorts #highlights",
            "tags": ["sports", "cricket", "football", "shorts"],
            "categoryId": "17",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload("final_video.mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"Video successfully YouTube par upload ho chuki hai! Video ID: {video_id}")
    print(f"Watch URL: https://www.youtube.com/watch?v={video_id}")


if __name__ == "__main__":
    download_and_edit_video()
    if os.path.exists("final_video.mp4"):
        upload_to_youtube()
