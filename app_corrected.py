
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import numpy as np
import plotly.express as px

from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Configuración visual
st.set_page_config(page_title="🌿 Verdana – Cultivos Inteligentes", layout="wide")

st.markdown("## 🌿 Verdana – Monitoreo de Microcultivos Urbanos")
st.caption("Visualiza datos ambientales, analiza tendencias y recibe recomendaciones para el cuidado de tu cultivo.")

# Estilo personalizado
st.markdown("""
<style>
    .stMetric {
        background-color: #f4f4f4;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Función genérica de consulta
def query_measurement_fields(measurement, fields, range_minutes=60):
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
        query_api = client.query_api()
        filters = " or ".join([f'r["_field"] == "{f}"' for f in fields])
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
        df = df.rename(columns={"_time": "time"})
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        st.error(f"Error al consultar {measurement}: {e}")
        return pd.DataFrame()

# Parámetro de tiempo
range_minutes = st.slider("🕒 Selecciona el rango de tiempo (min):", 10, 180, 60)

# Consultas
df_air = query_measurement_fields("airSensor", ["temperature", "humidity", "heat_index"], range_minutes)
df_uv = query_measurement_fields("uv_sensor", ["uv_index", "uv_raw"], range_minutes)
if not df_uv.empty:
    df_uv["uv_index"] = pd.to_numeric(df_uv["uv_index"], errors="coerce")
df_accel = query_measurement_fields("accelerometer", ["ax", "ay", "az"], range_minutes)

# Análisis y visualización
st.subheader("📊 Análisis y Visualización")
col1, col2 = st.columns(2)

with col1:
    if not df_air.empty:
        st.metric("🌡️ Temp. Promedio (°C)", round(df_air["temperature"].mean(), 2))
        st.metric("💧 Humedad Promedio (%)", round(df_air["humidity"].mean(), 2))
    if not df_uv.empty:
        st.metric("☀️ Índice UV Promedio", round(df_uv["uv_index"].mean(), 2))

with col2:
    if not df_air.empty:
        st.write("**Temperatura y Humedad**")
        st.plotly_chart(px.line(df_air, x="time", y=["temperature", "humidity"]), use_container_width=True)
    if not df_uv.empty:
        st.write("**Índice UV**")
        st.plotly_chart(px.line(df_uv, x="time", y="uv_index"), use_container_width=True)

if not df_accel.empty:
    df_accel["accel_magnitude"] = np.sqrt(df_accel["ax"]**2 + df_accel["ay"]**2 + df_accel["az"]**2)
    st.write("**Movimiento del Cultivo**")
    st.plotly_chart(px.line(df_accel, x="time", y="accel_magnitude", title="Magnitud de aceleración"), use_container_width=True)

# Recomendaciones
st.subheader("🌱 Recomendaciones Automatizadas")

if not df_air.empty:
    humedad = df_air["humidity"].iloc[-1]
    if humedad < 40:
        st.warning("💧 Humedad baja: Riega o coloca bandejas de agua.")
    elif humedad > 80:
        st.warning("💧 Humedad alta: Mejora ventilación o usa deshumidificador.")
    else:
        st.success("💧 Humedad ideal.")

if not df_uv.empty:
    uv = df_uv["uv_index"].iloc[-1]
    if uv > 7:
        st.warning("☀️ UV alto: Protege los cultivos con sombra.")
    else:
        st.success("☀️ Radiación UV adecuada.")

# Datos crudos
st.subheader("📄 Datos Crudos")
with st.expander("Ver registros"):
    if not df_air.empty:
        st.write("**Sensor DHT22 (Temperatura, Humedad)**")
        st.dataframe(df_air)
    if not df_uv.empty:
        st.write("**Sensor UV (VEML6070)**")
        st.dataframe(df_uv)
    if not df_accel.empty:
        st.write("**Sensor Acelerómetro**")
        st.dataframe(df_accel)

# Dashboard externo Grafana
st.subheader("📺 Panel Externo (Grafana)")
st.markdown(
    '''
    ### Ver panel completo
    Debido a políticas de seguridad, el panel no puede mostrarse aquí directamente.<br>
    👉 [Haz clic aquí para abrir el panel en una nueva pestaña.](https://miguelcmo.grafana.net/)
    ''',
    unsafe_allow_html=True
)
