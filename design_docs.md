Analizador de Textos Históricos Ponderado
1. Objetivo Principal

Construir una aplicación interactiva que clasifique y cuantifique la densidad de contenido histórico de un texto libre proporcionado por el usuario, utilizando un sistema de pesos y excluyendo el ruido léxico común.

La aplicación permite:

Determinar el Índice de Densidad Histórica (IDH).

Cuantificar "qué tan histórico es" un texto mediante un sistema de pesos.

Ignorar el ruido léxico común (Stop Words) para mejorar la precisión.

Proporcionar una interpretación visual del IDH.

2. Tecnologías
Tecnología	Uso
Python 3.11	Lenguaje base
Streamlit	Interfaz gráfica y servidor local
Pandas	Manejo del archivo vocabulario.tsv
Plotly/Go	Visualización tipo Gauge para el IDH
Archivos TSV	Fuente de datos del vocabulario
re / unicodedata	Limpieza léxica, normalización y tokenización
3. Entrada (Input)

Un área de texto grande (st.text_area) donde el usuario escribe o pega el texto a evaluar.

Archivo requerido: vocabulario.tsv ubicado en la raíz del proyecto.

4. Lógica Principal

Se basa en la evaluación ponderada y en la exclusión de ruido léxico para evitar que palabras comunes reduzcan el puntaje histórico.

A. Preparación

Cargar vocabulario: Se carga vocabulario.tsv en un diccionario VOCAB_CON_PESO que asigna un peso de 1 a 5 a cada palabra.

Stop Words: Se define un conjunto de palabras comunes del español que serán ignoradas.

B. Análisis

Conteo Significativo:
Se itera sobre cada token del texto.
Si no es Stop Word, incrementa total_palabras_significativas.

Suma de Pesos:
Si el token coincide con una palabra histórica del vocabulario, su peso se suma a suma_pesos_detectados.

C. Cálculo del IDH

Se utiliza la siguiente fórmula, donde 5 es el peso máximo permitido:

IDH
=
∑
Pesos Detectados
Total Palabras Significativas
×
5
×
100
IDH=
Total Palabras Significativas×5
∑Pesos Detectados
	​

×100
5. Salida (Output)

IDH (%) mostrado mediante st.metric.

Gráfico Gauge (Plotly) mostrando niveles de 0% a 100%.

Interpretación del IDH (muy bajo, bajo, medio, alto, muy alto).

Conteo de tokens presentes en el texto original.

6. Limitaciones Actuales

Solo analiza texto plano desde el cuadro de texto.

No existe persistencia de datos (no se usa historia.db).

La precisión depende del vocabulario y de los pesos asignados.

No hay lematización ni análisis morfológico avanzado.

7. Mejoras Futuras

Implementación de la base de datos historia.db para registrar análisis.

Lematización o stemming para mejorar coincidencias.

Exportación de resultados detallados (palabras detectadas y pesos).

Sistema de caché más eficiente para el vocabulario.

Deploy en Render u otro servidor público.