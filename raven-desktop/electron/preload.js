const { ipcRenderer } = require('electron');

window.ravenBridge = {
  expand:   () => ipcRenderer.send('expand-panel'),
  collapse: () => ipcRenderer.send('collapse-panel'),
  hide:     () => ipcRenderer.send('hide-window'),
  close:    () => ipcRenderer.send('close-app'),
  drag:     (x, y) => ipcRenderer.send('drag-window', { x, y }),
};