import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Texto a Python AI", page_icon="🐍", layout="wide")

# --- ESTILO CSS (Opcional) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body { font-family: 'Roboto', sans-serif; }
    h1 { text-align: center; color: #306998; } /* Azul Python */
    .stButton>button { background-color: #FFD43B; color: #306998; border-radius: 5px; font-weight: bold; border: 1px solid #306998;} /* Amarillo Python */
    .stTextArea textarea { border: 1px solid #ccc; border-radius: 5px; }
    /* Estilo para la caja de código Python resultante */
    .stCodeBlock {
        border: 2px solid #306998;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE LA API ---
def texto_a_python(api_key, peticion_natural):
    """Llama a la API de OpenRouter para convertir lenguaje natural a Python."""

    # Meta-prompt específico para Text-to-Python
    instruccion = f"""
    Actúa como un programador Python senior experto.
    Tu tarea es traducir la siguiente descripción en lenguaje natural a código Python funcional y bien escrito (Python 3.9+).

    **Descripción del Usuario:**
    "{peticion_natural}"

    **Instrucciones Adicionales:**
    - Incluye los imports necesarios al principio del script.
    - Añade comentarios breves si la lógica no es obvia.
    - Prioriza el uso de la librería estándar de Python si es posible.
    - Formatea el código siguiendo las convenciones PEP 8.
    - Devuelve ÚNICAMENTE el código Python generado, sin explicaciones, saludos, notas, ni formato markdown (como ```python ... ```). Solo el código Python puro.
    """

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    # Modelos como GPT-4, Claude, o CodeLlama son excelentes para código
    payload = {
        "model": "openai/gpt-3.5-turbo", # Puedes probar modelos específicos para código
        "messages": [{"role": "user", "content": instruccion}],
        "max_tokens": 1024, # Aumenta si necesitas código más largo
        "temperature": 0.2 # Baja para código más predecible y correcto
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=90) # Aumentamos timeout por si tarda más
        if response.status_code != 200: return f"Error HTTP {response.status_code}: {response.text}"
        data = response.json()
        if "error" in data: return f"Error de OpenRouter: {data['error'].get('message', 'Sin mensaje')}"
        python_code = data["choices"][0]["message"]["content"]
        # Limpieza extra
        python_code = python_code.replace("```python", "").replace("```", "").strip()
        return python_code
    except Exception as e:
        return f"Error interno de la aplicación: {str(e)}"

# --- INTERFAZ DE USUARIO ---
st.title("🐍 Traductor de Texto a Python con IA")
st.write("Describe la funcionalidad que quieres en Python y la IA generará el código.")

st.subheader("Describe lo que quieres que haga el código:")
peticion_input = st.text_area(
    "Tu descripción:",
    height=200,
    key="peticion_input",
    placeholder="Ej: Escribe una función que reciba una lista de números y devuelva la suma de los cuadrados de esos números."
)

# Botón de conversión
boton_convertir = st.button("Generar Código Python")

st.markdown("---")

st.subheader("Código Python Generado:")
# Placeholder para el resultado
resultado_placeholder = st.empty()
resultado_placeholder.code("El código Python aparecerá aquí...", language="python")

# Lógica del botón adaptada para producción
if boton_convertir:
    if not peticion_input:
        st.warning("Por favor, describe la funcionalidad que deseas.")
    # --- Lectura de la API Key desde st.secrets ---
    elif "OPENROUTER_API_KEY" not in st.secrets:
        st.error("Error: La clave API no está configurada en los 'Secrets' de la aplicación.")
    else:
        api_key = st.secrets["OPENROUTER_API_KEY"] # Leer desde secrets
        with st.spinner("Generando código Python..."):
            python_resultado = texto_a_python(api_key, peticion_input) # Pasar la clave leída
            # Mostramos el resultado en el placeholder usando st.code
            resultado_placeholder.code(python_resultado, language="python")
            if "Error" not in python_resultado:
                st.success("¡Código Python generado!")
                st.info("Revisa y prueba el código generado antes de usarlo.")
            else:
                 st.error("Hubo un problema al generar el código.")