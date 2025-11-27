# Módulo de Impresión Térmica - Guía de Uso

## Instalación Completada ✅

Se han instalado las siguientes librerías:
- `python-escpos` - Soporte para impresoras ESC/POS
- `Pillow` - Procesamiento de imágenes (logos)

## Características Implementadas

### 1. Configuración de Impresora
**Ubicación:** Configuración → ⚙️ Configurar Impresora Térmica

**Tipos de impresora soportados:**
- **ESC/POS** (Epson, Star, Bixolon, Custom, etc.)
  - Conexión USB
  - Conexión por Red (IP)
- **Windows** (Impresora predeterminada del sistema)

**Funciones:**
- Detección automática de impresoras USB
- Prueba de impresión
- Configuración de auto-impresión

### 2. Logo Empresarial
**Ubicación:** Configuración → Logo de la Empresa

**Funciones:**
- Cargar logo (PNG, JPG, JPEG, BMP)
- Vista previa del logo
- Logo se muestra en:
  - Pantalla de login (pendiente)
  - Ventana principal (pendiente)
  - Tickets impresos

### 3. Impresión Automática
- Los tickets se imprimen automáticamente después de cada venta
- Se puede activar/desactivar en la configuración de impresora
- Si falla la impresión, la venta se completa de todos modos

### 4. Formato de Ticket

```
========================================
        [LOGO DE LA EMPRESA]
        NOMBRE DEL NEGOCIO
        RIF: J-12345678-9
        Dirección completa
        Tel: 0414-1234567
========================================
Fecha: 2025-11-27 09:30:45
Ticket #: 123
----------------------------------------
PRODUCTO          CANT  PRECIO   TOTAL
----------------------------------------
Tornillo 1/4"        5   $2.50   $12.50
Pintura Blanca       1  $25.00   $25.00
----------------------------------------
                       TOTAL: $37.50

Método de Pago: Efectivo Bs
Tasa: 1 USD = 100.00 Bs
Total Bs: Bs 3750.00

========================================
    ¡GRACIAS POR SU COMPRA!
========================================
[CÓDIGO DE BARRAS: 123]
```

## Configuración Paso a Paso

### Para Impresora USB (ESC/POS)

1. Conectar la impresora térmica al puerto USB
2. Instalar drivers del fabricante (si es necesario)
3. Ir a **Configuración** → **⚙️ Configurar Impresora Térmica**
4. Seleccionar tipo: **ESC/POS**
5. Seleccionar conexión: **USB**
6. Hacer clic en **"Detectar Impresoras USB"**
7. Si se detecta, hacer clic en **"Sí"** para usar la primera
8. Hacer clic en **"Prueba de Impresión"**
9. Verificar que se imprimió correctamente
10. Activar **"Imprimir tickets automáticamente"**
11. Hacer clic en **"Guardar Configuración"**

### Para Impresora de Red (ESC/POS)

1. Conectar la impresora a la red
2. Anotar la dirección IP de la impresora
3. Ir a **Configuración** → **⚙️ Configurar Impresora Térmica**
4. Seleccionar tipo: **ESC/POS**
5. Seleccionar conexión: **Network**
6. Ingresar IP Address (ej: 192.168.1.100)
7. Ingresar Puerto (generalmente 9100)
8. Hacer clic en **"Prueba de Impresión"**
9. Verificar que se imprimió correctamente
10. Activar **"Imprimir tickets automáticamente"**
11. Hacer clic en **"Guardar Configuración"**

### Para Impresora Windows

1. Configurar la impresora en Windows
2. Ir a **Configuración** → **⚙️ Configurar Impresora Térmica**
3. Seleccionar tipo: **Windows**
4. Dejar el nombre vacío para usar la predeterminada, o ingresar nombre específico
5. Hacer clic en **"Prueba de Impresión"**
6. Verificar que se imprimió correctamente
7. Activar **"Imprimir tickets automáticamente"**
8. Hacer clic en **"Guardar Configuración"**

## Cargar Logo

1. Ir a **Configuración**
2. En la sección **"Logo de la Empresa"**, hacer clic en **"Cargar Logo"**
3. Seleccionar imagen (PNG o JPG recomendado)
4. Verificar vista previa
5. Hacer clic en **"Guardar Cambios"**
6. El logo aparecerá en los tickets impresos

## Solución de Problemas

### La impresora no se detecta (USB)
- Verificar que la impresora esté encendida
- Verificar que el cable USB esté conectado
- Instalar drivers del fabricante
- Reiniciar la aplicación

### Error al imprimir
- Verificar que la impresora tenga papel
- Verificar que no haya atascos
- Verificar la configuración (IP, puerto, etc.)
- Hacer una prueba de impresión desde Windows

### El logo no se imprime
- Verificar que el archivo de imagen exista
- Verificar que la imagen no sea muy grande (max 512px ancho)
- Activar "Imprimir logo en ticket" en configuración

### La venta se completa pero no imprime
- Esto es normal, la venta no falla si la impresión falla
- Revisar la configuración de la impresora
- Hacer una prueba de impresión manual

## Vendor IDs Comunes

- **Epson:** 0x04b8
- **Star Micronics:** 0x0519
- **Bixolon:** 0x154f
- **Custom:** 0x0fe6

## Notas Importantes

- La impresión automática solo funciona si hay una sesión de caja abierta
- Los tickets se imprimen en el momento de completar la venta
- Si la impresión falla, la venta se completa de todos modos
- El logo debe estar en formato PNG o JPG para mejor calidad
- Para impresoras térmicas, se recomienda logos en blanco y negro
