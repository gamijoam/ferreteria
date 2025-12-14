# Guía de Despliegue y Arquitectura (Todo en Uno)

Has elegido la estrategia **"Todo en Uno"** para máxima simplicidad. Tanto el programa de Caja (Cliente) como el Sistema (Servidor) se empaquetan y actualizan juntos.

## 1. Estructura de Carpetas en el Cliente
Al instalar/actualizar, el Launcher creará esta estructura en la PC:

```
Carpeta Ferreteria/
├── Launcher.exe        <-- El usuario abre esto (Auto-actualizable)
├── version.json        <-- Versión actual instalada
├── Client/             <-- Carpeta del Frontend (Caja)
│   ├── Ferreteria.exe
│   └── .env            <-- Configuración DE LA CAJA (Opcional, para IP remota)
└── Server/             <-- Carpeta del Backend (Base de Datos)
    ├── Server.exe
    └── .env            <-- Configuración DE LA BASE DE DATOS (Obligatorio)
```

## 2. Configuración por Tipo de PC

### A. PC Única (Servidor + Caja)
Ideal para instalar en la computadora principal.
1.  Descomprime el archivo Zip.
2.  **IMPORTANTE**: Copia tu archivo `.env` (el que tiene la clave `DB_URL`) dentro de la carpeta `Server/`.
    - Ejemplo: `Server/.env`
3.  Ejecuta `Launcher.exe`.
    - Esto abrirá la Caja (`Client/Ferreteria.exe`).
4.  Tienes que ejecutar `Server/Server.exe` manualmente (o crear un acceso directo en "Inicio" de Windows) para que la base de datos funcione.

### B. PC Solo Caja (Red Local)
Para computadoras extra que solo cobran.
1.  Instala/Copia la carpeta Ferreteria.
2.  **Ignora** la carpeta `Server/` (no necesitas ejecutarla aquí).
3.  Entra a la carpeta `Client/`.
4.  Crea un archivo `.env` nuevo con la IP de la PC Principal:
    ```
    API_URL=http://192.168.1.X:8000
    ```
    *(Reemplaza X por la IP correcta)*.
5.  Ejecuta `Launcher.exe`.

---

## 3. Flujo de Actualización Automática
1.  **Tú (Dev)**: Ejecutas `build_update.py`. Se crea un Zip con AMBOS sistemas.
2.  **Launcher**:
    - Detecta cambio en `version.json` remoto.
    - Descarga el Zip "Todo en Uno".
    - Descomprime y actualiza ambas carpetas (`Client` y `Server`).
    - Tus archivos `.env` (en Client y Server) **se mantienen seguros** (no se sobrescriben).

---

## 4. Para el DESARROLLADOR (Crear una Actualización)

Sigue estos pasos cada vez que quieras liberar una nueva versión.

1.  **Programar**: Haz tus cambios en `frontend_caja` o `backend_api`.
2.  **Compilar**: Ejecuta el script mágico:
    ```bash
    python ferreteria_refactor/scripts/build_update.py
    ```
3.  **Probar**: Ve a la carpeta `landing_page/downloads` y prueba el Zip generado.
4.  **Publicar**: Sube los cambios a Git/GitHub (esto actualizará la Landing Page automáticamente en Netlify/Pages).

¡Listo! Los clientes se actualizarán solos al abrir el Launcher.
