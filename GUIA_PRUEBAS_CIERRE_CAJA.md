# Guía de Pruebas: Cierre de Caja Dual (USD y Bs)

Sigue estos pasos para verificar que el sistema maneja correctamente las dos monedas por separado.

## 1. Apertura de Caja
1. Ve al módulo **"Caja y Finanzas"**.
2. Si hay una caja abierta, ciérrala primero.
3. En "Apertura de Caja", ingresa montos iniciales distintos para probar:
   - **Fondo USD:** `100` (ejemplo)
   - **Fondo Bs:** `500` (ejemplo)
4. Haz clic en **"Abrir Caja"**.
5. Verifica que el mensaje de éxito muestre ambos montos por separado.

## 2. Realizar Ventas (POS)
Ve al **Punto de Venta** y realiza las siguientes ventas para probar los contadores:

### Venta A: Efectivo USD
1. Agrega un producto.
2. Selecciona Moneda: **USD**.
3. Método de Pago: **Efectivo USD**.
4. Cobra la venta (ej: Total $10).

### Venta B: Efectivo Bs
1. Agrega un producto.
2. Selecciona Moneda: **Bs**.
3. Método de Pago: **Efectivo Bs**.
4. Cobra la venta (ej: Total Bs 400).
   - *Nota: El sistema guardará el equivalente en USD para el total de ventas, pero sumará los Bs físicos a la caja de Bs.*

### Venta C: Pago Digital (Opcional)
1. Haz una venta con "Transferencia" o "Pago Móvil".
2. Esto **NO** debe afectar el efectivo esperado en caja.

## 3. Registrar Gastos (Opcional)
1. Vuelve al módulo **"Caja y Finanzas"**.
2. Haz clic en **"Registrar Gasto / Retiro"**.
3. Registra un gasto en **Bs**:
   - Monto: `50`
   - Moneda: `Bs`
   - Descripción: "Pago transporte"
4. (Opcional) Registra otro en USD.

## 4. Cierre de Caja
1. Haz clic en **"CERRAR CAJA (Cierre Ciego)"**.
2. Aparecerá el diálogo para contar el dinero. Ingresa los montos que deberías tener físicamente.
   
   **Cálculo esperado según este ejemplo:**
   - **USD:** 100 (Inicio) + 10 (Venta A) = **$110**
   - **Bs:** 500 (Inicio) + 400 (Venta B) - 50 (Gasto) = **Bs 850**

3. Ingresa estos montos exactos:
   - Efectivo USD: `110`
   - Efectivo Bs: `850`

4. Haz clic en **"Cerrar Caja"**.

## 5. Verificación del Reporte
El reporte final debe mostrar:

- **EFECTIVO USD:**
  - Esperado: $110.00
  - Contado: $110.00
  - Diferencia: **CORRECTO**

- **EFECTIVO Bs:**
  - Esperado: Bs 850.00
  - Contado: Bs 850.00
  - Diferencia: **CORRECTO**

Si ingresas montos diferentes, el sistema te indicará "SOBRANTE" o "FALTANTE" en la moneda específica donde hubo el error.
