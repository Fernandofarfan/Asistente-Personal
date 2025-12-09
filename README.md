# 🕵️‍♂️ Asistente de Entrevistas (Con IA)

![Estado](https://img.shields.io/badge/Estado-Operativo-green) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![IA](https://img.shields.io/badge/Powered%20by-Gemini-orange)

Un **asistente de IA avanzado y discreto** diseñado para ayudarte a superar entrevistas técnicas en tiempo real. Escucha preguntas de audio, captura regiones de la pantalla y proporciona respuestas instantáneas y concisas utilizando el modelo Gemini Flash de Google.

## ✨ Características

- **🎙️ Transcripción en Tiempo Real**: Escucha las preguntas de la entrevista a través del micrófono.
- **👁️ Modo Visión (Captura)**: Captura problemas de código o diagramas de tu pantalla para un análisis instantáneo.
- **👻 Modo Ninja**: Transparencia de ventana ajustable (Control Deslizante) para mantener la discreción.
- **🚨 Botón de Pánico (F9)**: Oculta instantáneamente toda la aplicación en caso de emergencia.
- **📝 Vista de Código Enriquecida**: Respuestas mostradas en un editor de código en modo oscuro con desplazamiento y fuente monoespaciada.
- **🧠 Refinamiento**: Botones para **Resumir (➖)** o **Expandir (➕)** la respuesta de la IA sobre la marcha.
- **💾 Registro Automático**: Guarda automáticamente tu sesión de preguntas y respuestas en un archivo de texto para repasar después.
- **⌨️ Chat Sigiloso**: Modo de entrada de texto silencioso para cuando no puedes hablar.

## 🚀 Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tuusuario/asistente-personal.git
    cd asistente-personal
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar API Key**:
    - Crea un archivo `.env` en el directorio raíz.
    - Añade tu clave API de Google Gemini:
      ```env
      GOOGLE_API_KEY=tu_clave_api_aqui
      ```

## 🛠️ Uso

### Ejecutar desde Código Fuente
```bash
python main.py
```

### Ejecutar el Ejecutable (Windows)
Si has construido el ejecutable:
1.  Ve a la carpeta `dist`.
2.  Asegúrate de que el archivo `.env` esté presente junto al `.exe`.
3.  Ejecuta `InterviewAssistant.exe`.

### Controles
| Tecla/Botón | Acción |
|---|---|
| **F8** | Alternar Escucha (Pausar/Reanudar) |
| **F9** | **Modo Pánico** (Ocultar/Mostrar Ventana) |
| **📸** | Tomar Captura de Pantalla |
| **⌨️** | Alternar Chat de Texto |
| **Slider** | Ajustar Transparencia |

## 📦 Crear Ejecutable Portátil (.exe)
Para crear el ejecutable tú mismo:
```bash
python build.py
```
*Los artefactos estarán en la carpeta `dist/`.*

## ⚠️ Aviso Legal
Esta herramienta está destinada a fines educativos y de ayuda en la preparación de entrevistas. Úsala de manera responsable y ética.

---
*Construido con Python, CustomTkinter y Google Gemini.*
