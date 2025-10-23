# tres3_gpt_chainlit — Chainlit + Ollama (interfaz mínima)

Este repo contiene una aplicación mínima de Chainlit que actúa como chatbot
y delega la generación de texto a Ollama mediante llamadas al ejecutable `ollama`
desde el backend (subprocess).

Requisitos
--

- Python 3.8+
- Ollama instalado y accesible en PATH (https://ollama.ai)
- Modelo en Ollama (por ejemplo: llama2) según tus preferencias

Instalación (PowerShell)
--

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Variables de entorno importantes
--

- OLLAMA_MODEL: nombre del modelo a usar (por defecto: llama2)
- OLLAMA_CMD_TEMPLATE: (opcional) template del comando usado para invocar Ollama.
  Debe contener {model} y {prompt} y será separado por espacios. Ejemplo:

  $env:OLLAMA_CMD_TEMPLATE = 'ollama run {model} --prompt {prompt} --option foo'

Uso (ejecutar la app Chainlit)
--

Desde PowerShell:

```powershell
# (opcional) establecer el modelo
#$env:OLLAMA_MODEL = 'llama2'

chainlit run tres3_gpt_chainlit.py
```

Por defecto Chainlit levantará una interfaz local (normalmente http://localhost:8788)
donde podrás chatear con el bot.

Notas y recomendaciones
--

- Asegúrate de que el ejecutable `ollama` esté en tu PATH y que el modelo exista
  en tu instalación de Ollama. Por ejemplo, para algunos modelos puede ser necesario
  descargar/pull antes de usarlos.
- El archivo `tres3_gpt_chainlit.py` usa llamadas sincrónicas a `subprocess` pero
  las ejecuta en un thread separado mediante `asyncio.to_thread` para no bloquear
  el event loop de Chainlit.
- Si necesitas interacción más avanzada (streaming, system prompts, mensajes
  estructurados), se puede extender la plantilla y adaptar la forma de invocar
  el CLI de Ollama o pasar a su SDK/HTTP API si corresponde.

Contacto
--

Si quieres que adapte esto a un flujo de mensajes con historial, o que integre
variables adicionales (temperature, max_tokens) en la plantilla del comando,
dímelo y lo añado.
