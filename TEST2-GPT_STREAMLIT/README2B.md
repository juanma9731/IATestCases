# Test2B Chat con Ollama (biblioteca Python)

Este script `test2B_gpt_streamlit.py` es una versión de ejemplo que usa la librería Python de Ollama cuando está disponible, y hace fallback a la CLI `ollama run` si no lo está.

Requisitos:
- Python 3.8+
- Ollama instalado localmente (si planeas usar la CLI como fallback)
- Preferiblemente instalar la librería Python `ollama` si está disponible para tu versión de Ollama.

Instalación y ejecución (PowerShell):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements2b.txt
streamlit run test2B_gpt_streamlit.py
```

Notas:
- El script intenta detectar la librería `ollama` e invocar `chat` o `Ollama().chat` si están presentes. Si no reconoce la API de la librería, recurre a la CLI.
- Ajusta la variable de entorno `OLLAMA_MODEL` o cambia el valor por defecto en el script para seleccionar el modelo.
- Este README asume que la librería `ollama` tiene una API HTTP/cliente; si tu instalación difiere, adapta el llamado dentro de `call_ollama()`.
