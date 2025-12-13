import streamlit as st
import pandas as pd
import requests
import time
import os
import plotly.express as px

from dotenv import load_dotenv
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Monitor IoT", layout="wide")

st.title("Centro de Control Industrial - IoT")

st.sidebar.header("🔐 Autenticación")
default_user = os.getenv("GUEST_USER", "guest")
default_pass = os.getenv("GUEST_PASSWORD", "")

usuario = st.sidebar.text_input("Usuario", value=default_user)
password = st.sidebar.text_input("Contraseña", value=default_pass, type="password")
refresh_rate = st.sidebar.slider("Actualizar cada (segundos)", 1, 10, 2)

API_URL = "http://127.0.0.1:8000/data"

placeholder = st.empty()

while True:
    try:
        response = requests.get(
            API_URL, 
            params={"limit": 50},
            auth=(usuario, password),
            timeout=2
        )
        
        with placeholder.container():
            if response.status_code == 401:
                st.error("Acceso Denegado: Credenciales incorrectas.")
                st.stop()
            
            elif response.status_code == 200:
                data = response.json()
                
                if not data:
                    st.warning("La API está vacía.")

                else:
                    df = pd.DataFrame(data)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    ultimo_dato = df.iloc[-1]
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Temperatura", f"{ultimo_dato['temperature']} °C", delta_color="inverse")

                    if 'cpu' in df.columns:
                        col2.metric("Uso CPU", f"{ultimo_dato['cpu']}%")
                        col3.metric("Latencia", f"{ultimo_dato['latency']} ms")
                        st.success(f"🔓 Modo: ADMINISTRADOR - Mostrando telemetría completa")
                    else:
                        st.info(f"👤 Modo: VISITA - Vista restringida")

                    color_linea = "navy" if 'cpu' in df.columns else "green"

                    fig = px.line(
                        df, 
                        x="timestamp", 
                        y="temperature",
                        title="Evolución Térmica en Vivo",
                        labels={"timestamp": "Hora", "temperature": "Temperatura (°C)"}
                    )

                    fig.update_traces(
                        line_color=color_linea,
                        mode="lines+markers",
                        marker=dict(size=8, color="cyan", line=dict(width=1, color="white"))
                    )

                    fig.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20),
                        hovermode="x unified"
                    )

                    st.plotly_chart(
                        fig, 
                        use_container_width=True, 
                        key=f"chart_{time.time()}"
                    )

            else:
                st.error(f"Error desconocido: {response.status_code}")
        time.sleep(refresh_rate)

    except Exception as e:
        with placeholder.container():
            st.error(f"No se puede conectar a la API: {e}")
            st.warning("¿Está corriendo 'main.py'?")
        time.sleep(5)