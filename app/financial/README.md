# Explorador de Tickers S&P 500 con IA local (llama3)

Este proyecto es una aplicación interactiva construida con Streamlit que permite explorar, comparar y analizar la evolución semanal de los precios de hasta 3 empresas del S&P 500. Además, integra un modelo de lenguaje local (llama3 vía Ollama) para realizar comparativas inteligentes a partir de un prompt personalizado.

## ¿Cómo funciona?

1. **Carga de Tickers:**
   - El script obtiene la lista actualizada de empresas del S&P 500 desde Wikipedia.
   - Muestra un selector donde puedes buscar y elegir hasta 3 tickers (símbolo y nombre de la empresa).

2. **Visualización de Precios:**
   - Para cada ticker seleccionado, descarga los precios de cierre de la última semana usando yfinance.
   - Muestra un gráfico individual para cada ticker, facilitando la comparación visual.

3. **Información Detallada:**
   - Debajo de los gráficos, se muestra información relevante de cada empresa: nombre, sector, industria, precio actual, moneda y sitio web.

4. **Comparativa con IA (llama3):**
   - Puedes escribir un prompt personalizado para pedir un análisis, resumen o comparativa entre los tickers seleccionados.
   - Al pulsar el botón, el script envía los datos y el prompt al modelo llama3 corriendo localmente en Ollama.
   - La respuesta de la IA se muestra directamente en la app.

## ¿Por qué funciona así?
- **Streamlit** permite crear dashboards interactivos de forma sencilla y rápida en Python.
- **yfinance** facilita la descarga de datos históricos de acciones de Yahoo Finance.
- **Ollama + llama3** permite usar modelos de lenguaje avanzados localmente, sin depender de la nube ni exponer datos sensibles.
- El flujo es eficiente: solo se descargan datos y se consulta la IA para los tickers seleccionados, optimizando recursos y velocidad.

## Requisitos
- Python 3.8+
- Tener instalado Ollama y el modelo llama3 descargado y corriendo localmente.
- Instalar dependencias con:
  ```
  pip install -r requirements.txt
  ```

## Cómo ejecutar
1. Inicia el servidor de Ollama y asegúrate de tener el modelo llama3:
   ```
   ollama serve
   ollama pull llama3
   ```
2. Ejecuta la app de Streamlit:
   ```
   streamlit run sp500_streamlit.py
   ```
3. Abre el navegador en la URL que te indique Streamlit (por defecto http://localhost:8501).

## Personalización
- Puedes modificar el prompt para pedir análisis específicos a la IA.
- Puedes cambiar el número máximo de tickers a comparar.
- El código es modular y fácil de adaptar a otros índices o modelos.

---

**Autor:**
- Juan Carlos Macías
