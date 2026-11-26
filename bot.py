import os
import requests as http_requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy import VideoFileClip, vfx

# YAHAN APNE SPORTS / WORKING VIDEO LINKS DALEIN (aik fail ho toh agla try hoga)
VIDEO_URLS = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
]


def download_with_requests(url: str, output_path: str) -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = http_requests.get(url, headers=headers, stream=True, timeout=60)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "").lower()
    if "text/html" in content_type:
        return False

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    return os.path.exists(output_path) and os.path.getsize(output_path) > 10000


def download_and_edit_video():
    for file_name in ("raw_video.mp4", "final_video.mp4"):
        if os.path.exists(file_name):
            os.remove(file_name)

    downloaded = False

    for url in VIDEO_URLS:
        print(f"Video download ki koshish: {url}")

        # Pehle yt_dlp se try karna
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": "raw_video.mp4",
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True,
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    )
                },
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists("raw_video.mp4") and os.path.getsize("raw_video.mp4") > 10000:
                downloaded = True
                print("yt_dlp se video download ho gayi!")
                break
        except Exception as e:
            print(f"yt_dlp error ({url}): {e}")

        # Agar yt_dlp fail ho toh direct requests se try karna
        try:
            if download_with_requests(url, "raw_video.mp4"):
                downloaded = True
                print("Direct download se video mil gayi!")
                break
        except Exception as e:
            print(f"Direct download error ({url}): {e}")

    if not downloaded or not os.path.exists("raw_video.mp4"):
        raise RuntimeError(
            "Koi bhi video download nahi ho saki. VIDEO_URLS mein valid/accessible video links dalein."
        )

    print("Video editing aur processing shuru...")
    clip = VideoFileClip("raw_video.mp4")

    # Agar video 60 seconds se lambi ho toh pehle 55 seconds lein (Shorts/quick clip ke liye)
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
            "title": "Automated Sports Highlight #Shorts",
            "description": "Generated automatically via Python & GitHub Actions. #sports #highlights #shorts",
            "tags": ["sports", "highlights", "shorts"],
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
