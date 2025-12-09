# 🕵️‍♂️ Interview Assistant (AI Powered)

![Status](https://img.shields.io/badge/Status-Operational-green) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![AI](https://img.shields.io/badge/Powered%20by-Gemini-orange)

An **advanced, stealthy AI assistant** designed to help you ace technical interviews in real-time. It listens to audio, captures screen regions, and provides instant, concise answers using Google's Gemini Flash model.

## ✨ Features

- **🎙️ Real-Time Transcription**: Listens to interview questions via microphone.
- **👁️ Vision Mode (Snapshot)**: Capture coding problems or diagrams from your screen for instant analysis.
- **👻 Ninja Mode**: Adjustable window transparency (Opacity Slider) to stay discreet.
- **🚨 Panic Button (F9)**: Instantly hide the entire application in case of emergency.
- **📝 Rich Code View**: Answers displayed in a scrollable, dark-mode code editor with syntax highlighting font.
- **🧠 Refinement**: Buttons to **Summarize (➖)** or **Expand (➕)** the AI's answer on the fly.
- **💾 Auto-Logging**: Automatically saves your interview Q&A session to a text file for post-interview review.
- **⌨️ Stealth Chat**: Silent text input mode for when you can't speak.

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/interview-assistant.git
    cd interview-assistant
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup API Key**:
    - Create a `.env` file in the root directory.
    - Add your Google Gemini API key:
      ```env
      GOOGLE_API_KEY=your_api_key_here
      ```

## 🛠️ Usage

### Running form Source
```bash
python main.py
```

### Running the Executable (Windows)
If you built the executable:
1.  Go to the `dist` folder.
2.  Ensure `.env` is present next to the `.exe`.
3.  Run `InterviewAssistant.exe`.

### Controls
| Key/Button | Action |
|Data|Description|
|---|---|
| **F8** | Toggle Listening (Pause/Resume) |
| **F9** | **Panic Mode** (Hide/Show Window) |
| **📸** | Take Screen Snapshot |
| **⌨️** | Toggle Chat Input |
| **Slider** | Adjust Transparency |

## 📦 Build Standalone .exe
To create a portable executable yourself:
```bash
python build.py
```
*Artifacts will be in `dist/` folder.*

## ⚠️ Disclaimer
This tool is intended for educational purposes and interview preparation assistance. Use responsibly and ethically.

---
*Built with Python, CustomTkinter, and Google Gemini.*
