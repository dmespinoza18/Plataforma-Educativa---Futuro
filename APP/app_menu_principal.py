import streamlit as st
import os
import json

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENIDOS_DIR = os.path.join(BASE_DIR, "contenidos")

st.set_page_config(page_title="📚 Plataforma Educativa", layout="centered")
st.title("📚 Plataforma Educativa Interactiva")

# --- FUNCIONES ---
def obtener_cursos():
    if not os.path.exists(CONTENIDOS_DIR):
        return []
    return sorted([
        d for d in os.listdir(CONTENIDOS_DIR)
        if os.path.isdir(os.path.join(CONTENIDOS_DIR, d))
    ])

def cargar_descripcion(curso):
    path = os.path.join(CONTENIDOS_DIR, curso, "descripcion.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Sin descripción disponible."

def obtener_capitulos(curso):
    curso_path = os.path.join(CONTENIDOS_DIR, curso)
    return sorted([
        d for d in os.listdir(curso_path)
        if os.path.isdir(os.path.join(curso_path, d))
    ])

def cargar_texto(curso, capitulo):
    path = os.path.join(CONTENIDOS_DIR, curso, capitulo, "texto.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def cargar_quiz(curso, capitulo):
    path = os.path.join(CONTENIDOS_DIR, curso, capitulo, "quiz.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- INTERFAZ PRINCIPAL ---
cursos = obtener_cursos()
if not cursos:
    st.warning("No se encontraron cursos o libros en la carpeta /contenidos/.")
else:
    seleccionado = st.selectbox("Selecciona un curso o libro:", cursos)
    st.subheader(f"📘 {seleccionado.replace('_', ' ').title()}")
    st.info(cargar_descripcion(seleccionado))

    capitulos = obtener_capitulos(seleccionado)
    if capitulos:
        cap = st.selectbox("Selecciona un capítulo o módulo:", capitulos)
        texto = cargar_texto(seleccionado, cap)
        
        st.markdown(f"### 📖 Contenido de {cap.replace('_', ' ').title()}")

        # CONTENEDOR CON SCROLL QUE INCLUYE AUDIO Y QUIZ
        st.markdown(
            f"""
            <div style="height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 1rem; border-radius: 8px; background-color: #f9f9f9; margin-bottom: 1rem;">
                <p style="white-space: pre-wrap;">{texto}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Botón de audio fuera del bloque HTML (por temas de funcionalidad)
        if st.button("🔊 Escuchar contenido"):
            from gtts import gTTS
            from tempfile import NamedTemporaryFile
            with st.spinner("Generando audio..."):
                tts = gTTS(texto, lang="es")
                with NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                    tts.save(tmpfile.name)
                    st.audio(tmpfile.name, format="audio/mp3")

        # Cargar quiz si existe
        quiz = cargar_quiz(seleccionado, cap)
        if quiz:
            st.markdown("### 🧠 Quiz del capítulo")
            score = 0
            for pregunta, opciones in quiz.items():
                respuesta = st.radio(pregunta, opciones, key=pregunta)
                if respuesta == opciones[0]:
                    score += 1
            st.success(f"Puntaje: {score}/{len(quiz)}")
    else:
        st.warning("Este curso aún no tiene capítulos.")
