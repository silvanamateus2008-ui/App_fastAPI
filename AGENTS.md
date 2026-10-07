# Reglas del proyecto App_fastAPI (backend de fabrica)
- Stack: FastAPI, SQLAlchemy 2.0 sincrono, Alembic, Pydantic v2, PyJWT, pwdlib/Argon2, pytest, ruff. Python 3.12 o superior.
- Capas: routers (solo HTTP) -> services (reglas de negocio y consultas) -> models. Los routers no contienen logica.
- Idioma: dominio, rutas, errores y comentarios en espanol; infraestructura en ingles. Codigo ASCII, sin tildes en identificadores.

## Nombres (regla propia de este proyecto)
- Las tablas y columnas conservan EXACTAMENTE el nombre del dump original de PostgreSQL (`"Cliente"`, `"nombreCliente"`, `detalle_venta`). PostgreSQL exige comillas para esos nombres y asi la API habla directo con la base ya existente sin renombrar nada.
- El atributo Python si es snake_case en espanol: `nombre_cliente = mapped_column("nombreCliente", String(100))`.
- El JSON de la API si es camelCase (clase base `CamelCaseSchema`). Los tres niveles quedan separados y sin colisiones.
- La tabla `usuarios` es nueva (el dump original no tiene autenticacion) y si usa snake_case.

- API bajo /api, rutas en plural y minusculas, colecciones con "" (no "/"). Rutas fijas declaradas ANTES de /{id}.
- Errores: lanza ErrorNegocio y sus subclases (NoEncontradoError 404, ConflictoError 409, ReglaNegocioError 422, PermisoError 403, StockInsuficienteError 409). Respuesta {"detail","code","errors":[]}. Nunca HTTPException con texto suelto.
- Listas paginadas con Pagina[T] y PaginacionParams (pagina>=1, tamano 1..100, default 20).
- Dinero: Decimal, Numeric(12,2). Fechas: DateTime con zona UTC en BD. Hoy y semanas usan America/Bogota (ZoneInfo; requirements incluye tzdata).
- Permisos: require_roles(...) en cada ruta. ADMIN, ALMACEN, VENTAS. Lo destructivo o financiero sensible es solo ADMIN.

## Reglas de negocio de la fabrica
- `subtotal = precio_unitario * cantidad` y `total = suma de subtotales`: los calcula el servidor, el cliente nunca los envia.
- Una venta se crea con sus detalles en la misma peticion y descuenta stock de cada producto.
- No se puede registrar una venta si algun producto no tiene stock suficiente.
- No se puede eliminar un producto con ventas asociadas ni una venta con detalles: se responde 409 para no perder historico.
- Las claves foraneas usan ON DELETE RESTRICT (el dump original traia CASCADE, que borraba el historico de ventas en silencio).

- Cada ruta con summary, description y responses en espanol, y tags. Nombres de funcion unicos (generan el operationId).
- Migraciones: `alembic revision --autogenerate`, revision manual y verificacion offline con --sql. `alembic heads` debe dar uno.
- Tests (SQLite en memoria) con las fabricas de tests/factories.py. `python -m pytest -q` y `ruff check .` deben pasar. Un test por regla de negocio y por codigo de error.
- Nunca Docker local ni PostgreSQL local. Nunca leer, imprimir ni modificar `.env`. Sin claves en el repo.
- Un tema por sesion: muestra un plan de 3 a 5 lineas y espera mi ok. No hagas commit ni push. Toca solo los archivos de la tarea.
