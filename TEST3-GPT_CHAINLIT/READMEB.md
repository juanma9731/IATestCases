# tres3B_gpt_chainlit — Chainlit + Ollama (librería Python)

Este fichero contiene una variante de la aplicación Chainlit que usa la
librería Python de Ollama en lugar de invocar el CLI con subprocess.

Características principales
- Mantiene un historial global en memoria como una lista de diccionarios
  con la forma {"role": "user"|"assistant"|"system", "content": "..."}.
- Envía al modelo una lista de mensajes (no un string único concatenado).
- Intenta adaptarse a varias APIs posibles de la librería `ollama` y proporciona
  mensajes de error útiles si la librería no está instalada o su API difiere.

Variables de entorno
- OLLAMA_MODEL: modelo por defecto a usar (ej: 'llama2').
- OLLAMA_SYSTEM_PROMPT: prompt del sistema que se incluye antes del historial.
- OLLAMA_HISTORY_TURNS: número máximo de turnos a mantener (por defecto 6).

Instalación (PowerShell)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Instala la librería Python de Ollama si está disponible (ajusta el nombre):
# pip install ollama
```

Ejecución
```powershell
chainlit run tres3B_gpt_chainlit.py
```

Notas
- El código de `call_ollama_lib` intenta detectar varias formas comunes de
  invocar la librería (funciones `chat` o `generate`, o un cliente `Ollama`/`Client`).
  Dependiendo de la versión que tengas instalada puede ser necesario adaptar
  esa función a la API real.
- Si necesitas persistencia entre reinicios, cambia el almacenamiento de `HISTORY`
  por una base de datos o fichero.

Contacta si quieres que adapte el código a la API exacta de la librería Ollama
que tienes instalada (puedo modificar `call_ollama_lib` para usarla explícitamente).
