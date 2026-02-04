import streamlit as st
import pandas as pd
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Descarga de videos", layout="centered")

st.title("📥 Descarga masiva de videos")
st.write("Sube un archivo Excel con URLs (una por fila) y descarga los videos automáticamente.")

# Subir archivo Excel
uploaded_file = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx", "xls"]
)

if uploaded_file:
    data = pd.read_excel(uploaded_file, header=None)
    st.success(f"Archivo cargado con {len(data)} URLs")

    if st.button("🚀 Iniciar descarga"):
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_path, exist_ok=True)

        progress = st.progress(0)
        status_text = st.empty()

        total = len(data)

        for i, url in enumerate(data[0]):
            try:
                status_text.text(f"Descargando {i+1} de {total}")
                
                response = requests.get(
                    url,
                    headers=headers,
                    verify=False,
                    stream=True,
                    allow_redirects=True,
                    timeout=30
                )

                if response.status_code == 200:
                    filename = f"video_{i+1}.mp4"

                    cd = response.headers.get("Content-Disposition")
                    if cd and "filename=" in cd:
                        filename = cd.split("filename=")[-1].replace('"', '')

                    full_path = os.path.join(downloads_path, filename)

                    with open(full_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    st.write(f"✅ Guardado: {filename}")
                else:
                    st.warning(f"⚠️ Error {response.status_code} en {url}")

            except Exception as e:
                st.error(f"❌ Falló {url}: {e}")

            progress.progress((i + 1) / total)

        st.success("🎉 Descarga finalizada")
