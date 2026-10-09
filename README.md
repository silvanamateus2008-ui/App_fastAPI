# App_fastAPI — Backend de la fabrica

API de gestion de inventario y ventas (FastAPI + SQLAlchemy 2.0 + Alembic).
En desarrollo se usa **SQLite** por defecto (`DATABASE_URL=sqlite:///./fabrica.db`),
sin necesidad de PostgreSQL. El frontend Flutter (`App_Bocadillos`) se conecta en
`http://localhost:5173` (CORS habilitado por defecto).

## Requisitos

- Python 3.12 o superior.
- Frontend: `App_Bocadillos` (opcional, para ver la app).

## Instalacion y arranque en Windows (CMD)

Abre una terminal en `C:\Users\ASUS\Documents\App_fastAPI`.

### 1. Crear y activar el entorno virtual

```cmd
cd /d C:\Users\ASUS\Documents\App_fastAPI
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias (incluye las de desarrollo)

```cmd
pip install -r requirements-dev.txt
```

### 3. Crear el archivo `.env` local con SQLite

```cmd
copy .env.example .env
```

Solo edita `.env` si quieres cambiar valores. En desarrollo el valor que importa
ya viene con SQLite:

```
DATABASE_URL=sqlite:///./fabrica.db
```

Para poder sembrar usuarios, completa en `.env` las variables `SEED_ADMIN_*`,
`SEED_ALMACEN_*` y `SEED_VENTAS_*` (contrasenas de al menos 12 caracteres).

### 4. Inicializar la base vacia (crea todas las tablas)

```cmd
alembic upgrade head
```

Este es el metodo canonico y reproducible: aplica las migraciones desde cero,
compatibles con SQLite (revisiones con `batch_alter_table`).

> Atajo de desarrollo: `python dev_db.py` tambien crea el esquema directo desde
> los modelos, pero **no** lleva el control de versiones de Alembic. Usalo solo
> si entiendes la diferencia; el flujo documentado es `alembic upgrade head`.

### 5. Crear los usuarios semilla

```cmd
python seed.py
```

Si la base no tiene tablas, el script muestra exactamente que paso falta
(`alembic upgrade head`). Si faltan variables `SEED_*`, indica cuales definir.

### 6. Arrancar la API

```cmd
uvicorn app.main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Documentacion: `http://localhost:8000/docs`
- Salud: `http://localhost:8000/health`
- CORS para Flutter Web: `http://localhost:5173` (listo por defecto).

## Flujo completo de cero (resumen)

```cmd
cd /d C:\Users\ASUS\Documents\App_fastAPI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --port 8000
```

## Usuarios semilla por defecto

| Rol      | Usuario | Email             |
|----------|---------|-------------------|
| ADMIN    | admin   | admin@gmail.com   |
| ALMACEN  | almacen | almacen@gmail.com |
| VENTAS   | ventas  | ventas@gmail.com  |

Las credenciales se leen de `.env`; si los cambiaste alli, esos son los usuarios
que se crean/se conservan (el seed es idempotente).

## Verificacion

```cmd
python -m pytest -q
ruff check .
alembic heads            # debe mostrar una sola revision
```

## Reglas del proyecto

Ver `AGENTS.md` para la convencion de nombres (tablas/columnas del dump,
camelCase en JSON), contrato de errores `{"detail","code","errors"}`, paginacion
`{items,total,pagina,tamano,paginas}` y permisos por rol (ADMIN/ALMACEN/VENTAS).