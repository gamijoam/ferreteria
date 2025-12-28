const { app, BrowserWindow } = require('electron');
const path = require('path');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
// if (require('electron-squirrel-startup')) {
//   app.quit();
// }

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        title: "Ferretería SaaS",
        icon: path.join(__dirname, '../public/favicon.ico'), // Adjust path as needed
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.cjs')
        },
    });

    const isDev = !app.isPackaged;

    if (isDev) {
        // Development: Load Vite server
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
        console.log("Running in DEV mode: Loading http://localhost:5173");
    } else {
        // Production: Load built files
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
