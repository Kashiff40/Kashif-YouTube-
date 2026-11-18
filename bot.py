import os
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, vfx

def download_and_edit_video():
    print("Public video download ki ja rahi hai...")
    # Wikimedia Commons ki 100% working aur permanent public video link
    video_url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c4/BBH_Mozart_Violin_Concerto_No_4_3rd_movement.ogg/BBH_Mozart_Violin_Concerto_No_4_3rd_movement.ogg.480p.vp9.webm"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'raw_video.mp4',
        'noplaylist': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    if os.path.exists("raw_video.mp4"):
        print("Video editing aur processing...")
        clip = VideoFileClip("raw_video.mp4")
        
        # Video ki speed modify karna
        modified_clip = clip.with_speed_fx(1.05)
        
        modified_clip.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")
        print("Video successfully process ho chuki hai!")
    else:
        print("Error: Video file download nahi ho saki.")

if __name__ == "__main__":
    download_and_edit_video()
