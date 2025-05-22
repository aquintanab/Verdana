
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.express as px
import numpy as np

from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Configuración de página
st.set_page_config(page_title="🌿 Verdana – Naturaleza que te escucha", layout="wide")

# Título principal
st.markdown("## 🌿 Verdana – Naturaleza que te escucha")
st.markdown("Bienvenido al sistema interactivo de monitoreo de microcultivos urbanos. Visualiza los datos en tiempo real, analiza sus tendencias y recibe recomendaciones personalizadas.")

# Conexión a InfluxDB
def query_data(measurement, fields, range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()
    filters = " or ".join([f'r[\"_field\"] == \"{field}\"' for field in fields])
    query = f"""
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "{measurement}" and ({filters}))
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    """
    df = query_api.query_data_frame(query)
    if df.empty:
        return pd.DataFrame()
    df = df.rename(columns={{"_time": "time"}})
    df["time"] = pd.to_datetime(df["time"])
    return df

# Parámetro temporal
range_minutes = st.slider("⏱ Selecciona el rango de tiempo (en minutos):", 10, 180, 60)

# Consultas
df_air = query_data("airSensor", ["temperature", "humidity"], range_minutes)
df_accel = query_data("accelerometer", ["ax", "ay", "az"], range_minutes)

# Datos crudos
with st.expander("📄 Ver datos crudos"):
    if not df_air.empty:
        st.write("### Datos de temperatura y humedad")
        st.dataframe(df_air)
    if not df_accel.empty:
        st.write("### Datos del acelerómetro")
        st.dataframe(df_accel)

# Gráficas y estadísticas
st.markdown("### 📊 Visualización de datos y análisis estadístico")
col1, col2 = st.columns(2)

if not df_air.empty:
    with col1:
        st.write("#### 🌡️ Temperatura (°C)")
        st.plotly_chart(px.line(df_air, x="time", y="temperature", title="Temperatura"), use_container_width=True)
        st.metric("Promedio", round(df_air["temperature"].mean(), 2))
        st.metric("Máximo", round(df_air["temperature"].max(), 2))
        st.metric("Mínimo", round(df_air["temperature"].min(), 2))

    with col2:
        st.write("#### 💧 Humedad (%)")
        st.plotly_chart(px.line(df_air, x="time", y="humidity", title="Humedad"), use_container_width=True)
        st.metric("Promedio", round(df_air["humidity"].mean(), 2))
        st.metric("Máximo", round(df_air["humidity"].max(), 2))
        st.metric("Mínimo", round(df_air["humidity"].min(), 2))

# Movimiento (acelerómetro)
if not df_accel.empty:
    st.write("#### 📈 Movimiento (Magnitud del acelerómetro)")
    df_accel["accel_magnitude"] = np.sqrt(df_accel["ax"]**2 + df_accel["ay"]**2 + df_accel["az"]**2)
    st.plotly_chart(px.line(df_accel, x="time", y="accel_magnitude", title="Movimiento total"), use_container_width=True)

# Recomendaciones automatizadas
if not df_air.empty:
    st.markdown("### 🌱 Recomendaciones Automatizadas")
    humedad_actual = df_air["humidity"].iloc[-1]
    temperatura_actual = df_air["temperature"].iloc[-1]
    uv_simulado = 8  # Radiación UV simulada

    if humedad_actual < 40:
        st.warning("💧 Humedad baja: Riega con un atomizador o coloca una bandeja con agua cerca.")
        st.caption("La baja humedad puede secar las hojas y afectar el crecimiento.")
    elif humedad_actual > 80:
        st.warning("💧 Humedad alta: Mejora la ventilación o usa un deshumidificador.")
        st.caption("El exceso de humedad puede causar hongos o pudrición.")
    else:
        st.success("💧 Humedad óptima.")

    if uv_simulado > 7:
        st.warning("☀️ Radiación UV alta (simulada): Protege el cultivo con sombra parcial o reubícalo.")
        st.caption("La exposición prolongada a UV puede dañar tejidos sensibles de las plantas.")
    else:
        st.success("☀️ Radiación UV adecuada para la fotosíntesis.")

st.markdown("---")
st.markdown("Aplicación desarrollada como proyecto de Computación Física e IoT.")
