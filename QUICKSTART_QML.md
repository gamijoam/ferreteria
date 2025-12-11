# Guía Rápida - PySide6 + QML

## ✅ Estado Actual

**Fases Completadas:**
- ✅ Fase 1: Setup & Configuración
- ✅ Fase 2: Componentes Core (Login + Dashboard)

## 🚀 Cómo Ejecutar

```bash
# Desde la raíz del proyecto
python src\main_qml.py
```

O usa el script:
```bash
run_qml.bat
```

## 🔑 Credenciales

- **Usuario:** `admin`
- **Contraseña:** `admin123`

## 🎨 Características Implementadas

### Login (LoginView.qml)
- Diseño split-screen moderno
- Panel izquierdo con branding (logo + nombre del negocio)
- Panel derecho con formulario de login
- Validación de campos
- Mensajes de error
- Navegación con Enter

### Dashboard (MainView.qml)
- **Tema claro** con fondo blanco
- Header azul con logo y info de usuario
- Tarjetas de módulos **cuadradas** en grid 4x4
- Módulos visibles según rol:
  - **ADMIN**: Todos los módulos
  - **CASHIER**: POS, Caja, Clientes, Devoluciones, Cotizaciones
  - **WAREHOUSE**: Productos, Inventario, Proveedores, Compras

### Módulos Disponibles
- 🛒 Punto de Venta (naranja)
- 📦 Productos (verde)
- 📥 Inventario (verde)
- 💵 Caja (naranja)
- 👥 Clientes (morado)
- 📊 Reportes (cyan)
- ⚙️ Configuración (gris)
- 👥 Usuarios (gris)

## 📁 Archivos Clave

```
src/
├── main_qml.py              # Entry point
├── bridges/
│   └── auth_bridge.py       # Python-QML bridge
└── qml/
    ├── main.qml             # Root window
    └── views/
        ├── LoginView.qml    # Login screen
        └── MainView.qml     # Dashboard
```

## 🔧 Próximos Pasos

Para continuar la migración:

1. **Crear vistas de módulos** (POSView, ProductView, etc.)
2. **Crear más bridges** para cada módulo
3. **Agregar navegación** entre vistas
4. **Implementar funcionalidad** de cada módulo

## 📝 Notas

- La app antigua (PyQt6) sigue en `src/main.py`
- La app nueva (PySide6+QML) está en `src/main_qml.py`
- Todos los controladores y modelos NO han cambiado
- Solo la UI ha sido reemplazada
