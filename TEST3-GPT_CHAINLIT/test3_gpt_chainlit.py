"""
tres3_gpt_chainlit.py

App mínima de Chainlit para crear un chatbot que delega la generación de texto
a Ollama vía llamada a comando (subprocess).

Uso:
  - configurar la variable de entorno OLLAMA_MODEL (por ejemplo: "llama2")
  - opcional: OLLAMA_CMD_TEMPLATE para cambiar la forma del comando
    (por defecto se usa: ['ollama','run', model, '--prompt', prompt])
  - ejecutar: `chainlit run tres3_gpt_chainlit.py`

Notas:
  - Este archivo usa llamadas de bloqueo a través de asyncio.to_thread para no
    bloquear el loop de Chainlit.
  - Asegúrate de tener Ollama instalado y el modelo descargado/instalado localmente.
"""

import os
import subprocess
import asyncio
import shlex
from typing import Optional, List, Tuple

import chainlit as cl


def _call_ollama_sync(prompt: str, model: str) -> str:
    """Llama a Ollama usando subprocess de forma sincrónica.

    Por defecto construye el comando: ['ollama', 'run', model, '--prompt', prompt]
    Si quieres usar un template distinto, exporta OLLAMA_CMD_TEMPLATE con
    las variables {model} y {prompt} (se pasará a shell=False si es una lista
    separada por espacios; para seguridad se recomienda no usar shell=True).
    """

 
    cmd = ["ollama", "run", model, prompt]
    try:
        proc  = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=60)
        return proc.stdout.strip() or proc.stderr.strip() or "(sin salida)"
    except subprocess.CalledProcessError as e:
        # Devolver una descripción del error para mostrarla en la UI
        stderr = e.stderr.strip() if e.stderr else ""
        stdout = e.stdout.strip() if e.stdout else ""
        raise RuntimeError(f"Ollama retornó código {e.returncode}. stdout={stdout} stderr={stderr}")
    except FileNotFoundError:
        raise RuntimeError("No se encontró el ejecutable 'ollama' en PATH. Instala Ollama y asegúrate que esté en PATH.")


async def call_ollama(prompt: str, model: Optional[str] = None) -> str:
    """Wrapper asíncrono que ejecuta la llamada a Ollama en un thread.

    Args:
        prompt: texto del usuario
        model: modelo a usar (si no se pasa, se toma OLLAMA_MODEL o 'llama2')
    Returns:
        La respuesta textual devuelta por Ollama.
    """
    print("call ollama")
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    # Ejecutar en thread para evitar bloquear el event loop
    return await asyncio.to_thread(_call_ollama_sync, prompt, model)


# Simple historial en memoria (lista global de tuplas (role, content)).
_HISTORY: List[Tuple[str, str]] = []


def _append_history(role: str, content: str, max_turns: int):
    """Añade un (role, content) al historial global y recorta a max_turns."""
    _HISTORY.append((role, content))
    # Mantener solo los últimos (max_turns * 2) mensajes (user+assistant por turno)
    max_msgs = max_turns * 2
    if len(_HISTORY) > max_msgs:
        del _HISTORY[0 : len(_HISTORY) - max_msgs]


def _build_prompt_from_history(system_prompt: Optional[str]) -> str:
    parts: List[str] = []
    if system_prompt:
        parts.append(system_prompt.strip())

    for role, content in _HISTORY:
        if role == "user":
            parts.append(f"User: {content}")
        else:
            parts.append(f"Assistant: {content}")

    # Añadir una señal para que el modelo responda
    parts.append("Assistant:")
    return "\n".join(parts)


@cl.on_message
async def main(message):  # message puede ser str o un objeto Message de Chainlit
    """Handler principal que recibe mensajes del usuario en Chainlit.

    Algunos hooks de Chainlit pasan un objeto Message en lugar de una cadena.
    Normalizamos a texto aquí para evitar pasar un objeto Message a subprocess
    (que espera strings en la lista de argumentos).
    """
    print(message)
    # Normalizar el prompt a str
    if hasattr(message, "content"):
        prompt = message.content
    else:
        prompt = str(message)

    # Verificar prompt no vacío
    if not prompt or not prompt.strip():
        await cl.Message(content="Por favor escribe algo para enviar al modelo.").send()
        return

    # Opciones de historial
    max_turns = int(os.getenv("OLLAMA_HISTORY_TURNS", "10"))
    system_prompt = os.getenv("OLLAMA_SYSTEM_PROMPT")

    # Añadir el mensaje del usuario al historial global
    _append_history("user", prompt, max_turns)

    # Construir prompt que incluye el historial global
    assembled_prompt = _build_prompt_from_history(system_prompt)

    # Feedback inmediato
    await cl.Message(content="Procesando tu petición con Ollama...").send()

    try:
        response = await call_ollama(assembled_prompt)
    except Exception as e:
        # Mostrar error al usuario
        await cl.Message(content=f"Error al invocar Ollama: {e}").send()
        return

    # Guardar respuesta del assistant en el historial
    _append_history("assistant", response, max_turns)

    # Enviar la respuesta final
    await cl.Message(content=response).send()


if __name__ == "__main__":
    # Este módulo está pensado para ejecutarse con `chainlit run`.
    print("Ejecuta 'chainlit run tres3_gpt_chainlit.py' para iniciar la app de Chainlit.")
