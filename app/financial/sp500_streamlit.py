
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.title("Explorador de Tickers S&P 500")

@st.cache_data
def obtener_tickers_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tablas = pd.read_html(url)
    df = tablas[0]
    return df[['Symbol', 'Security']]




# Obtener tickers (sin sector, para que la app sea rápida)
df_tickers = obtener_tickers_sp500()



# Ordenar la tabla por Symbol por defecto
df_tickers = df_tickers.sort_values(by="Symbol")

opciones_selector = df_tickers.apply(lambda row: f"{row['Symbol']} - {row['Security']}", axis=1)
mapa_ticker = dict(zip(opciones_selector, df_tickers['Symbol']))
tickers_seleccionados_str = st.multiselect(
    "Selecciona hasta 3 tickers para comparar evolución semanal:",
    opciones_selector,
    max_selections=3
)
tickers_seleccionados = [mapa_ticker[op] for op in tickers_seleccionados_str]


# Mostrar los gráficos de los tickers seleccionados en una sola línea horizontal y más pequeños
if tickers_seleccionados:
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=7)
    cols = st.columns(len(tickers_seleccionados))
    datos_tickers = {}
    for idx, ticker in enumerate(tickers_seleccionados):
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)
        if not hist.empty:
            # Convertir el índice a string para evitar error de serialización
            datos_tickers[ticker] = {str(k): float(v) for k, v in hist['Close'].to_dict().items()}
        else:
            datos_tickers[ticker] = {}
        with cols[idx]:
            if not hist.empty:
                st.markdown(f"**{ticker}**")
                df_graf = pd.DataFrame({ticker: hist['Close']})
                st.line_chart(df_graf, height=200, width=250)
            else:
                st.info(f"No hay datos para {ticker}.")

    # --- Integración con Ollama llama3 ---
    st.markdown("---")
    st.subheader("Comparativa con IA (llama3 en Ollama)")
    prompt = st.text_area("Escribe tu prompt para comparar los tickers seleccionados:")
    if st.button("Analizar con llama3"):
        import requests
        import json
        # Preparamos el contexto para el modelo
        contexto = {
            "tickers": tickers_seleccionados,
            "datos": datos_tickers,
            "prompt_usuario": prompt
        }
        mensaje = f"Compara los siguientes tickers usando los datos proporcionados y responde al prompt del usuario.\n\nDatos: {json.dumps(contexto, ensure_ascii=False)}"
        try:
            respuesta = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": mensaje,
                    "stream": False
                },
                timeout=120
            )
            if respuesta.status_code == 200:
                resultado = respuesta.json()
                st.success(resultado.get("response", "Sin respuesta del modelo."))
            else:
                st.error(f"Error llamando a Ollama: {respuesta.status_code}")
        except Exception as e:
            st.error(f"Error conectando con Ollama: {e}")

# Mostrar listado de tickers y tabla SIEMPRE
st.write(f"Total de tickers S&P 500: {len(df_tickers)}")
tabla = df_tickers[["Symbol", "Security"]].rename(columns={"Symbol": "Ticker", "Security": "Nombre"})
st.dataframe(tabla, use_container_width=True)

# Mostrar info de cada ticker debajo (incluyendo sector solo para los seleccionados)
if tickers_seleccionados:
    for ticker in tickers_seleccionados:
        stock = yf.Ticker(ticker)
        info = stock.info
        st.markdown(f"---\n### Información de {ticker}")
        st.write(f"**Nombre:** {info.get('longName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industria:** {info.get('industry', 'N/A')}")
        st.write(f"**Precio actual:** {info.get('currentPrice', 'N/A')}")
        st.write(f"**Moneda:** {info.get('currency', 'N/A')}")
        st.write(f"**Sitio web:** {info.get('website', 'N/A')}")
