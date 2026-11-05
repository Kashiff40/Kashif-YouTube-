import os
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

def download_and_edit_video():
    print("Sports video search aur download ki ja rahi hai...")
    search_query = "ytsearch1:trending cricket shorts highlights"
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'raw_video.mp4',
        'noplaylist': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])
    
    print("Video editing aur anti-copyright processing...")
    clip = VideoFileClip("raw_video.mp4")
    # Video ki speed halki si change karna taake copyright match na ho
    modified_clip = clip.fx(vfx.speedx, 1.05)
    modified_clip.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
    print("Video upload ke liye tayar hai!")

if __name__ == "__main__":
    download_and_edit_video()
