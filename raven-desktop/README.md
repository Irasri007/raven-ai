# R.A.V.E.N Desktop App

## 📁 Folder Structure
```
Raven_Desktop/
├── Jarvis/              ← Your existing Python backend (app.py etc.)
├── electron/            ← Electron desktop wrapper
│   ├── main.js          ← Window manager
│   ├── widget.html      ← The desktop widget UI
│   ├── preload.js       ← IPC bridge
│   └── package.json
└── START_RAVEN.bat      ← Double-click to launch everything
```

## ⚡ Requirements
1. **Python** — already installed (you're using it)
2. **Node.js** — download from https://nodejs.org (LTS version)
   - This is needed for Electron only

## 🚀 How to Run
1. Make sure your `Jarvis/` folder is in the same directory as `electron/`
2. Double-click **START_RAVEN.bat**
3. First launch: Electron installs automatically (~1 min)
4. Raven appears in the **bottom-right corner** of your screen

## 🎮 Controls
| Action | How |
|--------|-----|
| Open chat panel | Click 💬 button or green ⬡ button |
| Close chat panel | Click ✕ in panel or toggle button |
| Move widget | Drag the top strip of the robot column |
| Minimize | Click yellow − button |
| Quit | Click red ✕ button |
| Right-click tray icon | More options |

## 🔧 Notes
- Raven is **always on top** of all windows
- Flask backend starts **automatically** — no need to run `python app.py` separately
- Voice input works (Chrome's speech engine is built into Electron)
- The widget sits in the **bottom-right** of your screen by default
