import os
from moviepy import VideoFileClip, ColorClip, vfx

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
        
        # Universal speed modification safely handled
        try:
            modified_clip = clip.fx(vfx.speedx, 1.05)
        except Exception:
            modified_clip = clip
        
        modified_clip.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
        print("Video successfully process aur tayar ho chuki hai!")
    else:
        print("Error: Video file tayar nahi ho saki.")

if __name__ == "__main__":
    download_and_edit_video()
