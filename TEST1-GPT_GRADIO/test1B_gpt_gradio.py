"""
Interfaz estilo ChatGPT con Gradio que envía las preguntas al LLM local ejecutándose con Ollama.

Requisitos:
- Tener Ollama instalado y el modelo descargado (por ejemplo: `ollama pull <model>`).
- Tener gradio instalado: pip install gradio

Modo de funcionamiento:
- Usa la CLI `ollama run <model> "prompt"` para obtener la respuesta del modelo local.
- Ajustar la variable OLLAMA_MODEL o el campo de la UI si se desea otro modelo.
"""

import os
import gradio as gr

# Try to import the official Ollama Python client. If it's not available,
# we'll handle it later and return a helpful error message from the
# generation function instead of crashing at import time.
try:
    from ollama import chat, ResponseError
except Exception:
    chat = None
    ResponseError = None

# Modelo por defecto (ajustar según lo que tenga instalado en Ollama)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")


def generate_with_ollama(prompt , model: str = OLLAMA_MODEL, timeout: int = 60) -> str:
    """Call the Ollama Python client to get a model response.

    If the `ollama` package isn't installed this function returns a helpful
    message. It returns the assistant content as plain text on success, or an
    error string starting with [Error ...] on failure.
    """
    if chat is None:
        return (
            "[Error] Python package 'ollama' no está instalado. "
            "Instale con: pip install ollama"
        )

    try:
        # Use the chat API. Ensure `messages` is a list of dicts with 'role' and 'content'.
        messages = prompt
        if isinstance(prompt, list):
            # Normalize messages to only role/content
            messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in prompt]
        else:
            # If a single string was provided, wrap as a single user message
            messages = [{"role": "user", "content": str(prompt)}]

        response = chat(model=model, messages=messages)

        # Response can be dict-like or have attribute access depending on version.
        # Try dictionary access first.
        if isinstance(response, dict):
            return response.get("message", {}).get("content", "").strip()

        # Fallback to attribute access
        try:
            return response.message.content.strip()
        except Exception:
            # As a last resort, convert to string
            return str(response).strip()

    except ResponseError as e:
        # Ollama client raises ResponseError for HTTP/stream errors
        err = getattr(e, "error", str(e))
        return f"[Error invoking ollama] {err}"
    except Exception as e:
        return f"[Error] Unexpected error calling ollama: {e}"


def respond(message, chat_history, model=OLLAMA_MODEL):
    """Maneja una nueva entrada del usuario y actualiza el historial de chat en formato OpenAI (role/content)."""
    chat_history = chat_history or []
    # Añadir mensaje del usuario al historial (role: user)
    chat_history.append({"role": "user", "content": message})

    # Preparar prompt concatenando el historial para dar contexto simple al modelo
    """conversation = []
    for msg in chat_history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        speaker = "Usuario" if role == "user" else "Assistant"
        conversation.append(f"{speaker}: {content}")
    prompt = "\n".join(conversation) + "\nAssistant:"
    """

    # Llamar a Ollama
    response = generate_with_ollama(chat_history, model=model)

    # Añadir respuesta al historial (role: assistant)
    chat_history.append({"role": "assistant", "content": response})

    # Devuelve el historial actualizado y limpia el cuadro de texto
    return chat_history, ""


with gr.Blocks(title="Chat con Ollama (local)") as demo:
    gr.Markdown("## Interfaz estilo ChatGPT usando Ollama local")

    with gr.Row():
        model_input = gr.Textbox(label="Modelo Ollama (usar el nombre tal cual)", value=OLLAMA_MODEL)
    # Usar el formato moderno de mensajes
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Escribe tu mensaje aquí...", show_label=False)
    send = gr.Button("Enviar")

    # Conectar eventos
    send.click(respond, inputs=[msg, chatbot, model_input], outputs=[chatbot, msg])
    msg.submit(respond, inputs=[msg, chatbot, model_input], outputs=[chatbot, msg])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
