const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // We will add methods here later, e.g.:
    // syncData: () => ipcRenderer.invoke('sync-data'),
    // printTicket: (data) => ipcRenderer.invoke('print-ticket', data),
    getAppVersion: () => ipcRenderer.invoke('get-app-version')
});
