const { app, BrowserWindow, ipcMain, screen, Tray, Menu, nativeImage, session, shell } = require('electron');
const { exec } = require('child_process');
const path = require('path');
const http = require('http');
const fs   = require('fs');

let mainWindow = null;
let tray       = null;
let flaskProc  = null;

const WIDGET_W = 300, WIDGET_H = 480;
const PANEL_W  = 680, PANEL_H  = 520;

// ─── Auto-start: copies .vbs launcher to Windows Startup folder ───
function setupAutoStart() {
  try {
    const startupDir = path.join(process.env.APPDATA,
      'Microsoft','Windows','Start Menu','Programs','Startup');
    const vbsTarget  = path.join(startupDir, 'RAVEN.vbs');
    const batPath    = path.join(__dirname, '..', 'START_RAVEN.bat');
    const vbs = `Set WShell = CreateObject("WScript.Shell")\r\nWShell.Run """${batPath}""", 0, False`;
    fs.writeFileSync(vbsTarget, vbs);
    console.log('✅ Auto-start set:', vbsTarget);
  } catch(e) {
    console.error('Auto-start setup failed:', e.message);
  }
}

// ─── Start Flask backend ───
function startFlask() {
  const dir = path.join(__dirname, '..', 'Jarvis');
  flaskProc = exec('python app.py', { cwd: dir });
  flaskProc.stdout.on('data', d => process.stdout.write('[Flask] '+d));
  flaskProc.stderr.on('data', d => process.stderr.write('[Flask] '+d));
}

// ─── Wait for Flask to respond ───
function waitForFlask(cb, tries=30) {
  http.get('http://localhost:5000/', () => cb())
    .on('error', () => tries>0 ? setTimeout(()=>waitForFlask(cb,tries-1),500) : cb());
}

// ─── Create the always-on-top window ───
function createWindow() {
  const { width:sw, height:sh } = screen.getPrimaryDisplay().workAreaSize;

  // Grant ALL permissions (mic, camera, etc.)
  session.defaultSession.setPermissionRequestHandler((wc, perm, cb) => cb(true));
  session.defaultSession.setPermissionCheckHandler(() => true);

  mainWindow = new BrowserWindow({
    width:       WIDGET_W,
    height:      WIDGET_H,
    x:           sw - WIDGET_W - 16,
    y:           sh - WIDGET_H - 16,
    frame:       false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: false,
    resizable:   false,
    hasShadow:   false,
    closable:    false,
    webPreferences: {
      nodeIntegration:  true,
      contextIsolation: false,
      webSecurity:      false,
      preload:          path.join(__dirname, 'preload.js'),
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'widget.html'));
  mainWindow.setVisibleOnAllWorkspaces(true);

  // Stay on top and ALWAYS VISIBLE — check every second
  setInterval(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setAlwaysOnTop(true, 'screen-saver');
      if (!mainWindow.isVisible()) mainWindow.show(); // force visible if somehow hidden
    }
  }, 1000);
}

// ─── Tray icon ───
function createTray() {
  const img = nativeImage.createFromDataURL(
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAASklEQVQ4jWNgGAWDDfz//5+BkgEMDAyMlBowygCjDhg1wKgDRh0w6oBRB4w6YNQBow4YdcCoA0YdMOqAUQeMOmDUAaMOGHEAADqUCgU3tDd3AAAAAElFTkSuQmCC'
  );
  tray = new Tray(img);
  tray.setToolTip('R.A.V.E.N — AI Assistant');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: '⬡ R.A.V.E.N Assistant', enabled: false },
    { type: 'separator' },
    { label: '✅ Always on screen', enabled: false },
    { label: '✅ Launches on startup', enabled: false },
    { type: 'separator' },
    { label: '❌ Quit Raven completely', click: () => { flaskProc?.kill(); app.exit(0); } }
  ]));
  // Tray click does nothing — robot is always visible
  tray.on('click', () => mainWindow?.show());
}

// ─── IPC handlers ───
ipcMain.on('expand-panel', () => {
  if (!mainWindow) return;
  const {width:sw,height:sh} = screen.getPrimaryDisplay().workAreaSize;
  mainWindow.setSize(PANEL_W, PANEL_H);
  mainWindow.setPosition(sw-PANEL_W-16, sh-PANEL_H-16);
});
ipcMain.on('collapse-panel', () => {
  if (!mainWindow) return;
  const {width:sw,height:sh} = screen.getPrimaryDisplay().workAreaSize;
  const x = sw - WIDGET_W - 16;
  const y = sh - WIDGET_H - 16;
  mainWindow.setSize(WIDGET_W, WIDGET_H);
  mainWindow.setPosition(x, y);
  mainWindow.show(); // force visible after resize — Windows sometimes hides on resize
});
// hide-window disabled — robot is always visible
ipcMain.on('drag-window', (e,{x,y}) => mainWindow?.setPosition(Math.round(x), Math.round(y)));
ipcMain.on('close-app',   ()        => { flaskProc?.kill(); app.exit(0); });

// ─── Mic flags for Chromium ───
app.commandLine.appendSwitch('enable-speech-dispatcher');
app.commandLine.appendSwitch('use-fake-ui-for-media-stream');

// ─── Launch ───
app.whenReady().then(() => {
  setupAutoStart();
  startFlask();
  createTray();
  waitForFlask(createWindow);
});

// Don't quit when all windows closed — keep tray alive
app.on('window-all-closed', e => e.preventDefault());
app.on('before-quit', () => flaskProc?.kill());