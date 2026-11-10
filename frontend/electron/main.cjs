const { app, BrowserWindow } = require('electron');
const path = require('node:path');
const { spawn } = require('node:child_process');
const http = require('node:http');

let backend;
let mainWindow;
const isDev = !app.isPackaged;

function waitForBackend(attempt = 0) {
  return new Promise((resolve, reject) => {
    const req = http.get('http://127.0.0.1:8000/health', res => { res.resume(); resolve(true); });
    req.on('error', () => attempt >= 40 ? reject(new Error('Local backend did not start')) : setTimeout(() => waitForBackend(attempt + 1).then(resolve, reject), 500));
    req.setTimeout(700, () => req.destroy());
  });
}

function startBackend() {
  if (isDev) {
    backend = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: path.join(__dirname, '../../backend'), windowsHide: true, stdio: 'inherit' });
  } else {
    const executable = path.join(process.resourcesPath, 'backend', 'voicegrocery-backend.exe');
    backend = spawn(executable, [], { windowsHide: true, stdio: 'inherit' });
  }
}

async function createWindow() {
  startBackend();
  try { await waitForBackend(); } catch (error) { console.error(error); }
  mainWindow = new BrowserWindow({ width: 1440, height: 920, minWidth: 1000, minHeight: 700, backgroundColor: '#0a0f1a', webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true } });
  if (isDev) await mainWindow.loadURL('http://127.0.0.1:5173');
  else await mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('before-quit', () => { if (backend && !backend.killed) backend.kill(); });
