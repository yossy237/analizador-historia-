#!/usr/bin/env python

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Analizador de Textos Históricos",
    layout="centered",
    page_icon="📜"
)

DATA_FILEPATH = "historia.export.all.tsv"


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Load data from local TSV (sin saltar filas)."""
    return pd.read_csv(filepath, sep="\t").fillna("")


def search_dataframe(df: pd.DataFrame, column: str, search_str: str) -> pd.DataFrame:
    """Search a column for a substring and return results as df."""
    if not search_str:
        return df.iloc[0:0]  # empty df same columns
    return df.loc[df[column].str.contains(search_str, case=False)]


def generate_barplot(results: pd.DataFrame, count_column: str, top_n: int = 10):
    """load results from search_dataframe() and create barplot."""
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
            alt.datum.rank < top_n
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
            title="Top 10 — Fuentes históricas más frecuentes"
        )
        .interactive()
    )


def app():
    """Search Streamlit App."""
    st.title("Analizador de Textos Históricos 📜")
    st.caption("Explora menciones, temas, publicaciones...")

    df = load_data(DATA_FILEPATH)

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

        st.subheader("Muestras de resultados (primeros 10):")
        st.table(results.head(10))

        st.subheader("Distribución de publicaciones:")
        st.altair_chart(generate_barplot(results, "journal", 10), use_container_width=True)


if __name__ == "__main__":
    app()
      