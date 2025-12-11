# README - PySide6 + QML Migration

## 🚀 Instalación de PySide6

### Opción 1: Script Automático (Recomendado)
Ejecuta el archivo `install_pyside6.bat`:
```bash
install_pyside6.bat
```

### Opción 2: Manual
```bash
pip install PySide6 PySide6-Addons
```

Si tienes problemas de SSL:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org PySide6 PySide6-Addons
```

## 🎯 Ejecutar la Aplicación QML

```bash
python src/main_qml.py
```

## 📁 Estructura del Proyecto QML

```
src/qml/
├── main.qml                    # Ventana principal
├── components/                 # Componentes reutilizables
│   ├── Button.qml             # Botón Material Design
│   ├── Card.qml               # Tarjeta glassmórfica
│   ├── TextField.qml          # Campo de texto
│   └── ModuleCard.qml         # Tarjeta de módulo
├── views/                      # Vistas de la aplicación
│   ├── LoginView.qml          # Vista de login
│   └── MainView.qml           # Dashboard principal
└── styles/                     # Temas y estilos
    ├── Theme.qml              # Tema Material Design 3
    └── qmldir                 # Definición del módulo

src/bridges/
├── auth_bridge.py             # Puente Python-QML para autenticación
└── __init__.py
```

## ✨ Características Implementadas

### Fase 1: Setup & Configuration ✅
- [x] PySide6 en requirements.txt
- [x] Estructura de directorios QML
- [x] Sistema de temas Material Design 3
- [x] Componentes base (Button, Card, TextField)

### Fase 2: Core Components ✅
- [x] LoginView con diseño moderno
- [x] MainView con dashboard
- [x] AuthBridge para comunicación Python-QML
- [x] Sistema de navegación con StackView

## 🎨 Componentes QML Disponibles

### Button
```qml
Button {
    text: "Click Me"
    variant: "primary"  // primary, secondary, success, danger, warning, outlined, text
    loading: false
    iconName: "🚀"
    onClicked: { /* acción */ }
}
```

### Card
```qml
Card {
    elevation: 2
    hoverable: true
    clickable: true
    onClicked: { /* acción */ }
    
    contentItem: Text {
        text: "Card Content"
    }
}
```

### TextField
```qml
TextField {
    label: "Username"
    placeholderText: "Enter username"
    iconLeft: "👤"
    isPassword: false
    hasError: false
    errorText: ""
    onAccepted: { /* acción */ }
}
```

## 🔄 Próximos Pasos

1. **Instalar PySide6** usando `install_pyside6.bat`
2. **Probar la aplicación** con `python src/main_qml.py`
3. **Migrar vistas restantes**:
   - POSView
   - ProductView
   - InventoryView
   - CashView
   - Etc.

## 📝 Notas Importantes

- La aplicación antigua (PyQt6) sigue disponible en `src/main.py`
- La nueva aplicación (PySide6 + QML) está en `src/main_qml.py`
- Todos los controladores y modelos permanecen sin cambios
- Solo la capa de UI ha sido reemplazada

## 🐛 Troubleshooting

### Error: "No module named 'PySide6'"
Ejecuta: `install_pyside6.bat`

### Error SSL durante instalación
El script automáticamente intenta con `--trusted-host`

### La aplicación no carga
Verifica que todos los archivos QML estén en `src/qml/`
