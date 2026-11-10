const { app, BrowserWindow, dialog, session } = require('electron');
const path = require('node:path');
const { spawn } = require('node:child_process');
const http = require('node:http');

let backend;
let ownsBackend = false;
let mainWindow;
const isDev = !app.isPackaged;

function probeBackend() {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:8000/health', (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const health = JSON.parse(body);
          resolve(res.statusCode === 200 && health.database === 'connected');
        } catch { resolve(false); }
      });
    });
    req.setTimeout(900, () => req.destroy());
    req.on('error', () => resolve(false));
  });
}

function startBackend() {
  if (isDev) {
    backend = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], {
      cwd: path.join(__dirname, '../../backend'), windowsHide: true, stdio: 'inherit'
    });
  } else {
    const executable = path.join(process.resourcesPath, 'backend', 'voicegrocery-backend.exe');
    const databasePath = path.join(app.getPath('userData'), 'voicegrocery.db').replace(/\\/g, '/');
    backend = spawn(executable, [], { windowsHide: true, stdio: 'inherit', env: { ...process.env, DATABASE_URL: `sqlite:///${databasePath}` } });
  }
  ownsBackend = true;
}

async function waitForBackend(attempts = 40) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    if (await probeBackend()) return true;
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  return false;
}

async function createWindow() {
  // Reuse a healthy local API (e.g. one started manually for debugging).
  // Never spawn a second process blindly on the same fixed port.
  const alreadyRunning = await probeBackend();
  if (!alreadyRunning) startBackend();
  const ready = alreadyRunning || await waitForBackend();
  mainWindow = new BrowserWindow({
    width: 1440, height: 920, minWidth: 1000, minHeight: 700,
    backgroundColor: '#eeede7',
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  if (isDev) await mainWindow.loadURL('http://127.0.0.1:5173');
  else await mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  if (!ready) {
    dialog.showErrorBox('Local backend unavailable', 'VoiceGroceryPOS could not connect to its local API on 127.0.0.1:8000. Close other processes using that port, then restart the app.');
  }
}

app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_webContents, permission, callback) => {
    callback(permission === 'media' || permission === 'microphone');
  });
  return createWindow();
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('before-quit', () => { if (ownsBackend && backend && !backend.killed) backend.kill(); });
