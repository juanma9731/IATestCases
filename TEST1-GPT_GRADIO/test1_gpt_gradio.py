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
import subprocess
import gradio as gr

# Modelo por defecto (ajustar según lo que tenga instalado en Ollama)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")


def generate_with_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 60) -> str:
    """Llama a la CLI de Ollama y devuelve la salida como texto.
    Requiere que el comando `ollama` esté en PATH y que el modelo esté instalado localmente.
    """
    # Construir comando como lista para evitar problemas de shell
    cmd = ["ollama", "run", model, prompt]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode == 0:
            # Normalmente la respuesta está en stdout
            return proc.stdout.strip()
        else:
            return f"[Error invoking ollama] {proc.stderr.strip()}"
    except FileNotFoundError:
        return "[Error] Comando 'ollama' no encontrado. Asegúrese de que Ollama esté instalado y en PATH."
    except subprocess.TimeoutExpired:
        return "[Error] La llamada a Ollama expiró (timeout)."


def respond(message, chat_history, model=OLLAMA_MODEL):
    """Maneja una nueva entrada del usuario y actualiza el historial de chat."""
    chat_history = chat_history or []
    # Añadir mensaje del usuario al historial
    chat_history.append(("Usuario", message))

    # Preparar prompt concatenando el historial para dar contexto simple al modelo
    conversation = []
    for speaker, text in chat_history:
        conversation.append(f"{speaker}: {text}")
    prompt = "\n".join(conversation) + "\nAssistant:"

    # Llamar a Ollama
    response = generate_with_ollama(prompt, model=model)

    # Añadir respuesta al historial
    chat_history.append(("Assistant", response))

    # Devuelve el historial actualizado y limpia el cuadro de texto
    return chat_history, ""


with gr.Blocks(title="Chat con Ollama (local)") as demo:
    gr.Markdown("## Interfaz estilo ChatGPT usando Ollama local")

    with gr.Row():
        model_input = gr.Textbox(label="Modelo Ollama (usar el nombre tal cual)", value=OLLAMA_MODEL)
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Escribe tu mensaje aquí...", show_label=False)
    send = gr.Button("Enviar")

    # Conectar eventos
    send.click(respond, inputs=[msg, chatbot, model_input], outputs=[chatbot, msg])
    msg.submit(respond, inputs=[msg, chatbot, model_input], outputs=[chatbot, msg])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
