import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Asistencia 2026", layout="wide")

st.title("📝 Registro de Asistencia")

# 1. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Formulario de Registro
with st.form(key="registro_form"):
    nombre_input = st.text_input("Escribe tu nombre completo:")
    submit_button = st.form_submit_button(label="Registrar Asistencia")

if submit_button:
    if nombre_input:
        # Limpieza de datos (SOLID: Responsabilidad única)
        nombre_limpio = nombre_input.strip().upper()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Leer datos actuales
        df_existente = conn.read(worksheet="Sheet1")
        
        # Verificar duplicados hoy
        duplicado = df_existente[(df_existente['Nombre'] == nombre_limpio) & 
                                 (df_existente['Fecha'] == fecha_hoy)]
        
        if not duplicado.empty:
            st.warning(f"⚠️ {nombre_limpio}, ya te registraste hoy.")
        else:
            # Añadir nuevo registro
            nuevo_registro = pd.DataFrame([{"Fecha": fecha_hoy, "Nombre": nombre_limpio, "Asistencia": "X"}])
            df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df_actualizado)
            st.success(f"✅ ¡Asistencia registrada para {nombre_limpio}!")
    else:
        st.error("Por favor, escribe un nombre.")

# --- SECCIÓN DEL CUADRANTE ---
st.divider()
st.subheader("📊 Cuadrante de Asistencia Anual")

try:
    data = conn.read(worksheet="Sheet1")
    if not data.empty:
        # Crear el pivot table (el ajuste automático)
        cuadrante = data.pivot_table(
            index='Nombre', 
            columns='Fecha', 
            values='Asistencia', 
            aggfunc='first'
        ).fillna("")
        
        st.dataframe(cuadrante)
        
        # Botón para descargar a Excel
        st.download_button(
            label="📥 Descargar Reporte en Excel",
            data=cuadrante.to_csv().encode('utf-8'),
            file_name=f"asistencia_{datetime.now().strftime('%Y')}.csv",
            mime="text/csv"
        )
except Exception as e:
    st.info("Aún no hay registros para mostrar el cuadrante.")
