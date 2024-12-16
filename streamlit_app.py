import streamlit as st
import pandas as pd
import re  
import os
from PIL import Image
import base64
from io import BytesIO
import datetime
import copy
from groq import Groq
from datetime import date
import requests

hoy = date.today()

ruta_imagen = "https://i.ibb.co/vcgGs9B/a10.png"

# Establece la clave API para acceder a la API de Groq desde st.secrets
api_key = st.secrets["general"]["GROQ_API_KEY"]

modelo = 'llama-3.1-70b-versatile'

# Inicializa el cliente de Groq usando la clave API
client = Groq(
    api_key=api_key,
)


def generar_resumen(pregunta, horoscopo):

    prompt = f"""
    Regarding this comment: {horoscopo},
    answer this question without methodological details:
    {pregunta}
    """   
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "You are an astrologer and an expert in name etymology"
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        #tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message.content
    
    return response_message

def generar_recomendacion(nombre):
    prompt = f"""
    Hello, my name is {nombre} (If empty or the name doesn’t exist, request a correction without generating additional output).
    Generate a message in two paragraphs:

    In the first paragraph, craft a brief inspirational message with reflections, predictions, 
    or advice, both fun and thought-provoking, like those found inside fortune cookies. The message should be direct, without 
    introductions or opening phrases like "Here’s your message."

    In the second paragraph, write an astrological message related to my name if possible.
    Additionally, use today's date ({hoy}) to identify relevant aspects of the day, such as the position of planets, 
    important transits, or the lunar phase. Aim to find a symbolic or astrological connection that resonates with the name 
    or the overall situation. This message should also be concise and without introductions.
    
    In both paragraphs, use emojis occasionally.
        
    """
    
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "You are an astrologer and an expert in name etymology"
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        #tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message.content
    
    return response_message

def crear_grafico(datos):
    # Crear el gráfico de líneas
    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(datos['Fecha de respuesta'], datos['NPS'], marker='o', linestyle='-', color='b')

    # Personalización del gráfico
    ax.set_title('Tendencia de NPS', fontsize=16)
    #ax.set_xlabel('Fecha de respuesta', fontsize=12)
    ax.set_ylabel('NPS', fontsize=12)

    # Eliminar líneas de los ejes x e y (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Eliminar las marcas en los ejes
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=True)

    # Formato de fechas en el eje X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))  # Formato mm/aaaa
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Espaciado mensual

    # Mejorar la visualización de las fechas
    plt.xticks(rotation=45, ha='right')  # Rotar fechas para mejor legibilidad

    # Agregar un grid (opcional)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Ajustar los márgenes para que no se corten las fechas
    plt.tight_layout()

    # Guardar el gráfico en BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig)
    return img_buffer

# La función principal, ahora recibe el tópico como parámetro
def get_tip(nombre):
    
    nombre = nombre
   
    # Recomendaciones
    Reco = generar_recomendacion(nombre)



    # Guardar en el estado de sesión para acceso rápido
    st.session_state['Reco'] = Reco
    st.session_state['comentarios'] = Reco

    return {"recomendacion": Reco} 

# Mostrar resultados en Streamlit
def mostrar_resultados(recomendacion):
    """
    Función para mostrar los resultados de indicadores y recomendaciones en Streamlit.
    
    Args:
        indicadores (dict): Diccionario con los indicadores calculados.
        recomendacion (str): Recomendación generada.
    """
    # Mostrar recomendación
    if recomendacion:
        st.subheader("💬")
        recomendacion_html = recomendacion.replace("\n", "<br>")
        st.markdown(
        f"""
        <div style="background-color: #FCF3EA; padding: 10px; border-radius: 7px; color: #606062;
        font-size: 17px; font-weight: 600; line-height: 1; margin-bottom: 10px !important;">
        <br>{recomendacion_html}<br>
        <br>
        </div>
        <br>
        <hr style="border: 1px solid #606062; margin-top: 10px;">
        """,
        unsafe_allow_html=True
    )
        #st.write(recomendacion)
    else:
        st.warning("No se generó ninguna recomendación.")


############################################################################################################################
######---- Interfaz en Streamlit-----#######################################################################################
############################################################################################################################

# Inicia ngrok con la URL de Streamlit, omitiendo la advertencia del navegador
#public_url = ngrok.connect(8501,  bind_tls=True)

# Mostrar la URL de ngrok generada
#print(f"Streamlit is running on: {public_url}")

# Cargar la imagen Loope in Hiwork
# Descargar la imagen desde la URL
response = requests.get(ruta_imagen)

