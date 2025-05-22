
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.express as px
import numpy as np

from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Configuración de la página
st.set_page_config(page_title="🌿 Verdana – Naturaleza que te escucha", layout="wide")

st.title("🌿 Verdana – Naturaleza que te escucha")
st.markdown("Una app sensorial que traduce los datos de tu planta en bienestar. Visualiza temperatura, humedad y movimiento en tiempo real.")

# Conexión y consultas a InfluxDB
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
    data = [{"time": record.get_time(), field: record.get_value()} for table in result for record in table.records]
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

# Recomendaciones de humedad basadas en el último valor
def mostrar_recomendaciones(humedad, uv=5):
    st.subheader("🌱 Recomendaciones de Cuidado")
    if humedad < 40:
        st.warning("💧 Humedad baja: Riega con un atomizador o coloca una bandeja con agua cerca.")
        st.markdown("*La baja humedad puede secar las hojas y afectar el crecimiento.*")
    elif humedad > 80:
        st.warning("💧 Humedad alta: Mejora la ventilación o usa un deshumidificador.")
        st.markdown("*El exceso de humedad puede causar hongos o pudrición.*")
    else:
        st.success("💧 Humedad óptima: No es necesario intervenir.")

    if uv > 7:
        st.warning("☀️ Radiación UV alta (simulada): Protege el cultivo con sombra parcial o reubícalo.")
        st.markdown("*La radiación intensa puede dañar tejidos sensibles de la planta.*")
    else:
        st.success("☀️ Radiación UV adecuada para la fotosíntesis.")

# Interfaz principal
range_minutes = st.slider("⏱ Selecciona el rango de tiempo (en minutos):", 10, 180, 60)

temp_df = query_data("airSensor", "temperature", range_minutes)
hum_df = query_data("airSensor", "humidity", range_minutes)
mov_df = query_accelerometer_data(range_minutes)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🌡️ Temperatura (°C)")
    if not temp_df.empty:
        st.plotly_chart(px.line(temp_df, x="time", y="temperature"), use_container_width=True)
    else:
        st.info("No hay datos de temperatura disponibles.")

with col2:
    st.subheader("💧 Humedad (%)")
    if not hum_df.empty:
        st.plotly_chart(px.line(hum_df, x="time", y="humidity"), use_container_width=True)
    else:
        st.info("No hay datos de humedad disponibles.")

st.subheader("📈 Movimiento (magnitud del acelerómetro)")
if not mov_df.empty:
    st.plotly_chart(px.line(mov_df, x="time", y="accel_magnitude"), use_container_width=True)
else:
    st.info("No hay datos de movimiento disponibles.")

# Recomendaciones
if not hum_df.empty:
    mostrar_recomendaciones(hum_df["humidity"].iloc[-1])
