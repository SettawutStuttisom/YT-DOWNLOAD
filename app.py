import streamlit as st
import yt_dlp
import os
import zipfile
import shutil
import imageio_ffmpeg

st.set_page_config(page_title="YouTube Playlist Downloader", layout="centered")
st.title("📥 YouTube Playlist → ZIP")

playlist_url = st.text_input("วางลิงก์ Playlist YouTube")

download_type = st.radio(
    "เลือกประเภทไฟล์",
    ["🎬 วิดีโอ (MP4)", "🎵 เสียง (MP3)"]
)

quality = st.selectbox(
    "เลือกความละเอียด (เฉพาะวิดีโอ)",
    ["best", "1080p", "720p", "480p"]
)

download_path = "downloads"

# 🔥 ล้างโฟลเดอร์ก่อนโหลดใหม่
def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

if st.button("🚀 ดาวน์โหลดและสร้าง ZIP"):

    if playlist_url.strip() == "":
        st.warning("กรุณาใส่ลิงก์ Playlist")
    else:
        clear_folder(download_path)

        progress = st.progress(0)
        status = st.empty()

        # 🔥 progress
        def progress_hook(d):
            if d['status'] == 'downloading':
                status.text("📥 กำลังดาวน์โหลด...")
                progress.progress(50)
            elif d['status'] == 'finished':
                progress.progress(80)

        try:
            # =========================
            # 🎬 VIDEO MODE
            # =========================
            if download_type == "🎬 วิดีโอ (MP4)":

                if quality == "best":
                    fmt = "best"
                else:
                    fmt = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"

                ydl_opts = {
                    'format': fmt,
                    'outtmpl': f'{download_path}/%(playlist_index)s_%(title).80s_%(id)s.%(ext)s',
                    'ignoreerrors': True,
                    'progress_hooks': [progress_hook],
                }

            # =========================
            # 🎵 AUDIO MODE (MP3 จริง)
            # =========================
            else:
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'ffmpeg_location': ffmpeg_path,
                    'outtmpl': f'{download_path}/%(playlist_index)s_%(title).80s_%(id)s.%(ext)s',
                    'ignoreerrors': True,
                    'progress_hooks': [progress_hook],

                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

            # 🔥 ดาวน์โหลด
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([playlist_url])

            status.text("✅ ดาวน์โหลดเสร็จแล้ว")
            progress.progress(90)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()

        # =========================
        # 📦 ZIP FILE
        # =========================
        zip_path = os.path.join(download_path, "playlist.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)

                if file_path != zip_path:
                    zipf.write(file_path, file)

        # 🔥 ลบไฟล์ทั้งหมด เหลือแค่ ZIP
        for file in os.listdir(download_path):
            file_path = os.path.join(download_path, file)

            if file_path != zip_path:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass

        progress.progress(100)
        status.text("📦 สร้าง ZIP และลบไฟล์เรียบร้อย!")

        # =========================
        # ⬇️ DOWNLOAD BUTTON
        # =========================
        with open(zip_path, "rb") as f:
            st.download_button(
                label="⬇️ ดาวน์โหลด ZIP",
                data=f,
                file_name="playlist.zip",
                mime="application/zip"
            )

        st.success("🎉 เสร็จสมบูรณ์!")