if response.status_code == 200:
    image = Image.open(BytesIO(response.content))

    # Convertir la imagen a base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Mostrar la imagen en Streamlit
    #st.image(image, caption="Imagen cargada desde URL")
else:
    st.error("No se pudo cargar la imagen desde la URL")

# Crear el HTML para una imagen responsiva
st.markdown(
    f"""
    <style>
    .responsive-img {{
        width: 35%;
        max-width: 500px;
        height: auto;
    }}
    </style>
    <img src="data:image/png;base64,{img_str}" class="responsive-img">
    """,
    unsafe_allow_html=True
    )

st.markdown('''
<a href="https://paypal.me/JavierAlbertoOliver?country.x=AR&locale.x=es_XC" target="_blank" style="text-decoration:none; font-weight:bold;">
👉 Donate 😘
</a>
''', unsafe_allow_html=True)

# Ingreso de ANI
st.subheader("Enter your Name")
nombre_ingresado = st.text_input("your Name?:", "")

if nombre_ingresado:  # Verifica que se haya ingresado algo
    # Verificar si se ha ingresado un nuevo ANI
    if 'nombre' not in st.session_state or st.session_state['nombre'] != nombre_ingresado:
        st.session_state['nombre'] = nombre_ingresado

        # Obtener resultados para el nuevo ANI
        nuevo_resultado = get_tip(nombre_ingresado)

        # Inicializar el historial si no existe
        if 'historial_resultados' not in st.session_state:
            st.session_state['historial_resultados'] = []

        # Eliminar los resultados previos del historial para este ANI si ya existían
        st.session_state['historial_resultados'] = [
            entry for entry in st.session_state['historial_resultados'] 
            if entry['nombre'] != nombre_ingresado
        ]

        # Agregar los nuevos resultados al historial
        st.session_state['historial_resultados'].append({
            "nombre": nombre_ingresado,
            "resultados": nuevo_resultado
        })

    # Mostrar historial en orden inverso
    for idx, item in enumerate(reversed(st.session_state['historial_resultados'])):
        try:
            # Verificar que 'resultados' no sea None
            if item.get('resultados') is not None:
                resultados = item['resultados']

                # Verificar que 'indicadores' y 'recomendacion' estén presentes en 'resultados'
                indicadores = resultados.get('indicadores', 'No hay indicadores')
                recomendacion = resultados.get('recomendacion', 'No hay recomendación')

                # Usar st.markdown para mostrar el ANI y estilo
                nombre = item.get('nombre', 'N/A')
                st.markdown(f"""
                    <div style="background-color: #f9f9f9; color: grey; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 5px;">
                        {len(st.session_state['historial_resultados']) - idx} - {nombre}
                    </div>
                """, unsafe_allow_html=True)

                # Mostrar los detalles de los resultados para este ANI
                mostrar_resultados(recomendacion)
            else:
                st.warning(f"El item {idx+1} no tiene resultados válidos.")
        
        except KeyError as e:
            st.error(f"Error al acceder a la clave {e} en el item del historial de resultados.")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado: {e}")

else:
    st.write("After entering your name, press Enter.")


# Preguntas sobre los comentarios
if "comentarios" in st.session_state:
    st.subheader("Do you want to ask me any questions about the message?")
    pregunta = st.text_area("Write your question or request and click 'Ask'", height=150)
    
    if st.button("Ask"):
        resumen = generar_resumen(pregunta, st.session_state.comentarios)
        
        # Almacenar la respuesta en session_state para persistencia
        if 'respuestas' not in st.session_state:
            st.session_state.respuestas = []
        st.session_state.respuestas.append({"pregunta": pregunta, "respuesta": resumen, "nombre": st.session_state['nombre']})


# Mostrar preguntas y respuestas previas
if 'respuestas' in st.session_state:
    st.subheader("History of questions and answers")

    # Iterar en orden inverso para mostrar la última respuesta primero
    for idx, item in enumerate(reversed(st.session_state.respuestas), start=1):
        st.markdown(f"""
        <div style="background-color: #f9f9f9; color: grey; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            {item['nombre']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-left: 20px; font-size: 16px;">
            <br>        
            <strong>Question {len(st.session_state['respuestas']) - idx + 1}:</strong> {item['pregunta']}<br>
            <br>
        </div>
        """, unsafe_allow_html=True)

        # Manejar los saltos de línea en la respuesta
        respuesta_formateada = item['respuesta'].replace('\n', '<br>')
        st.markdown(f"""
        <div style="margin-left: 20px;">       
            {respuesta_formateada}<br>
            <br> 
        </div>
        """, unsafe_allow_html=True)
