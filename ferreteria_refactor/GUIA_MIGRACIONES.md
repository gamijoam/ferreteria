# Guía de Migraciones de Base de Datos con Alembic

## 📚 Introducción

Este documento explica cómo realizar modificaciones a la base de datos del sistema de Ferretería utilizando el sistema de auto-migración con Alembic.

## 🎯 Concepto Clave

**Regla de Oro:** Cuando modificas `models.py`, SIEMPRE debes generar y commitear el archivo de migración correspondiente.

## 🔄 Flujo de Trabajo Completo

### Paso 1: Modificar el Modelo

**Ubicación:** `backend_api/models/models.py`

Ejemplo - Agregar una nueva tabla:

```python
class MiNuevaTabla(Base):
    __tablename__ = "mi_nueva_tabla"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
```

Ejemplo - Agregar una columna a tabla existente:

```python
class Product(Base):
    # ... columnas existentes ...
    
    # Nueva columna
    nueva_columna = Column(String, nullable=True)
```

### Paso 2: Generar la Migración

**Comando:**
```bash
cd ferreteria_refactor
alembic revision --autogenerate -m "Descripción del cambio"
```

**Ejemplos de descripciones:**
- `"Add customer_notes table"`
- `"Add discount_percentage to products"`
- `"Remove deprecated_field from sales"`

**Salida esperada:**
```
INFO [alembic.autogenerate.compare] Detected added table 'mi_nueva_tabla'
Generating .../alembic/versions/abc123_descripcion.py ... done
```

### Paso 3: Revisar la Migración Generada

**Ubicación:** `alembic/versions/[hash]_descripcion.py`

Verifica que Alembic detectó correctamente los cambios:

```python
def upgrade():
    # Aquí están los cambios que se aplicarán
    op.create_table('mi_nueva_tabla',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        # ...
    )

def downgrade():
    # Aquí está cómo revertir los cambios
    op.drop_table('mi_nueva_tabla')
```

### Paso 4: Commitear AMBOS Archivos

```bash
# Agregar el modelo modificado
git add backend_api/models/models.py

# Agregar el archivo de migración
git add alembic/versions/

# Commitear juntos
git commit -m "Add nueva_tabla to database schema"

# Pushear al repositorio
git push
```

## 🖥️ En la PC del Cliente

### Proceso Automático

1. **Git Pull:** El `Launcher.pyw` ejecuta `git pull` automáticamente
   - Descarga `models.py` actualizado
   - Descarga el nuevo archivo de migración

2. **Auto-Migración:** Al iniciar el servidor, `run_migrations()` en `main.py`:
   - Detecta la nueva migración
   - La aplica automáticamente
   - Crea/modifica las tablas en PostgreSQL

3. **Resultado:** Sin intervención manual del cliente

### Log Esperado

```
🔄 Checking database migrations...
INFO [alembic.runtime.migration] Running upgrade abc123 -> def456, Add nueva_tabla
✅ Database migrations applied successfully.
```

## ⚠️ Errores Comunes

### Error 1: "Target database is not up to date"

**Causa:** Tu base de datos local no está sincronizada.

**Solución:**
```bash
alembic upgrade head
```

### Error 2: La tabla no se crea en el cliente

**Causa:** Olvidaste pushear el archivo de migración.

**Solución:**
```bash
git add alembic/versions/
git commit -m "Add missing migration file"
git push
```

### Error 3: "No module named 'backend_api'"

**Causa:** Alembic no encuentra el módulo del proyecto.

**Solución:** Ya está corregido en `alembic/env.py` con path resolution absoluto.

## 📝 Tipos de Modificaciones

### Agregar Tabla Nueva

```python
# En models.py
class NuevaTabla(Base):
    __tablename__ = "nueva_tabla"
    id = Column(Integer, primary_key=True)
    # ... columnas ...
```

### Agregar Columna

```python
# En models.py - Clase existente
class Product(Base):
    # ... columnas existentes ...
    nueva_columna = Column(String, nullable=True)  # ← Agregar aquí
```

### Modificar Columna

```python
# Cambiar tipo de dato
# ANTES: precio = Column(Numeric(10, 2))
# DESPUÉS: precio = Column(Numeric(12, 2))
```

### Eliminar Columna

```python
# Simplemente comenta o elimina la línea
# columna_vieja = Column(String)  # ← Eliminar
```

### Eliminar Tabla

```python
# Comenta o elimina toda la clase
# class TablaVieja(Base):
#     ...
```

## 🧪 Probar Localmente Antes de Pushear

```bash
# 1. Genera la migración
alembic revision --autogenerate -m "Mi cambio"

# 2. Aplica la migración localmente
alembic upgrade head

# 3. Verifica en tu base de datos que funcionó

# 4. Si todo está bien, commitea y pushea
git add .
git commit -m "Database schema update"
git push
```

## 🔧 Comandos Útiles de Alembic

```bash
# Ver historial de migraciones
alembic history

# Ver migración actual
alembic current

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver SQL que se ejecutará (sin aplicar)
alembic upgrade head --sql
```

## 📂 Estructura de Archivos

```
ferreteria_refactor/
├── alembic/
│   ├── versions/
│   │   ├── 3a1b7ff040a1_initial_migration.py
│   │   ├── 6bff1d3c8718_add_test_auto_migration_table.py
│   │   └── [nuevas migraciones aquí]
│   ├── env.py          ← Configuración de Alembic
│   └── script.py.mako  ← Template para nuevas migraciones
├── backend_api/
│   ├── models/
│   │   └── models.py   ← AQUÍ modificas las tablas
│   └── main.py         ← run_migrations() ejecuta auto-migración
└── alembic.ini         ← Configuración principal
```

## ✅ Checklist para Modificaciones

- [ ] Modificar `backend_api/models/models.py`
- [ ] Ejecutar `alembic revision --autogenerate -m "Descripción"`
- [ ] Revisar el archivo de migración generado
- [ ] Probar localmente con `alembic upgrade head`
- [ ] Verificar que la tabla/columna se creó correctamente
- [ ] `git add backend_api/models/models.py`
- [ ] `git add alembic/versions/`
- [ ] `git commit -m "Mensaje descriptivo"`
- [ ] `git push`
- [ ] Verificar en PC del cliente que se aplicó automáticamente

## 🎓 Resumen

1. **Modificas** `models.py`
2. **Generas** migración con `alembic revision --autogenerate`
3. **Commiteas** AMBOS archivos (modelo + migración)
4. **Pusheas** al repositorio
5. **El cliente** recibe todo automáticamente vía `git pull`
6. **La migración** se aplica automáticamente al iniciar el servidor

**¡Nunca olvides el archivo de migración!** 🚨
