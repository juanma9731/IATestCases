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


def stream_with_ollama(messages, model: str = OLLAMA_MODEL):
    """Return an iterator that yields partial chunks from Ollama chat streaming.

    Each yielded item is the raw chunk returned by the Ollama client. The
    caller should handle dict shapes and error objects.
    """
    if chat is None:
        # Yield a single error object so caller can display it
        yield {"error": "[Error] Python package 'ollama' no está instalado. Instale con: pip install ollama"}
        return

    try:
        for part in chat(model=model, messages=messages, stream=True):
            yield part
    except ResponseError as e:
        err = getattr(e, "error", str(e))
        yield {"error": f"[Error invoking ollama] {err}"}
    except Exception as e:
        yield {"error": f"[Error] Unexpected error calling ollama: {e}"}


def respond(message, chat_history, model=OLLAMA_MODEL):
    """Generator-based responder that streams partial assistant output to Gradio.

    Yields tuples matching the Gradio outputs: (chat_history, textbox_value).
    The function appends the user's message, inserts a placeholder assistant
    message, then updates that assistant message as chunks arrive from the
    Ollama streaming API.
    """
    chat_history = chat_history or []

    # Append the user message
    chat_history.append({"role": "user", "content": message})

    # Insert a placeholder assistant message we will update in-place
    chat_history.append({"role": "assistant", "content": ""})

    # Immediately yield so UI shows the user's message and an empty assistant
    yield chat_history, ""

    # Stream from Ollama
    stream = stream_with_ollama(chat_history, model=model)

    assistant_text = ""
    for part in stream:
        # If the stream yields an error dict, show it and finish
        if isinstance(part, dict) and part.get("error"):
            chat_history[-1]["content"] = part.get("error")
            yield chat_history, ""
            return

        # Extract content from the chunk. Ollama streaming chunks typically
        # have the shape {'message': {'content': '...'}}; but be permissive.
        chunk_text = ""
        try:
            if isinstance(part, dict):
                msg = part.get("message") or {}
                # preserve original whitespace (do not strip) so fragments join correctly
                chunk_text = msg.get("content") if msg.get("content") is not None else part.get("content") or ""
            else:
                # part may be an object with .message.content; preserve whitespace
                try:
                    chunk_text = part.message.content
                except Exception:
                    chunk_text = str(part)
        except Exception:
            chunk_text = str(part)

        # Append chunk as-is (no extra space) so tokens form full words across chunks
        assistant_text += chunk_text
        chat_history[-1]["content"] = assistant_text

        # Yield updated history so Gradio can render the partial response
        yield chat_history, ""

    # Final yield to ensure UI shows the full response (redundant but safe)
    yield chat_history, ""


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
    demo.launch(server_name="0.0.0.0", server_port=7862)
