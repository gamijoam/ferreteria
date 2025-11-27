# Guía de Pruebas - Sistema Dual de Monedas (USD/Bs)

## 🚀 Inicio Rápido

### 1. Ejecutar Migración de Base de Datos
```bash
python migrate_dual_currency.py
```

**Resultado Esperado:**
- Mensaje: "MIGRACIÓN COMPLETADA EXITOSAMENTE"
- Campos agregados a tablas `sales` y `payments`
- Tasa de cambio inicializada en 1.0

---

## 📋 Pruebas Paso a Paso

### PASO 1: Configurar Tasa de Cambio

1. Ejecutar la aplicación:
   ```bash
   python run.py
   ```

2. Ir a **Configuración** (menú principal)

3. En la sección "Tasa de Cambio (USD → Bs)":
   - Ingresar tasa actual (ejemplo: `36.50`)
   - Hacer clic en "Guardar Cambios"

4. **Verificar:**
   - Mensaje de éxito
   - Fecha de "Última Actualización" debe mostrar la fecha actual

---

### PASO 2: Punto de Venta (POS) - Venta en USD

1. Abrir **Punto de Venta**

2. **Verificar UI:**
   - Selector "Moneda Venta" con opciones USD/Bs
   - Métodos de pago expandidos:
     - Efectivo USD
     - Efectivo Bs
     - Transferencia USD
     - Transferencia Bs / Pago Móvil
     - Tarjeta Débito/Crédito
     - Crédito (Fiado)
   - Label inferior muestra: `Tasa: 1 USD = 36.50 Bs`

3. **Realizar Venta:**
   - Agregar producto al carrito
   - **Verificar:** Total muestra ambas monedas: `Total: $10.00 / Bs 365.00`
   - Seleccionar "Moneda Venta: USD"
   - Seleccionar "Método Pago: Efectivo USD"
   - Hacer clic en "COBRAR"

4. **Resultado Esperado:**
   - Venta procesada exitosamente
   - Ticket generado

---

### PASO 3: Punto de Venta (POS) - Venta en Bs

1. En **Punto de Venta**:
   - Agregar producto (ejemplo: $5.00)
   - **Verificar:** Total muestra `$5.00 / Bs 182.50`
   - Seleccionar "Moneda Venta: Bs"
   - Seleccionar "Método Pago: Efectivo Bs"
   - COBRAR

2. **Resultado Esperado:**
   - Venta procesada
   - En la base de datos, el campo `currency` = "Bs"
   - Campo `total_amount_bs` = 182.50

---

### PASO 4: Clientes - Deuda Dual

1. Ir a **Gestión de Clientes** → Pestaña "Cuentas Corrientes"

2. Seleccionar un cliente con deuda

3. **Verificar:**
   - Deuda muestra ambas monedas: `Deuda Actual: $50.00 / Bs 1,825.00`
   - Label inferior: `Tasa: 1 USD = 36.50 Bs`

---

### PASO 5: Clientes - Pago en USD

1. Con cliente seleccionado, clic en "Registrar Pago"

2. **Verificar Diálogo:**
   - Muestra deuda en ambas monedas
   - Radio buttons: "Pagar en USD" y "Pagar en Bs"

3. Seleccionar "Pagar en USD"
   - Ingresar monto: `$25.00`
   - Registrar Pago

4. **Resultado Esperado:**
   - Mensaje: "Deuda Restante: $25.00 / Bs 912.50"
   - Deuda actualizada en pantalla

---

### PASO 6: Clientes - Pago en Bs

1. Registrar otro pago
   - Seleccionar "Pagar en Bs"
   - Ingresar: `912.50` (equivalente a $25 USD)
   - Registrar Pago

2. **Resultado Esperado:**
   - Mensaje: "Deuda saldada completamente"
   - Deuda Actual: `$0.00 / Bs 0.00`

---

### PASO 7: Cierre de Caja - Desglose por Moneda

1. Ir a **Caja y Finanzas**

2. Hacer clic en "CERRAR CAJA"

3. **Verificar Reporte:**
   ```
   === RESUMEN DE CIERRE ===
   
   DINERO FÍSICO (Efectivo):
   - Esperado en Caja: $XXX
   - Reportado (Cajero): $XXX
   - Diferencia: CORRECTO
   
   DINERO DIGITAL / BANCO:
   (No se cuenta en caja, verificar en banco)
   --- Desglose de Ventas ---
   - Efectivo USD: $100.00
   - Efectivo Bs: Bs 365.00
   - Transferencia USD: $50.00
   - Transferencia Bs / Pago Móvil: Bs 1,825.00
   
   TOTAL VENTAS: $XXX
   ```

4. **Resultado Esperado:**
   - Ventas separadas por método de pago
   - Efectivo esperado solo cuenta ventas en efectivo
   - Transferencias/tarjetas mostradas para conciliación bancaria

---

## ✅ Checklist de Verificación

- [ ] Migración ejecutada sin errores
- [ ] Tasa de cambio configurable y guardada
- [ ] POS muestra precios duales (USD/Bs)
- [ ] Selector de moneda funcional
- [ ] Métodos de pago expandidos (USD/Bs)
- [ ] Ventas en USD se guardan correctamente
- [ ] Ventas en Bs se guardan con conversión
- [ ] Deuda de clientes muestra ambas monedas
- [ ] Pagos en USD funcionan
- [ ] Pagos en Bs se convierten correctamente
- [ ] Cierre de caja muestra desglose por método
- [ ] Efectivo esperado solo cuenta dinero físico

---

## 🐛 Problemas Comunes

### Error: "UnicodeEncodeError" en migración
**Solución:** Ya corregido en `migrate_dual_currency.py` (sin emojis)

### Tasa de cambio no se actualiza
**Solución:** Verificar que guardaste en Configuración y reiniciaste la vista

### Precios no se muestran en Bs
**Solución:** Verificar que la tasa de cambio sea > 0

---

## 📊 Datos de Prueba Sugeridos

**Tasa de Cambio:** 36.50 Bs por USD

**Productos:**
- Tornillo M8: $2.50 → Bs 91.25
- Cable 2x12: $15.00 → Bs 547.50

**Escenarios de Venta:**
1. Venta USD en Efectivo: $100
2. Venta Bs en Efectivo: Bs 365 (= $10 USD)
3. Venta USD por Transferencia: $50
4. Venta a Crédito: $200

**Escenarios de Pago:**
1. Cliente debe $100 → Paga $50 USD
2. Cliente debe $50 → Paga Bs 1,825 (= $50 USD)
