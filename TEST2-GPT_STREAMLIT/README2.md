# Chat con Ollama + Streamlit

Pequeña app de ejemplo para crear un chatbot usando Ollama y Streamlit.

Requisitos:
- Ollama instalado y con un modelo disponible (ej: llama2). Ver https://ollama.ai
- Python 3.8+

Instalación:

1. Crear un entorno virtual y activarlo (PowerShell):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecutar la app:

```powershell
streamlit run app.py
```

4. Si no creas entorno virtual usa: python -m
 streamlit run app.py


Uso:
- La app intentará primero llamar a la API HTTP de Ollama en http://localhost:11434/chat.
- Si falla, usará el comando CLI `ollama chat <modelo> --prompt "..."` como fallback.
- Cambia el modelo en la barra lateral o exporta la variable de entorno `OLLAMA_MODEL`.

Notas:
- Ajusta timeout y manejo de errores según necesites.
- Este ejemplo es minimal y no maneja streaming de respuestas ni tokenización avanzada.
