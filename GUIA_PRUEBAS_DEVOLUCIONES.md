# Guía de Pruebas - Devoluciones y Anulaciones (Dual Currency)

## Objetivo
Verificar que el sistema de devoluciones funciona correctamente con soporte dual currency y que las anulaciones de ventas se registran en la moneda correcta.

---

## Prueba 1: Devolución Parcial en USD

### Pasos:
1. **Abrir Caja** con fondos iniciales (ej: $100 USD, Bs 0)
2. **Realizar una venta** de 3 productos en "Efectivo USD"
3. **Ir a Devoluciones** (Módulo 6)
4. Buscar la venta por ID
5. Marcar **1 producto** para devolver (cambiar cantidad en columna "Devolver")
6. Seleccionar **USD** como moneda de reembolso
7. Procesar devolución con motivo "Producto defectuoso"

### Resultado Esperado:
- ✅ Stock del producto devuelto aumenta
- ✅ Mensaje muestra reembolso en USD
- ✅ Al cerrar caja, aparece como "Gasto USD"

---

## Prueba 2: Anulación Completa en Bs

### Pasos:
1. **Realizar una venta** de 2 productos en "Efectivo Bs"
2. **Ir a Devoluciones**
3. Buscar la venta
4. Hacer clic en **"ANULAR VENTA COMPLETA"**
5. Verificar que todas las cantidades se llenan automáticamente
6. Seleccionar **Bs** como moneda de reembolso
7. Procesar con motivo "Error de cajero"

### Resultado Esperado:
- ✅ Todas las cantidades se llenan al máximo
- ✅ Stock de todos los productos se restaura
- ✅ Mensaje muestra reembolso en Bs
- ✅ Al cerrar caja, aparece como "Gasto Bs"

---

## Prueba 3: Verificación en Cierre de Caja

### Pasos:
1. Después de las pruebas anteriores, **Cerrar Caja**
2. Revisar el reporte de cierre

### Resultado Esperado:
- ✅ Los gastos de devoluciones aparecen separados por moneda:
  - Gastos USD: incluye devolución de Prueba 1
  - Gastos Bs: incluye devolución de Prueba 2
- ✅ El efectivo esperado refleja correctamente las devoluciones

---

## Notas Importantes
- El reembolso **siempre se calcula en USD** (precio original), pero se **registra en la moneda seleccionada**
- Si devuelves en Bs, el sistema convierte usando la tasa actual
- Las anulaciones completas son útiles para corregir errores de cajero rápidamente
