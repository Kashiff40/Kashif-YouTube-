import os
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, vfx

def download_and_edit_video():
    print("Video download ki ja rahi hai...")
    # Ek stable sample public video ka link taake download mein error na aaye
    video_url = "https://www.youtube.com/watch?v=BaW_jenozKc"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'raw_video.mp4',
        'noplaylist': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    if os.path.exists("raw_video.mp4"):
        print("Video editing aur anti-copyright processing...")
        clip = VideoFileClip("raw_video.mp4")
        
        # Video ki speed halki si change karna taake unique ho jaye
        modified_clip = clip.with_speed_fx(1.05)
        
        modified_clip.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
        print("Video upload ke liye tayar hai!")
    else:
        print("Error: Video file download nahi ho saki.")

if __name__ == "__main__":
    download_and_edit_video()
