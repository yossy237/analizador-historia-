import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import unicodedata

st.set_page_config(
    page_title="Analizador de Textos Históricos",
    page_icon="📜"
)

# Stop Words en español (Palabras comunes a ignorar en el denominador)

STOP_WORDS = set([
    'a', 'al', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'del', 'desde', 'durante', 'en', 'entre',
    'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'so', 'sobre', 'tras',
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'mi', 'mis', 'tu', 'tus',
    'su', 'sus', 'nuestro', 'nuestra', 'vuestro', 'vuestra', 'y', 'e', 'o', 'u', 'pero',
    'aunque', 'si', 'no', 'que', 'lo', 'se', 'es', 'son', 'fue', 'eran', 'ha', 'había', 
    'estar', 'están', 'esto', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel',
    'aquella', 'aquellos', 'aquellas', 'yo', 'tu', 'él', 'ella', 'nosotros', 'vosotros', 'ellos', 'ellas',
    'cual', 'cuales', 'quien', 'quienes', 'cuyo', 'cuyos', 'cuyas', 'cuyos', 'otro', 'otra', 'otros', 'otras',
    'mismo', 'misma', 'mismos', 'mismas', 'tan', 'tanto', 'tanta', 'tantos', 'tantas', 'todo', 'toda', 
    'todos', 'todas', 'poco', 'poca', 'pocos', 'pocas', 'mucho', 'mucha', 'muchos', 'muchas', 'casi',
    'tal', 'tales', 'vez', 'veces', 'solo', 'solos', 'sola', 'solas'
])


# Función para remover acentos

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


# Limpiar palabra para comparar

def limpiar(p):
    p = p.lower()
    p = quitar_acentos(p)
    p = re.sub(r"[^a-zñ]", "", p)
    return p


# Cargar vocabulario desde TSV 

@st.cache_data
def cargar_vocabulario():
    df = pd.read_csv("vocabulario.tsv", sep="\t")
    

    df.columns = df.columns.str.strip().str.lower()
    
    df = df.fillna("")

    vocab_con_peso = {}

    for _, fila in df.iterrows():
        try:
            palabra_principal = limpiar(fila["palabra"])
            peso = int(fila["peso"])
        except ValueError:
            continue

        def registrar_palabra(p_limpia, p):
            if p_limpia:
                vocab_con_peso[p_limpia] = max(vocab_con_peso.get(p_limpia, 0), p)

        registrar_palabra(palabra_principal, peso)

        if fila["sinonimos"]:
            for s in str(fila["sinonimos"]).split(";"):
                registrar_palabra(limpiar(s), peso)

        if palabra_principal and not palabra_principal.endswith("s"):
            registrar_palabra(palabra_principal + "s", peso)

    return vocab_con_peso


VOCAB_CON_PESO = cargar_vocabulario()
MAX_PESO_TSV = 5 # El peso máximo en tu escala (5)

# Analizar texto (MODIFICADA: Ignora Stop Words para el denominador)

def analizar_texto(texto):
    palabras = re.findall(r'\b\w+\b', texto.lower())
    
    suma_pesos_detectados = 0
    palabras_encontradas = {} 
    
    palabras_a_contar = [] # Solo palabras que NO son Stop Words

    for p in palabras:
        p_limpia = limpiar(p)
        
        # 1. Ignorar la palabra si es una Stop Word
        if p_limpia in STOP_WORDS:
            continue
            
        # 2. Si NO es Stop Word, se cuenta en el denominador
        palabras_a_contar.append(p_limpia)

        # 3. Si es una palabra clave histórica, sumamos el peso
        if p_limpia in VOCAB_CON_PESO:
            peso_actual = VOCAB_CON_PESO[p_limpia]
            suma_pesos_detectados += peso_actual
            palabras_encontradas[p] = peso_actual

    # Cálculo del Índice de Densidad Histórica (IDH)
    
    total_palabras_significativas = len(palabras_a_contar)
    
    # IDH = (Suma de Pesos / (Total de Palabras * Peso Máximo)) * 100
    peso_maximo_posible = total_palabras_significativas * MAX_PESO_TSV 
    
    if peso_maximo_posible > 0:
        indice_historico = (suma_pesos_detectados / peso_maximo_posible) * 100
    else:
        indice_historico = 0
        
    # Devolvemos el total de tokens, el IDH, y la lista de encontradas (aunque no se muestre)
    return len(palabras), indice_historico, palabras_encontradas

# UI

st.title("📜 Analizador de Textos Históricos")

st.subheader("🔹 Analizar texto")
texto = st.text_area("Escribe o pega el texto a analizar:")

if st.button("🔍 Analizar"):

    if not texto.strip():
        st.warning("Por favor ingresa un texto.")
    else:
        total_palabras, indice_historico, palabras_encontradas = analizar_texto(texto)

        st.header("Resultado del Análisis")

        # ------------------------------------
        # Palabras totales (SOLO queda esta métrica de conteo)
        # ------------------------------------
        st.subheader("🔹 Palabras totales")
        st.metric(label="Palabras encontradas en el texto", value=total_palabras)
        
        st.markdown("---")

        # ------------------------------------
        # Porcentaje histórico (IDH)
        # ------------------------------------
        st.subheader("📊 Coincidencia histórica")
        
        # Muestra el valor
        st.write(f"**{indice_historico:.2f}%**")

        # ------------------------------------
        # Gauge gráfico
        # ------------------------------------
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=indice_historico,
            title={'text': "Nivel Histórico"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 15], 'color': "#ffcccc"},
                    {'range': [15, 30], 'color': "#ffe0b3"},
                    {'range': [30, 50], 'color': "#ffffb3"},
                    {'range': [50, 75], 'color': "#c2f0c2"},
                    {'range': [75, 100], 'color': "#b3e6ff"}
                ]
            }
        ))

        st.plotly_chart(gauge, use_container_width=True)
        

        # ------------------------------------
        # Interpretación
        # ------------------------------------
        st.subheader("🔹 Interpretación")

        if indice_historico <= 15:
            nivel = "Muy bajo — el texto tiene muy poca densidad de conceptos históricos clave. Es poco probable que sea un texto histórico enfocado."
        elif indice_historico <= 30:
            nivel = "Bajo — la densidad histórica es ligera. Aborda temas históricos de forma superficial o con términos de bajo peso."
        elif indice_historico <= 50:
            nivel = "Medio — texto con una densidad histórica moderada."
        elif indice_historico <= 75:
            nivel = "Alto — texto fuertemente histórico."
        else:
            nivel = "Muy alto — texto excepcionalmente denso en términos históricos clave."

        st.success(nivel)
        
       