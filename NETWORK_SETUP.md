# Configuración de Red para Múltiples Computadoras

Esta guía te ayudará a configurar el sistema para que múltiples computadoras compartan la misma base de datos PostgreSQL en una red local.

## Requisitos Previos

- Dos o más computadoras en la misma red local
- Una computadora actuará como **SERVIDOR** (con PostgreSQL)
- Las demás serán **CLIENTES** (solo necesitan el ejecutable)

---

## PASO 1: Configurar el Servidor de Base de Datos

### 1.1 Instalar PostgreSQL en el Servidor

1. Descargar PostgreSQL desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Durante la instalación:
   - **Puerto**: Dejar el predeterminado `5432`
   - **Contraseña**: Elegir una contraseña segura para el usuario `postgres` (¡ANÓTALA!)
   - **Locale**: Seleccionar `Spanish, Venezuela` o `C` para evitar problemas de encoding

### 1.2 Configurar PostgreSQL para Aceptar Conexiones Remotas

1. **Abrir pgAdmin 4** (se instala con PostgreSQL)

2. **Conectarse al servidor local**:
   - Host: `localhost`
   - Usuario: `postgres`
   - Contraseña: (la que elegiste en la instalación)

3. **Crear la base de datos**:
   - Click derecho en `Databases` → `Create` → `Database`
   - Nombre: `ferreteria_db`
   - Owner: `postgres`
   - Encoding: `UTF8`
   - Click en `Save`

4. **Crear un usuario para la aplicación**:
   - Click derecho en `Login/Group Roles` → `Create` → `Login/Group Role`
   - **General tab**:
     - Name: `ferreteria_user`
   - **Definition tab**:
     - Password: `ferreteria2024` (o la que prefieras, ¡ANÓTALA!)
   - **Privileges tab**:
     - Marcar: `Can login?`
   - Click en `Save`

5. **Dar permisos al usuario**:
   - Click derecho en `ferreteria_db` → `Properties`
   - Ir a la pestaña `Security`
   - Click en `+` para agregar
   - Grantee: `ferreteria_user`
   - Privileges: Marcar `ALL`
   - Click en `Save`

### 1.3 Configurar Firewall de Windows

1. Abrir **Windows Defender Firewall** → `Configuración avanzada`
2. Click en `Reglas de entrada` → `Nueva regla`
3. Tipo de regla: `Puerto`
4. Protocolo: `TCP`
5. Puerto específico: `5432`
6. Acción: `Permitir la conexión`
7. Perfil: Marcar `Dominio`, `Privado` y `Público`
8. Nombre: `PostgreSQL`
9. Click en `Finalizar`

### 1.4 Configurar PostgreSQL para Escuchar en la Red

1. **Localizar el archivo `postgresql.conf`**:
   - Ruta típica: `C:\Program Files\PostgreSQL\16\data\postgresql.conf`
   - En pgAdmin: Click derecho en el servidor → `Properties` → pestaña `General` → ver `Configuration file`

2. **Editar `postgresql.conf`**:
   - Abrir con Notepad como Administrador
   - Buscar la línea `#listen_addresses = 'localhost'`
   - Cambiarla por:
     ```
     listen_addresses = '*'
     ```
   - Guardar el archivo

3. **Editar `pg_hba.conf`** (mismo directorio):
   - Abrir con Notepad como Administrador
   - Al final del archivo, agregar:
     ```
     # Permitir conexiones desde la red local
     host    all             all             192.168.0.0/16          md5
     host    all             all             10.0.0.0/8              md5
     ```
   - Guardar el archivo

4. **Reiniciar PostgreSQL**:
   - Abrir `Servicios` de Windows (Win + R → `services.msc`)
   - Buscar `postgresql-x64-16` (o la versión instalada)
   - Click derecho → `Reiniciar`

### 1.5 Obtener la IP del Servidor

1. Abrir CMD (Win + R → `cmd`)
2. Ejecutar:
   ```cmd
   ipconfig
   ```
3. Buscar `Adaptador de LAN inalámbrica` o `Adaptador de Ethernet`
4. Anotar la **Dirección IPv4** (ejemplo: `192.168.1.100`)

---

## PASO 2: Configurar el Servidor (Primera Computadora)

### 2.1 Configurar el .env en el Servidor

1. Navegar a la carpeta del ejecutable: `dist/InventarioSoft/`
2. Crear o editar el archivo `.env`:
   ```env
   DB_URL=postgresql://ferreteria_user:ferreteria2024@localhost:5432/ferreteria_db
   ```
   > **Nota**: Usa `localhost` porque el servidor se conecta a sí mismo

3. Ejecutar `InventarioSoft.exe`
4. El sistema creará automáticamente las tablas en la base de datos

---

## PASO 3: Configurar los Clientes (Otras Computadoras)

### 3.1 Copiar el Ejecutable

1. Copiar toda la carpeta `dist/InventarioSoft/` a cada computadora cliente
2. Puede ser mediante:
   - USB
   - Carpeta compartida en red
   - Correo electrónico (si el tamaño lo permite)

