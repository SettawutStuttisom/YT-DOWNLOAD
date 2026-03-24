import streamlit as st
import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("📥 YouTube Multi Downloader")

urls_input = st.text_area("วางลิงก์ YouTube (1 บรรทัดต่อ 1 ลิงก์)")

quality = st.selectbox(
    "เลือกความละเอียด",
    ["best", "1080p", "720p", "480p"]
)

download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

def download_video(url):
    try:
        url = url.strip()
        if not url:
            return None, None

        if quality == "best":
            fmt = "best"
        else:
            fmt = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"

        filename_template = f'{download_path}/%(title).80s_%(id)s.%(ext)s'

        ydl_opts = {
            'format': fmt,
            'outtmpl': filename_template,
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return url, filename

    except Exception as e:
        return url, str(e)

if st.button("🚀 เริ่มดาวน์โหลด"):
    if urls_input.strip() == "":
        st.warning("กรุณาใส่ลิงก์ก่อน")
    else:
        urls = urls_input.split("\n")
        st.info("กำลังดาวน์โหลด...")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(download_video, url) for url in urls]

            for future in futures:
                url, result = future.result()

                if result and os.path.exists(result):
                    st.success(f"✅ โหลดเสร็จ: {url}")

                    with open(result, "rb") as f:
                        st.download_button(
                            label="📥 ดาวน์โหลดไฟล์",
                            data=f,
                            file_name=os.path.basename(result),
                            mime="video/mp4"
                        )
                else:
                    st.error(f"❌ ล้มเหลว: {url} | {result}")

        st.success("เสร็จทั้งหมด!")