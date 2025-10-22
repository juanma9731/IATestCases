import streamlit as st
import subprocess
try:
    import ollama
    _HAS_OLLAMA_PY = True
except Exception:
    _HAS_OLLAMA_PY = False
import os
from typing import List, Dict, Any

# Config
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")  # Default model name, user can set OLLAMA_MODEL env var

st.set_page_config(page_title="Chat con Ollama", layout="wide")

st.title("Chat con Ollama")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# UI
with st.sidebar:
    st.header("Configuración")
    model = st.text_input("Modelo Ollama", value=MODEL)
    clear = st.button("Limpiar chat")
    if clear:
        st.session_state.messages = []
        st.session_state['user_input'] = ''
        try:
            st.experimental_rerun()
        except Exception:
            pass




def call_ollama(prompt: str, model_name: str, timeout: int = 60) -> str:
    """Llama a Ollama usando la librería Python si está disponible, si no usa la CLI.
    Devuelve la respuesta como texto.
    """
   
    try:
            # Usar una API genérica: ollama.chat(...) o similar
            # Intentamos varias firmas comunes para ser robustos
            if hasattr(ollama, "chat"):
                print("llamada1")
                resp = ollama.chat(model=model_name, messages=prompt)
                # resp puede ser dict o str
                if isinstance(resp, dict):
                    return resp.get("message", {}).get("content", "").strip()
                else:
                    return resp.message.content.strip()
            else:
                # No reconocemos la API; fallback a CLI
                raise RuntimeError("La librería 'ollama' está presente pero su API no es conocida.")
    except Exception as e:
            # Fallback a CLI si la biblioteca falla
            print(f"ollama lib error, fallback a CLI: {e}")



def _handle_submit(model_name: str, timeout: int = 60):
    """Callback to handle form submit: read user_input from session_state, call Ollama, append messages and clear input."""
    user_input_val = st.session_state.get('user_input', '')
    if not user_input_val:
        return
    # Añadir mensaje de usuario
    st.session_state.messages.append({"role": "user", "content": user_input_val})
    response_text = None
    try:
        response_text = call_ollama(st.session_state.messages, model_name, timeout=timeout)
    except Exception as e_cli:
        response_text = f"Error llamando a Ollama via CLI: {e_cli}"

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    # Clear the input field in session_state (safe inside callback)
    st.session_state['user_input'] = ''


# Use a form with a submit callback to handle sending and clearing reliably
with st.form("chat_form"):
    user_input = st.text_input("Tu mensaje:", key="user_input")
    # form_submit_button supports on_click; pass the model name via args
    send = st.form_submit_button("Enviar", on_click=_handle_submit, args=(model,))
  

# Display messages
for m in st.session_state.messages:
    role = m.get("role")
    content = m.get("content")
    if role == "user":
        st.markdown(f"**Tú:** {content}")
    else:
        st.markdown(f"**Ollama:** {content}")


# Small footer
st.write("\n---\nChat creado con Ollama y Streamlit")
