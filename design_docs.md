“Analizador de Textos Históricos”
1. Objetivo

Construir una aplicación interactiva para analizar un corpus histórico (archivos TSV locales), permitiendo al usuario buscar palabras clave y visualizar patrones de publicaciones.

La app ayuda a:

encontrar referencias históricas por palabra clave

ver resultados inmediatos (primeros 10 matches)

visualizar en qué publicaciones aparecen más menciones

2. Tecnologías
Tecnología	    Uso
Python 3.11	    lenguaje base
Streamlit	    UI / servidor web local
Pandas	        manejo de DataFrames
Altair	        visualización (bar chart)
TSV(archivos)	fuente de datos local
3. Entrada (Input)

Caja de texto donde usuario escribe una palabra (ej: “Roma”, “Imperio”, “Egipto”).
Internamente la búsqueda se hace sobre la columna title_e.
Archivo requerido en la raíz del proyecto:
historia.export.all.tsv

4. Lógica principal

Cargar TSV local → DataFrame.
Esperar palabra del usuario.
Filtrar filas donde title_e contenga la palabra.

Presentar:
tabla con primeros 10 resultados
gráfico top 10 publicaciones (journal) más frecuentes

5. Salida (Output)

DataFrame (vista parcial)
gráfico Altair con conteo agrupado por journal
texto de resumen: cuántas coincidencias se encontraron

6. Limitaciones actuales

Solo se busca en UNA columna (title_e)
Busca coincidencias simples (no semánticas)
Archivo debe estar localmente presente

7. Mejoras futuras

selección de columnas para buscar
caché de consultas frecuentes
exportar resultados (CSV / Excel)
