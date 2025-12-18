# 🔐 Sistema de Licenciamiento - Guía Rápida para el Administrador

## 📌 ¿Qué es esto?

Un sistema que te permite controlar quién usa tu aplicación de ferretería mediante licencias digitales firmadas criptográficamente.

---

## 👥 Roles en el Sistema

### TÚ (Administrador)
- **Generas** las licencias para tus clientes
- Tienes la **clave privada** (como tu firma digital)
- Decides cuánto tiempo dura cada licencia

### TUS CLIENTES
- **Usan** las licencias que tú generas
- Solo pueden **verificar** que la licencia viene de ti
- No pueden crear licencias falsas

---

## 🚀 Configuración Inicial (Solo una vez en TU PC)

### Paso 1: Instalar Dependencia

```bash
pip install python-jose[cryptography]
```

### Paso 2: Generar Claves

```bash
cd ferreteria_refactor
python setup_license_system.py
```

**¿Qué hace esto?**
1. ✅ Crea `scripts/private_key.pem` - TU clave secreta (NUNCA compartir)
2. ✅ Crea `scripts/public_key.pem` - Clave pública (se embebe en la app)
3. ✅ Actualiza automáticamente los archivos del código con la clave pública

**⚠️ MUY IMPORTANTE:**
- Respalda `scripts/private_key.pem` en USB o nube
- Si la pierdes, no podrás generar más licencias
- NUNCA la incluyas en el repositorio Git

---

## 📝 Generar Licencias para Clientes

### Licencia DEMO (1 día, sin restricción de PC)

```bash
cd ferreteria_refactor
python scripts/license_generator.py --create-demo "Nombre del Cliente"
```

**Resultado:**
```
================================================================================
LICENCIA DEMO (Válida por 1 día)
================================================================================
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGZXJy...
================================================================================
```

**Uso:**
- Ideal para pruebas o demos
- Funciona en cualquier PC
- Expira automáticamente en 24 horas

### Licencia FULL (Personalizada, atada a una PC específica)

**Paso 1:** Cliente te envía su Machine ID

El cliente ejecuta el Launcher y ve una ventana como esta:
```
Machine ID: 123456789012
Proporcione este ID al administrador
```

**Paso 2:** Tú generas la licencia

```bash
# Licencia de 30 días
python scripts/license_generator.py --create-full "Ferretería XYZ" --hw-id 123456789012 --days 30

# Licencia de 1 año
python scripts/license_generator.py --create-full "Distribuidora ABC" --hw-id 123456789012 --days 365
```

**Resultado:**
```
================================================================================
LICENCIA FULL (Válida por 365 días)
================================================================================
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGZXJy...
================================================================================

🔒 Esta licencia SOLO funcionará en la máquina con ID: 123456789012
```

**Paso 3:** Envías el token al cliente

- Por email, WhatsApp, etc.
- Cliente lo copia completo
- Lo pega en la ventana de activación

---

## 🔄 Flujo Completo con un Cliente

```
1. CLIENTE ejecuta Launcher.pyw
   └─> ❌ "No se encontró licencia"
   └─> 🖥️ Muestra: "Machine ID: 123456789012"

2. CLIENTE te contacta
   └─> "Hola, mi Machine ID es 123456789012"

3. TÚ generas licencia
   └─> python scripts/license_generator.py --create-full "Cliente" --hw-id 123456789012 --days 365
   └─> Copias el token generado

4. TÚ envías token al cliente
   └─> Por email/WhatsApp

5. CLIENTE pega token en ventana
   └─> Click "Activar Licencia"
   └─> ✅ "Licencia activada exitosamente"

6. CLIENTE usa la app
   └─> Funciona por 365 días
   └─> Solo en ESA PC específica
```

---

## 🛠️ Comandos Útiles

### Ver tu Machine ID (para pruebas)

```bash
python scripts/license_generator.py --get-machine-id
```

### Ayuda del generador

```bash
python scripts/license_generator.py --help
```

---

## 📊 Tipos de Licencias

| Tipo | Duración | Hardware Lock | Uso |
|------|----------|---------------|-----|
| **DEMO** | 1 día | ❌ No | Pruebas, demos |
| **FULL** | Configurable | ✅ Sí | Clientes pagos |

---

## ⚠️ Problemas Comunes

### Cliente dice: "Licencia Expirada"

**Solución:**
1. Generas nueva licencia con nueva fecha
2. Se la envías
3. Cliente la activa (reemplaza la anterior)

### Cliente dice: "Hardware No Compatible"

**Causa:** Usó una licencia de otra PC

**Solución:**
1. Cliente te envía su Machine ID correcto
2. Generas nueva licencia con ese ID
3. Se la envías

### Cliente dice: "Licencia Inválida"

**Causa:** Token corrupto (copió mal)

**Solución:**
1. Reenvías el token
2. Cliente verifica que lo copió completo

---

## 🔒 Seguridad

### ✅ Lo que SÍ pueden hacer los clientes
- Usar la aplicación con licencia válida
- Ver cuántos días les quedan
- Activar nuevas licencias

### ❌ Lo que NO pueden hacer
- Generar licencias falsas
- Extender la fecha de expiración
- Usar la licencia en otra PC (FULL)
- Modificar el código para saltarse la validación

---

## 📁 Archivos Importantes

### EN TU PC (Administrador)

```
ferreteria_refactor/
├── scripts/
│   ├── license_generator.py     # ⭐ Usas este para generar licencias
│   ├── private_key.pem          # 🔐 TU clave secreta (RESPALDAR!)
│   └── public_key.pem           # 🔓 Clave pública (se distribuye)
└── setup_license_system.py      # ⚙️ Usas una sola vez
```

### EN PC DEL CLIENTE

```
ferreteria/
├── Launcher.pyw                 # 🚀 Cliente ejecuta esto
└── license.key                  # 📄 Se crea al activar licencia
```

---

## 🎯 Checklist de Distribución

Cuando envías la app a un cliente:

- [ ] **NO incluir:**
  - ❌ `scripts/private_key.pem`
  - ❌ `scripts/public_key.pem`
  - ❌ `license.key`

- [ ] **SÍ incluir:**
  - ✅ `Launcher.pyw` (con clave pública embebida)
  - ✅ Carpeta `ferreteria_refactor/` completa
  - ✅ Instrucciones de activación

---

## 📞 Soporte al Cliente

### Instrucciones para el Cliente

```
1. Ejecuta Launcher.pyw
2. Anota el Machine ID que aparece
3. Envíamelo por WhatsApp/Email
4. Espera a que te envíe la licencia
5. Copia el token completo
6. Pégalo en la ventana y click "Activar"
7. ¡Listo! La app se abre automáticamente
```

---

## 🔄 Renovación de Licencias

Cuando una licencia expira:

1. Cliente te contacta
2. Generas nueva licencia (mismo hw-id, nueva fecha)
3. Cliente activa la nueva licencia
4. Reemplaza automáticamente la anterior

---

**¿Dudas?** Consulta la documentación completa en `LICENSE_SYSTEM.md`

**Versión:** 1.0  
**Fecha:** 2025-12-18
