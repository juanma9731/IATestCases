"""
tres3B_gpt_chainlit.py

Versión alternativa que usa la librería Python de Ollama (si está disponible)
en lugar de invocar el CLI por subprocess.

Comportamiento principal:
 - Mantiene un historial global como lista de diccionarios: {'role': 'user'|'assistant'|'system', 'content': str}
 - Al enviar la petición al modelo usa la interfaz de la librería (si existe)
   y pasa la lista de mensajes (no un único prompt concatenado).
 - Variables de entorno:
     OLLAMA_MODEL: modelo por defecto (ej: 'llama2')
     OLLAMA_SYSTEM_PROMPT: (opcional) prompt system inicial

Uso:
  chainlit run tres3B_gpt_chainlit.py

Nota: adapta la función `call_ollama_lib` según la API exacta de la librería
de Ollama que tengas instalada; el código intenta varios patrones y admite
respuestas en distintos formatos.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any

import chainlit as cl
import ollama

# Historial global: lista de dicts con keys: role, content
HISTORY: List[Dict[str, str]] = []


def _append_history(role: str, content: str, max_turns: int) -> None:
    HISTORY.append({"role": role, "content": content})
    max_msgs = max_turns * 2
    if len(HISTORY) > max_msgs:
        del HISTORY[0 : len(HISTORY) - max_msgs]


def _build_messages(system_prompt: Optional[str]) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})

    msgs.extend(HISTORY)
    return msgs


async def call_ollama_lib(messages: List[Dict[str, str]], model: str) -> str:
    """Intenta usar la librería Python de Ollama para generar una respuesta

    El comportamiento exacto depende de la versión de la librería. Aquí
    intentamos varios patrones conocidos y parseamos el resultado de forma
    flexible.
    """
    

    # Pattern 1: librería con función 'chat' o 'generate' estilo simple
    try:
        if hasattr(ollama, "chat"):
            print("call ollama lib chat")
            resp = ollama.chat(model=model, messages=messages)
            if isinstance(resp, dict):
                    return resp.get("message", {}).get("content", "").strip()
            else:
                    return resp.message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error al invocar la librería Ollama: {e}")


@cl.on_message
async def main(message):
    # Normalizar prompt
    if hasattr(message, "content"):
        prompt = message.content
    else:
        prompt = str(message)

    if not prompt or not prompt.strip():
        await cl.Message(content="Escribe algo para enviar al modelo.").send()
        return

    max_turns = int(os.getenv("OLLAMA_HISTORY_TURNS", "6"))
    system_prompt = os.getenv("OLLAMA_SYSTEM_PROMPT")
    model = os.getenv("OLLAMA_MODEL", "llama2")

    # Añadir mensaje del usuario al historial (role/content dicts)
    _append_history("user", prompt, max_turns)

    # Construir la lista de mensajes (system + historial)
    messages = _build_messages(system_prompt)

    await cl.Message(content="Procesando con la librería Ollama...").send()

    try:
        resp_text = await asyncio.to_thread(lambda: asyncio.run(call_ollama_lib(messages, model)))
    except RuntimeError as e:
        await cl.Message(content=f"Error al invocar librería Ollama: {e}").send()
        return
    except Exception as e:
        await cl.Message(content=f"Error inesperado: {e}").send()
        return

    # Añadir respuesta al historial
    _append_history("assistant", resp_text, max_turns)

    await cl.Message(content=resp_text).send()


if __name__ == "__main__":
    print("Ejecuta 'chainlit run tres3B_gpt_chainlit.py' para iniciar esta variante (usa la librería Ollama si está disponible).")
