# Reporte de Auditoría Técnica

## 1. Diagnóstico de Rendimiento (Async/Sync)
- **Estado:** [CRÍTICO]
- **Hallazgos:**
  - El archivo `backend_api/routers/products.py` contiene funciones definidas como `async def` que ejecutan operaciones de base de datos síncronas (bloqueantes) sin usar `await` ni ejecutores de hilos.
  - **Endpoints Afectados:**
    - `POST /products/` (`create_product`)
    - `PUT /products/{product_id}` (`update_product`)
    - `DELETE /products/{product_id}` (`delete_product`)
  - **Explicación Técnica:** Al definir la función como `async def`, FastAPI asume que es una corrutina y la ejecuta en el *Event Loop* principal. Operaciones como `db.add()`, `db.commit()` y `db.query()` son síncronas (bloqueantes) en SQLAlchemy (sin usar la extensión asyncio). Esto congela todo el servidor para todas las peticiones entrantes mientras la base de datos responde, anulando la concurrencia de FastAPI.

## 2. Preparación para PostgreSQL
- **Connection Pooling:** [Faltante]
  - La configuración en `backend_api/database/db.py` no especifica `pool_size` ni `max_overflow`. SQLAlchemy usa valores por defecto (QueuePool), pero para un entorno de producción con PostgreSQL se recomienda configuración explícita para evitar agotar conexiones.
- **Driver:** [Detectado]
  - `psycopg2-binary` está presente en `requirements.txt`.
- **Recomendación:**
  ```python
  engine = create_engine(
      settings.DATABASE_URL,
      pool_size=20,
      max_overflow=10,
      pool_timeout=30,
      pool_recycle=1800,
  )
  ```

## 3. Estrategia de Migraciones
- **Estado Actual:** Riesgo Alto.
  - Se utiliza `models.Base.metadata.create_all(bind=engine)` en `main.py`. Esto solo crea tablas nuevas pero **no actualiza** tablas existentes. Cualquier cambio en el esquema (ej: agregar columna) requerirá borrar la base de datos o ejecutar SQL manual.
  - No se encontró configuración de Alembic (`alembic.ini`).
- **Acción Requerida:**
  1. Instalar `alembic`.
  2. Ejecutar `alembic init alembic`.
  3. Configurar `alembic/env.py` para importar `Base` y cargar `DATABASE_URL`.
  4. Generar la migración inicial: `alembic revision --autogenerate -m "Initial_migration"`.
  5. Eliminar `create_all()` de `main.py`.

## 4. Calidad de Código (Refactor)
- **Endpoint `products.py` (`update_product`):**
  - **Lógica en Controlador:** La función contiene demasiada lógica de negocio (manejo de unidades, snapshots, cálculo de diffs) que debería estar en una capa de Servicios (`services/product_service.py`).
  - **Cálculo Manual de Diffs:** Se realiza un cálculo manual de diferencias (líneas 116-118) convirtiendo modelos a diccionarios. Esto es propenso a errores y difícil de mantener. Se sugiere usar `SQLAlchemy History` o una librería de auditoría dedicada.
  - **Hardcoded User:** La línea 99 `user_id = 1` es técnica deuda explícita. Debe obtenerse del token JWT del usuario actual (`current_user`).
  - **Manejo de Unidades:** La estrategia de borrar todas las unidades y recrearlas (líneas 87-92) es ineficiente y rompe la integridad referencial si otras tablas apuntan a `product_units`. Debería hacer "upsert" (actualizar existentes, crear nuevas, borrar no enviadas).

## 5. Conclusión
El código base **NO está listo para producción** en PostgreSQL bajo carga real.
1. **Prioridad 0:** Corregir el bloqueo del Event Loop (cambiar `async def` a `def` para endpoints síncronos o migrar a `AsyncSession` de SQLAlchemy).
2. **Prioridad 1:** Implementar Alembic para migraciones seguras.
3. **Prioridad 2:** Refactorizar la lógica de `products.py` a servicios y corregir la configuración del Pool de conexiones.

Se recomienda pausar nuevas funcionalidades hasta resolver la Prioridad 0 y 1.
