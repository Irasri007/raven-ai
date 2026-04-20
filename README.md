# R.A.V.E.N 🤖
### Responsive Adaptive Virtual Engineered Navigator

> An always-on-top AI desktop assistant that lives permanently on your screen — voice-controlled, Gemini-powered, and built with Python + Electron.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Electron](https://img.shields.io/badge/Electron-29-47848F?style=flat-square&logo=electron)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google)
![Flask](https://img.shields.io/badge/Flask-REST_API-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Preview

Raven sits in the **bottom-right corner** of your screen — always on top of every window. Click the chat button to expand a full AI assistant panel on the left. Click the mic button on Raven's chest to speak a command.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Always On Screen** | Transparent floating widget, always on top of every app |
| 🎙️ **Voice Input** | Click the mic on Raven's chest — speak your command |
| 🔊 **Speaks Back** | Text-to-speech with animated mouth lip-sync |
| ⚡ **Gemini 2.5 AI** | Full LLM responses for any question |
| 🌐 **Smart Commands** | Open YouTube, search Google, generate images, check weather and more |
| 🗣️ **Bilingual** | Understands English and Hindi |
| 📋 **Task Manager** | Add and view your todo list by voice |
| 💾 **Chat History** | All conversations saved to SQLite database |
| 🚀 **Auto Startup** | Launches automatically when Windows boots |
| 🔐 **User Auth** | Login/register system with secure password hashing |

---

## 🛠️ Tech Stack

**Backend**
- Python 3.10+
- Flask (REST API)
- SQLite (chat history & auth)
- SpeechRecognition + PyAudio (voice input)
- Google Gemini 2.5 Flash (AI responses)
- scikit-learn (intent classification model)

**Frontend / Desktop**
- Electron.js 29 (desktop wrapper)
- HTML + CSS + Vanilla JavaScript
- Web Speech API (TTS)
- SVG robot with CSS animations

---

## 📁 Project Structure

```
raven-desktop/
├── Jarvis/                     # Python backend
│   ├── app.py                  # Flask API server (main backend)
│   ├── main.py                 # Terminal version of Raven
│   ├── auth.py                 # User registration & login
│   ├── database.py             # SQLite connection & setup
│   ├── chat_logger.py          # Save/retrieve chat history
│   ├── intent_model.py         # Train the intent classifier
│   ├── intent_model.pkl        # Trained ML model
│   ├── sentiment.py            # Sentiment analysis
│   ├── user_config.py          # User preferences
│   └── todo.txt                # Task storage
│
├── electron/                   # Electron desktop app
│   ├── main.js                 # Window manager, Flask launcher, IPC
│   ├── widget.html             # The actual UI (robot + chat panel)
│   ├── preload.js              # IPC bridge between JS and Electron
│   ├── package.json            # Electron config & build settings
│   └── assets/                 # Icons and images
│
├── START_RAVEN.bat             # Double-click to launch everything
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- [Python 3.10+](https://python.org)
- [Node.js 18+](https://nodejs.org)
- A free [Gemini API key](https://aistudio.google.com)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/raven-ai.git
cd raven-ai
```

### 2. Install Python dependencies
```bash
cd Jarvis
pip install flask flask-cors requests wikipedia speechrecognition pyaudio pyttsx3 langdetect scikit-learn plyer pyautogui pywhatkit
```

### 3. Add your Gemini API key
Open `Jarvis/app.py` and replace:
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```
Get a free key at [aistudio.google.com](https://aistudio.google.com) → Get API Key

### 4. Install Electron dependencies
```bash
cd ../electron
npm install
```

### 5. Launch Raven
```bash
# Option A — double click
START_RAVEN.bat

# Option B — terminal
cd electron
npx electron .
```

Raven will appear in the **bottom-right corner** of your screen. 🎉

---

## 🎮 Usage

### Voice Commands
Click the **🎙️ mic button** on Raven's chest and speak:

| Command | What Raven Does |
|---|---|
| `"Hello"` | Greets you |
| `"What time is it?"` | Tells the current time |
| `"Open YouTube"` | Opens YouTube in browser |
| `"Play music"` | Plays a random song |
| `"Search [topic]"` | Googles it |
| `"Wikipedia [topic]"` | Fetches Wikipedia summary |
| `"Generate image of [X]"` | Creates AI image |
| `"Add task [task name]"` | Adds to your todo list |
| `"Show tasks"` | Lists your tasks |
| `"Open Gmail"` | Opens Gmail |
| `"Open Spotify"` | Opens Spotify |
| `"What is [anything]?"` | Asks Gemini AI |

### Text Commands
Click the **💬 button** on Raven to open the chat panel and type anything.

### Controls
| Button | Action |
|---|---|
| **▶** | Open chat panel |
| **◀ / ✕** | Close chat panel |
| 🟡 **Yellow dot** | Always on screen (permanent) |
| 🔴 **Red dot** | Quit Raven completely |
| **Drag** the top strip | Move Raven anywhere |
| **Tray icon** | Right-click for options |

---

## 🔧 Configuration

### Change the AI Model
In `Jarvis/app.py`:
```python
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)
```
Available models: `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-2.5-pro`

### Change Window Position
In `electron/main.js`:
```js
const WIDGET_W = 300, WIDGET_H = 480;  // widget size
x: sw - WIDGET_W - 16,  // distance from right edge
y: sh - WIDGET_H - 16,  // distance from bottom edge
```

### Disable Auto-Startup
In `electron/main.js`, comment out:
```js
// setupAutoStart();
```

---

## 📦 Build Installer (.exe)

To build a Windows installer:

```bash
cd electron
npm install electron-builder --save-dev
npx electron-builder --win   # Run as Administrator
```

Output: `electron/dist/RAVEN Setup 1.0.0.exe`

> **Note:** Run PowerShell as Administrator for the build to succeed.

---

## 🚀 Deployment

### Host the Website (GitHub Pages)
1. Upload `raven-website.html` as `index.html` to your GitHub repo
2. Go to Settings → Pages → set source to `main`
3. Live at `https://yourusername.github.io/raven-ai`

### Share the Installer (GitHub Releases)
1. Go to your repo → Releases → Create new release
2. Upload `RAVEN Setup 1.0.0.exe`
3. Copy the download URL into your website

---

## ⚠️ Known Limitations

- **Windows only** — Electron app is built for Windows 10/11
- **Python required** — users need Python installed (unless bundled with PyInstaller)
- **Gemini API key** — each user needs their own free key, or you share yours (1500 req/day limit)
- **Voice recognition** — requires internet (uses Google Speech API)
- **Mic in Electron** — uses Python backend for speech recognition to avoid browser restrictions

---

## 🗺️ Roadmap

- [ ] Bundle Python with PyInstaller (no Python install needed)
- [ ] First-launch API key setup screen
- [ ] Wake word detection (`"Hey Raven"`)
- [ ] Conversation memory across sessions
- [ ] LangChain agent for multi-step tasks
- [ ] macOS support
- [ ] Custom themes

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use, modify and distribute.

---

## 👩‍💻 Author

**Ira** — Built with Python, Electron, and a lot of debugging 🐦‍⬛

> *"Just a rather very... wait, that's the old name."*

---

<div align="center">
  <strong>R.A.V.E.N</strong> — Responsive Adaptive Virtual Engineered Navigator<br/>
  <sub>Built with ❤️ using Python · Flask · Electron · Gemini AI</sub>
</div>
