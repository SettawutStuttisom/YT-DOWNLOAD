import streamlit as st
import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="YouTube Downloader", layout="centered")

st.title("📥 YouTube Multi Downloader")

# รับลิงก์หลายตัว
urls_input = st.text_area("วางลิงก์ YouTube (1 บรรทัดต่อ 1 ลิงก์)")

quality = st.selectbox(
    "เลือกความละเอียด",
    ["best", "1080p", "720p", "480p"]
)

download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

# ฟังก์ชันดาวน์โหลด
def download_video(url):
    try:
        if quality == "best":
            fmt = "best"
        else:
            fmt = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"

        ydl_opts = {
            'format': fmt,
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return f"✅ สำเร็จ: {url}"

    except Exception as e:
        return f"❌ ล้มเหลว: {url} | {str(e)}"

# ปุ่มเริ่ม
if st.button("🚀 เริ่มดาวน์โหลด"):
    if urls_input.strip() == "":
        st.warning("กรุณาใส่ลิงก์ก่อน")
    else:
        urls = urls_input.split("\n")

        st.info("กำลังดาวน์โหลด...")

        results = []

        # โหลดพร้อมกัน (ปรับจำนวน thread ได้)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(download_video, url) for url in urls]

            for future in futures:
                result = future.result()
                results.append(result)
                st.write(result)

        st.success("ดาวน์โหลดครบแล้ว!")