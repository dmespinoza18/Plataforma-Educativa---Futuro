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
        cap_index = st.session_state.get("cap_index", 0)
        cap = st.selectbox("Selecciona un capítulo o módulo:", capitulos, index=cap_index, key="cap_selector")

        texto_completo = cargar_texto(seleccionado, cap)

        st.markdown(f"### 📖 Contenido de {cap.replace('_', ' ').title()}")

        if texto_completo.strip():
            # PAGINACIÓN DEL TEXTO
            paginas = [p.strip() for p in texto_completo.split('---')]
            num_paginas = len(paginas)
            pagina_actual = st.number_input("Página", min_value=1, max_value=num_paginas, value=1, step=1)

            st.markdown("#### 📄 Página del capítulo:")
            st.write(paginas[pagina_actual - 1])

            # AUDIO
            if st.button("🔊 Escuchar esta página"):
                from gtts import gTTS
                from tempfile import NamedTemporaryFile
                with st.spinner("Generando audio..."):
                    tts = gTTS(paginas[pagina_actual - 1], lang="es")
                    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                        tts.save(tmpfile.name)
                        st.audio(tmpfile.name, format="audio/mp3")
        else:
            st.warning("Este capítulo no tiene texto aún.")

        # QUIZ
        quiz = cargar_quiz(seleccionado, cap)
        if quiz:
            st.markdown("### 🧠 Quiz del capítulo")
            score = 0
            for pregunta, opciones in quiz.items():
                respuesta = st.radio(pregunta, opciones, key=pregunta)
                if respuesta == opciones[0]:
                    score += 1
            st.success(f"Puntaje: {score}/{len(quiz)}")

        # BOTÓN IR AL SIGUIENTE CAPÍTULO
        cap_actual_idx = capitulos.index(cap)
        if cap_actual_idx < len(capitulos) - 1:
            if st.button("➡️ Ir al siguiente capítulo"):
                st.session_state["cap_index"] = cap_actual_idx + 1
                st.experimental_rerun()
    else:
        st.warning("Este curso aún no tiene capítulos.")
