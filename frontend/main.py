## frontend/main.py
import streamlit as st

st.title("🧠 Generador de Contenido IA")
topic = st.text_input("Tema")
platform = st.selectbox("Plataforma", ["Twitter", "Blog", "Instagram", "LinkedIn"])
audience = st.text_input("Audiencia (ej: adolescentes, marketers...)")

if st.button("Generar"):
    st.write("⚙️ Aquí se mostrará el contenido generado…")