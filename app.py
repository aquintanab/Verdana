
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.express as px
import numpy as np

from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Configuración visual mínima
st.set_page_config(page_title="🌱 Verdana – Cuida tu cultivo", layout="wide")
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f4f4f4;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Verdana – Monitoreo de Microcultivos")
st.caption("Monitorea condiciones clave para tus cultivos urbanos. Accede a datos, análisis y recomendaciones en tiempo real.")

# Función para consultar múltiples campos de un measurement
def query_data(measurement, field, range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()
    query = f"""
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["_field"] == "{field}")
      |> sort(columns: ["_time"])
    """
    result = query_api.query(query)
    data = []
    for table in result:
        for record in table.records:
            data.append({"time": record.get_time(), field: record.get_value()})
    df = pd.DataFrame(data)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])
    return df

def query_accelerometer_data(range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()
    query = f"""
    import "math"
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "accelerometer" and (r["_field"] == "ax" or r["_field"] == "ay" or r["_field"] == "az"))
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    """
    result = query_api.query_data_frame(query)
    if result.empty:
        return pd.DataFrame()
    result = result.rename(columns={"_time": "time"})
    result["accel_magnitude"] = np.sqrt(result["ax"]**2 + result["ay"]**2 + result["az"]**2)
    result["time"] = pd.to_datetime(result["time"])
    return result[["time", "accel_magnitude"]]

# UI: Rango de tiempo
range_minutes = st.slider("⏱ Rango de tiempo (minutos)", 10, 180, 60)

# Datos
temp_df = query_data("airSensor", "temperature", range_minutes)
hum_df = query_data("airSensor", "humidity", range_minutes)
mov_df = query_accelerometer_data(range_minutes)

# Análisis Estadístico
st.subheader("📊 Análisis de Datos")
col1, col2 = st.columns(2)
if not temp_df.empty:
    with col1:
        st.metric("🌡️ Temperatura Promedio (°C)", round(temp_df["temperature"].mean(), 2))
        st.metric("Máximo", round(temp_df["temperature"].max(), 2))
        st.metric("Mínimo", round(temp_df["temperature"].min(), 2))
if not hum_df.empty:
    with col2:
        st.metric("💧 Humedad Promedio (%)", round(hum_df["humidity"].mean(), 2))
        st.metric("Máximo", round(hum_df["humidity"].max(), 2))
        st.metric("Mínimo", round(hum_df["humidity"].min(), 2))

# Gráficos
st.subheader("📈 Visualizaciones")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**🌡️ Temperatura (°C)**")
    if not temp_df.empty:
        st.plotly_chart(px.line(temp_df, x="time", y="temperature", markers=True), use_container_width=True)
    else:
        st.info("Sin datos de temperatura.")
with col4:
    st.markdown("**💧 Humedad (%)**")
    if not hum_df.empty:
        st.plotly_chart(px.line(hum_df, x="time", y="humidity", markers=True), use_container_width=True)
    else:
        st.info("Sin datos de humedad.")

st.markdown("**📈 Movimiento del Cultivo (magnitud del acelerómetro)**")
if not mov_df.empty:
    st.plotly_chart(px.line(mov_df, x="time", y="accel_magnitude", markers=True), use_container_width=True)
else:
    st.info("Sin datos de movimiento.")

# Datos crudos
st.subheader("📄 Datos Crudos")
with st.expander("Ver registros"):
    if not temp_df.empty:
        st.write("**Temperatura**")
        st.dataframe(temp_df)
    if not hum_df.empty:
        st.write("**Humedad**")
        st.dataframe(hum_df)
    if not mov_df.empty:
        st.write("**Acelerómetro**")
        st.dataframe(mov_df)

# Recomendaciones
st.subheader("🌱 Recomendaciones Automáticas")
if not hum_df.empty:
    humedad = hum_df["humidity"].iloc[-1]
    if humedad < 40:
        st.warning("💧 Humedad baja: se recomienda riego o colocar bandejas de agua.")
    elif humedad > 80:
        st.warning("💧 Humedad alta: mejorar ventilación o usar deshumidificador.")
    else:
        st.success("✅ Humedad dentro del rango ideal.")

# Simulación de radiación UV
uv_simulado = 8
if uv_simulado > 7:
    st.warning("☀️ Radiación UV alta (simulada): protege el cultivo con sombra.")
else:
    st.success("☀️ Radiación UV en nivel adecuado.")
