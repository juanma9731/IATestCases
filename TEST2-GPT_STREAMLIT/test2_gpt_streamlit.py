import streamlit as st
import subprocess
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




def call_ollama_cli(prompt: str, model_name: str, timeout: int = 60) -> str:
    """Llama a ollama CLI usando subprocess.run(['ollama','run', model, prompt]) y devuelve la respuesta de texto.
    Usa capture_output y encoding utf-8 tal como solicitaste.
    """
    try:
        # Construir comando como lista para evitar problemas de shell
        cmd = ["ollama", "run", model_name, prompt]
        proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(f"Ollama CLI error: {proc.stderr}")
        return proc.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError("Comando 'ollama' no encontrado. Instala Ollama y asegúrate de que esté en PATH.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("La llamada a Ollama via CLI expiró (timeout).")


def _handle_submit(model_name: str, timeout: int = 60):
    """Callback to handle form submit: read user_input from session_state, call Ollama, append messages and clear input."""
    user_input_val = st.session_state.get('user_input', '')
    if not user_input_val:
        return
    # Añadir mensaje de usuario
    st.session_state.messages.append({"role": "user", "content": user_input_val})
    # Concatenate conversation into a single prompt for CLI
    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    response_text = None
    try:
        response_text = call_ollama_cli(prompt, model_name, timeout=timeout)
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
