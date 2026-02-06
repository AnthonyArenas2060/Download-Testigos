import streamlit as st
import pandas as pd
import requests
import urllib3
import os
import zipfile

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Descarga de videos", layout="centered")

st.title("📥 Descarga masiva de videos")
st.write("Sube un archivo Excel con URLs (una por fila) y descarga los videos automáticamente.")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    data = pd.read_excel(uploaded_file, header=None)
    st.success(f"Archivo cargado con {len(data)} URLs")

    if st.button("🚀 Iniciar descarga"):
        headers = {"User-Agent": "Mozilla/5.0"}
        downloads_path = "downloads"
        os.makedirs(downloads_path, exist_ok=True)

        progress = st.progress(0)
        status_text = st.empty()
        downloaded_files = []
        total = len(data)

        for i, url in enumerate(data[0]):
            try:
                status_text.text(f"Descargando {i+1} de {total}")

                r = requests.get(
                    url,
                    headers=headers,
                    verify=False,
                    stream=True,
                    timeout=30
                )

                if r.status_code == 200:
                    filename = f"video_{i+1}.mp4"
                    cd = r.headers.get("Content-Disposition")
                    if cd and "filename=" in cd:
                        filename = cd.split("filename=")[-1].replace('"', '')

                    path = os.path.join(downloads_path, filename)
                    with open(path, "wb") as f:
                        for chunk in r.iter_content(8192):
                            if chunk:
                                f.write(chunk)

                    downloaded_files.append(path)
                else:
                    st.warning(f"⚠️ Error {r.status_code} en {url}")

            except Exception as e:
                st.error(f"❌ Falló {url}: {e}")

            progress.progress((i + 1) / total)

        # Crear ZIP con TODOS los archivos
        zip_path = "videos_descargados.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in downloaded_files:
                zipf.write(f, arcname=os.path.basename(f))

        st.success("🎉 Descarga finalizada")

        # UN SOLO BOTÓN → TODOS LOS ARCHIVOS
        with open(zip_path, "rb") as f:
            st.download_button(
                "⬇️ Descargar TODOS los videos",
                f,
                file_name="videos_descargados.zip",
                mime="application/zip"
            )