### 3.2 Configurar el .env en Cada Cliente

1. En cada computadora cliente, navegar a `InventarioSoft/`
2. Crear o editar el archivo `.env`:
   ```env
   DB_URL=postgresql://ferreteria_user:ferreteria2024@192.168.1.100:5432/ferreteria_db
   ```
   > **Importante**: Reemplazar `192.168.1.100` con la IP real del servidor

3. Ejecutar `InventarioSoft.exe`

---

## PASO 4: Verificar la Conexión

### 4.1 Probar desde el Cliente

1. Abrir CMD en la computadora cliente
2. Ejecutar:
   ```cmd
   ping 192.168.1.100
   ```
   - Debe responder correctamente
   - Si no responde, verificar que ambas computadoras estén en la misma red

3. Probar conexión al puerto PostgreSQL:
   ```cmd
   telnet 192.168.1.100 5432
   ```
   - Si dice "No se pudo abrir conexión", verificar el firewall

### 4.2 Probar la Aplicación

1. **En el servidor**: Crear un producto de prueba
2. **En el cliente**: Verificar que el producto aparezca
3. **En el cliente**: Crear una venta
4. **En el servidor**: Verificar que la venta aparezca

---

## Solución de Problemas

### Error: "could not connect to server"

**Causa**: El cliente no puede alcanzar el servidor

**Soluciones**:
1. Verificar que ambas computadoras estén en la misma red
2. Verificar la IP del servidor con `ipconfig`
3. Hacer ping desde el cliente al servidor
4. Verificar que el firewall permita el puerto 5432
5. Verificar que PostgreSQL esté corriendo en el servidor

### Error: "password authentication failed"

**Causa**: Usuario o contraseña incorrectos

**Soluciones**:
1. Verificar el `.env` - usuario y contraseña deben coincidir
2. En pgAdmin, verificar que el usuario `ferreteria_user` exista
3. Recrear el usuario si es necesario

### Error: "no pg_hba.conf entry for host"

**Causa**: PostgreSQL no permite conexiones desde esa IP

**Soluciones**:
1. Verificar que `pg_hba.conf` tenga las líneas correctas
2. Verificar que la IP del cliente esté en el rango permitido
3. Reiniciar PostgreSQL después de cambios en `pg_hba.conf`

### La aplicación es muy lenta

**Causa**: Problemas de red o configuración

**Soluciones**:
1. Verificar la velocidad de la red (ping debe ser < 10ms)
2. Usar cable Ethernet en lugar de WiFi si es posible
3. Verificar que el servidor tenga suficiente RAM (mínimo 4GB)

---

## Configuración Avanzada (Opcional)

### IP Estática para el Servidor

Para evitar que la IP del servidor cambie:

1. Ir a `Panel de Control` → `Centro de redes y recursos compartidos`
2. Click en la conexión activa → `Propiedades`
3. Seleccionar `Protocolo de Internet versión 4 (TCP/IPv4)` → `Propiedades`
4. Marcar `Usar la siguiente dirección IP`
5. Configurar:
   - Dirección IP: `192.168.1.100` (o la que prefieras)
   - Máscara de subred: `255.255.255.0`
   - Puerta de enlace: (la IP del router, ejemplo: `192.168.1.1`)
   - DNS preferido: `8.8.8.8`
   - DNS alternativo: `8.8.4.4`

### Backup Automático

Para hacer backups de la base de datos:

1. Crear un archivo `backup.bat`:
   ```batch
   @echo off
   set PGPASSWORD=tu_password_postgres
   "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres -d ferreteria_db > "C:\Backups\ferreteria_%date:~-4,4%%date:~-7,2%%date:~-10,2%.sql"
   ```

2. Programar en el Programador de tareas de Windows para que se ejecute diariamente

---

## Resumen de Configuración

| Computadora | Archivo .env | Descripción |
|-------------|--------------|-------------|
| **Servidor** | `DB_URL=postgresql://ferreteria_user:ferreteria2024@localhost:5432/ferreteria_db` | Se conecta a sí mismo |
| **Cliente 1** | `DB_URL=postgresql://ferreteria_user:ferreteria2024@192.168.1.100:5432/ferreteria_db` | Se conecta al servidor |
| **Cliente 2** | `DB_URL=postgresql://ferreteria_user:ferreteria2024@192.168.1.100:5432/ferreteria_db` | Se conecta al servidor |

> **Importante**: Reemplazar `192.168.1.100` con la IP real del servidor

---

## Soporte

Si tienes problemas con la configuración:

1. Verificar que PostgreSQL esté corriendo en el servidor
2. Verificar que el firewall permita el puerto 5432
3. Verificar que las credenciales en `.env` sean correctas
4. Hacer ping desde el cliente al servidor
5. Revisar los logs de PostgreSQL en `C:\Program Files\PostgreSQL\16\data\log\`
