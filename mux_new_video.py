import subprocess
import imageio_ffmpeg
import os

def mux_video():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    v_in = r"docs/Screen Recording 2026-07-31 135021.mp4"
    a_in = r"docs/voiceover_audio/voiceover_full_narration.mp3"
    v_out = r"docs/Zeroclaw_video_voiceover.mp4"

    print("=== Muxing Voiceover Audio with 5-Minute Video ===")
    print(f"Input Video: {v_in}")
    print(f"Input Audio: {a_in}")
    print(f"Output Video: {v_out}")

    cmd = [
        ffmpeg, '-y',
        '-i', v_in,
        '-i', a_in,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        v_out
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(v_out):
        file_size_mb = os.path.getsize(v_out) / (1024 * 1024)
        print(f"[SUCCESS] Created narrated video file: {v_out} ({file_size_mb:.2f} MB)")
    else:
        print(f"[ERROR] Muxing video failed. FFmpeg stderr: {res.stderr}")

if __name__ == "__main__":
    mux_video()
