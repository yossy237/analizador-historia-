#!/usr/bin/env python
import sqlite3
import altair as alt
import pandas as pd
import streamlit as st

# CONFIGURACIÓN INICIAL
st.set_page_config(
    page_title="Analizador de Textos Históricos",
    layout="centered",
    page_icon="📜"
)

DB_PATH = "historia.db"  # base de datos SQLite
TABLE_NAME = "fuentes_historicas"

# FUNCIONES DE CARGA Y PROCESAMIENTO
@st.cache_data
def load_data_from_db(db_path: str, table: str) -> pd.DataFrame:
    """Carga los datos históricos desde la base SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos desde la base: {e}")
        return pd.DataFrame()


@st.cache_data
def get_historical_vocabulary(df: pd.DataFrame) -> set:
    """Extrae vocabulario de palabras únicas desde columnas relevantes."""
    posibles_columnas = ["title_e", "journal", "título_e", "diario"]
    columnas_presentes = [col for col in posibles_columnas if col in df.columns]

    if not columnas_presentes:
        st.error("⚠️ No se encontraron columnas de texto válidas en la base de datos.")
        return set()

    all_text = " ".join(df[col].astype(str).str.lower().str.cat(sep=" ") for col in columnas_presentes)
    vocab = set(all_text.split())

    # Filtrar conectores comunes (stopwords)
    stopwords = {"la", "el", "los", "las", "de", "del", "en", "y", "a", "un", "una", "que", "por", "con", "para"}
    vocab = {word for word in vocab if word not in stopwords and len(word) > 2}
    return vocab


def search_dataframe(df: pd.DataFrame, column: str, search_str: str) -> pd.DataFrame:
    """Busca una subcadena en una columna y devuelve coincidencias."""
    if not search_str:
        return df.iloc[0:0]
    return df.loc[df[column].str.contains(search_str, case=False, na=False)]


def generate_barplot(results: pd.DataFrame, count_column: str, top_n: int = 10):
    """Crea un gráfico de barras con los resultados agrupados."""
    return (
        alt.Chart(results)
        .transform_aggregate(
            count="count()",
            groupby=[f"{count_column}"]
        )
        .transform_window(
            rank="rank(count)",
            sort=[alt.SortField("count", order="descending")]
        )
        .transform_filter(
            alt.datum.rank <= top_n
        )
        .mark_bar()
        .encode(
            y=alt.Y(f"{count_column}:N", sort="-x", title="Publicación / Journal"),
            x=alt.X("count:Q", title="Cantidad de menciones"),
            tooltip=[f"{count_column}:N", "count:Q"]
        )
        .properties(
            width=700,
            height=400,
            title=f"Top {top_n} — Fuentes históricas más frecuentes"
        )
        .interactive()
    )

# APLICACIÓN PRINCIPAL
def app():
    """Aplicación Streamlit: Analizador de Textos Históricos"""
    st.title("📜 Analizador de Textos Históricos")
    st.caption("Explora menciones, temas y analiza textos con vocabulario histórico.")

    # Cargar datos desde SQLite
    df = load_data_from_db(DB_PATH, TABLE_NAME)

    if df.empty:
        st.warning("No se pudieron cargar datos. Verifica la base de datos SQLite.")
        return

    # Generar vocabulario histórico
    historical_vocab = get_historical_vocabulary(df)

    # Selección de modo
    mode = st.radio("Selecciona una acción:", ["Buscar palabra", "Analizar texto"])

    #  MODO 1 — Buscar palabra
    if mode == "Buscar palabra":
        with st.form(key="busqueda"):
            text_query = st.text_input(label="Ingresa una palabra (p. ej. Imperio, Roma…)")
            submit_button = st.form_submit_button(label="Buscar")

        if submit_button:
            with st.spinner("Consultando archivos antiguos… 📚⌛"):
                results = search_dataframe(df, "title_e", text_query)

            st.success(
                f"Consulta finalizada — {len(results):,} coincidencias encontradas "
                f"en un corpus de {len(df):,} entradas históricas."
            )

            if not results.empty:
                st.subheader("Muestras de resultados (primeros 10):")
                st.table(results.head(10))

                st.subheader("Distribución de publicaciones:")
                st.altair_chart(generate_barplot(results, "journal", 10), use_container_width=True)
            else:
                st.warning("No se encontraron coincidencias para esa palabra.")

    # 🧠 MODO 2 — Analizar texto
    elif mode == "Analizar texto":
        user_text = st.text_area(
            "Pega o escribe un texto para analizar:",
            height=200,
            placeholder="Ejemplo: Durante el Imperio Romano, la expansión territorial..."
        )

        if st.button("Analizar texto"):
            if not user_text.strip():
                st.warning("Por favor, ingresa un texto antes de analizar.")
                return

            with st.spinner("Analizando contenido... ⚙️"):
                words = user_text.lower().split()
                total_words = len(words)
                matched = [w for w in words if w in historical_vocab]
                match_ratio = len(matched) / total_words if total_words else 0

            # Mostrar resultados
            st.subheader("Resultados del análisis:")
            st.write(f"🔹 Palabras totales: {total_words}")
            st.write(f"🔹 Palabras históricas detectadas: {len(matched)}")
            st.write(f"📊 Coincidencia: {match_ratio:.1%}")

            # Clasificación del texto
            if match_ratio > 0.4:
                st.success("Este texto tiene un ALTO contenido histórico.")
            elif match_ratio > 0.15:
                st.info("⚖️ Este texto tiene algunos rasgos históricos.")
            else:
                st.warning("Este texto parece no estar relacionado con temas históricos.")

            # Mostrar palabras coincidentes
            if matched:
                st.subheader("Palabras coincidentes:")
                st.write(", ".join(sorted(set(matched))[:50]))

                # Gráfico de frecuencia
                freq_df = pd.DataFrame({"word": matched})
                chart = (
                    alt.Chart(freq_df)
                    .mark_bar()
                    .encode(
                        x="count():Q",
                        y=alt.Y("word:N", sort="-x"),
                        tooltip=["word", "count()"]
                    )
                    .properties(
                        title="Palabras históricas más frecuentes en el texto",
                        width=600,
                        height=400
                    )
                )
                st.altair_chart(chart, use_container_width=True)

# EJECUCIÓN
if __name__ == "__main__":
    app()
