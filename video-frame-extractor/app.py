"""Video First Frame Extractor — Streamlit UI."""

import io
import zipfile
import streamlit as st
from pathlib import Path

from extractor import find_videos, extract_first_frame_bytes

st.set_page_config(page_title="First Frame Extractor", page_icon="🎬")
st.title("Video First Frame Extractor")

folder_path = st.text_input("Folder path", placeholder=r"C:\Users\you\Videos\recordings")
fmt = st.radio("Output format", ["jpg", "png"], horizontal=True)

if st.button("Extract", type="primary", disabled=not folder_path):
    input_path = Path(folder_path.strip()).resolve()

    if not input_path.exists():
        st.error(f"Path not found: {input_path}")
    else:
        videos = find_videos(input_path)
        if not videos:
            st.warning("No video files found.")
        else:
            base = input_path if input_path.is_dir() else input_path.parent
            results: list[tuple[str, bytes]] = []
            failed = 0
            progress = st.progress(0, text="Extracting...")

            for i, video in enumerate(videos):
                rel = video.relative_to(base)
                data = extract_first_frame_bytes(video, fmt)
                if data:
                    name = str(rel.with_suffix(f".{fmt}"))
                    results.append((name, data))
                else:
                    failed += 1
                progress.progress((i + 1) / len(videos), text=f"{i + 1}/{len(videos)}")

            progress.empty()
            st.info(f"{len(results)} extracted, {failed} failed")

            if len(results) == 1:
                name, data = results[0]
                st.download_button(f"Download {name}", data, file_name=name,
                                   mime=f"image/{fmt}")
            elif results:
                zip_name = f"{input_path.name}_first_frames.zip"
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for name, data in results:
                        zf.writestr(name, data)
                st.download_button(f"Download {zip_name}", buf.getvalue(),
                                   file_name=zip_name, mime="application/zip")
