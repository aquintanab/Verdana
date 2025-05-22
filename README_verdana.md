
# 🌿 Verdana – Naturaleza que te escucha

**Verdana** es una experiencia interactiva que conecta tecnología, naturaleza y bienestar. A través de una planta sensorizada, esta aplicación visualiza temperatura, humedad y movimiento en tiempo real, ofreciendo recomendaciones personalizadas para su cuidado y promoviendo la conciencia ambiental.

## ✨ Concepto

Inspirada en el bienestar sensorial, Verdana convierte tu planta en un espejo de tu entorno. Al detectar condiciones críticas, sugiere acciones prácticas y educativas, guiándote en el cuidado consciente de microcultivos urbanos.

## 🛠 Tecnologías utilizadas

- **ESP32** – Microcontrolador con conectividad WiFi
- **DHT22** – Sensor de temperatura y humedad
- **MPU6050** – Sensor de aceleración
- **InfluxDB** – Base de datos de series temporales
- **Python** – Procesamiento y lógica
- **Streamlit** – Visualización web interactiva
- **GitHub** – Control de versiones

## 📊 Funcionalidades

- Visualización en tiempo real de temperatura, humedad y movimiento.
- Recomendaciones automáticas basadas en condiciones ambientales.
- Visualización histórica con gráficos interactivos.
- Diseño minimalista, relajante y centrado en el usuario.

## 🚀 ¿Cómo ejecutar la aplicación?

1. **Clona este repositorio:**
```bash
git clone https://github.com/tuusuario/verdana.git
cd verdana
```

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configura InfluxDB en el archivo `config.py`**

4. **Ejecuta la app:**
```bash
streamlit run app_verdana.py
```

5. **Abre tu navegador:**
```
http://localhost:8501
```

## 📁 Estructura del proyecto

```
verdana/
├── app_verdana.py        # Aplicación principal en Streamlit
├── config.py             # Configuración de InfluxDB
├── requirements.txt      # Dependencias
├── assets/               # Imágenes y recursos visuales
└── README.md
```

## 🌱 Créditos

Desarrollado para el curso de **Computación Física e IoT**  
Autores: Adriana Quintana, Mateo Alzate y Santiago Cáceres  
Licencia: MIT
