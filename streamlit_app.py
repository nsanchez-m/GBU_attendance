import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Attendance Log", page_icon="📝", layout="centered")

# --- DISEÑO VISUAL (CSS) ---
st.markdown("""
    <style>
    /* Fondo y fuente general */
    .main {
        background-color: #f9fafb;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Títulos */
    h1 {
        color: #111827;
        font-weight: 800;
        letter-spacing: -0.025em;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Estilo de los inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        padding: 10px;
    }

    /* Estilo del Botón (Primary) */
    .stButton > button {
        width: 100%;
        background-color: #000000;
        color: white;
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #374151;
        border: none;
        color: white;
    }

    /* Estilo de la tabla/dataframe */
    .stDataFrame {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Contenedor tipo Tarjeta */
    .css-1r6slb0 {
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Encabezado visual
st.title("Attendance Log")
st.markdown("<p style='text-align: center; color: #6b7280;'>Registra tu asistencia diaria de forma rápida.</p>", unsafe_allow_html=True)

# Formulario centrado en una "tarjeta"
with st.container():
    nombre_input = st.text_input("Nombre Completo", placeholder="Ej. Juan Pérez")
    col1, col2, col3 = st.columns([1, 2, 1]) # Para centrar el botón
    with col2:
        submit_button = st.button("Check-in ➜")

if submit_button:
    if nombre_input:
        nombre_limpio = nombre_input.strip().upper()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Leer y actualizar (usa la misma lógica que antes)
        df_existente = conn.read(worksheet="Sheet1")
        duplicado = df_existente[(df_existente['Nombre'] == nombre_limpio) & (df_existente['Fecha'] == fecha_hoy)]
        
        if not duplicado.empty:
            st.warning(f"Ya te has registrado hoy, {nombre_limpio.capitalize()}.")
        else:
            nuevo = pd.DataFrame([{"Fecha": fecha_hoy, "Nombre": nombre_limpio, "Asistencia": "X"}])
            df_final = pd.concat([df_existente, nuevo], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df_final)
            st.balloons()
            st.success("¡Registro completado!")
    else:
        st.error("Escribe un nombre para continuar.")

# --- CUADRANTE VISUAL ---
st.markdown("### Historial de Asistencia")
try:
    data = conn.read(worksheet="Sheet1")
    if not data.empty:
        cuadrante = data.pivot_table(index='Nombre', columns='Fecha', values='Asistencia', aggfunc='first').fillna("-")
        st.table(cuadrante) # st.table se ve más "limpio" que st.dataframe para este estilo
except:
    st.info("Aún no hay registros.")
