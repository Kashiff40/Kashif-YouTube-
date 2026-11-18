import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy import VideoFileClip, ColorClip, vfx

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def create_fallback_video():
    print("Fallback video generate ki ja rahi hai...")
    clip = ColorClip(size=(720, 1280), color=(0, 128, 255), duration=5)
    clip.write_videofile("raw_video.mp4", fps=24, codec="libx264", audio_codec="aac")

def download_and_edit_video():
    try:
        from yt_dlp import YoutubeDL
        print("Video download ki koshish ki ja rahi hai...")
        video_url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c4/BBH_Mozart_Violin_Concerto_No_4_3rd_movement.ogg/BBH_Mozart_Violin_Concerto_No_4_3rd_movement.ogg.480p.vp9.webm"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'raw_video.mp4',
            'noplaylist': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"Download mein error aayi: {e}")
        create_fallback_video()
    
    if os.path.exists("raw_video.mp4"):
        print("Video editing aur processing...")
        clip = VideoFileClip("raw_video.mp4")
        
        try:
            modified_clip = clip.fx(vfx.speedx, 1.05)
        except Exception:
            modified_clip = clip
        
        modified_clip.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
        print("Video successfully process aur tayar ho chuki hai!")
    else:
        print("Error: Video file tayar nahi ho saki.")

def upload_to_youtube():
    print("YouTube par upload ki tayari...")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    
    # Credentials check
    if not client_id or not client_secret:
        print("Error: YouTube Secrets missing hain!")
        return

    # Temporary client_secret.json file generate karna authentication ke liye
    client_secret_content = f"""
    {{"installed": {{"client_id": "{client_id}", "project_id": "youtube-bot", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "{client_secret}", "redirect_uris": ["http://localhost"]}}}}
    """
    with open("client_secret.json", "w") as f:
        f.write(client_secret_content)

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            # Server environment ke liye token generate karne ka setup
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': 'Automated Sports Highlight',
            'description': 'Generated automatically via Python & GitHub Actions.',
            'tags': ['sports', 'cricket', 'shorts'],
            'categoryId': '17' # Sports category ID
        },
        'status': {
            'privacyStatus': 'public' # Aap 'private' ya 'unlisted' bhi rakh sakte hain
        }
    }

    media = MediaFileUpload('final_video.mp4', chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading progress: {int(status.progress() * 100)}%")
    
    print("Video successfully YouTube par upload ho chuki hai!")

if __name__ == "__main__":
    download_and_edit_video()
    if os.path.exists("final_video.mp4"):
        upload_to_youtube()
