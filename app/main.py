from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ErrorNegocio
from app.routers import auth, clientes, productos, proveedores, ventas
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.errors import ErrorNegocio
from app.routers import auth, clientes, health, productos, proveedores, ventas

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API de gestion de inventario y ventas de una fabrica.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErrorNegocio)
async def handle_error_negocio(_, exc: ErrorNegocio):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.mensaje, "code": exc.codigo, "errors": exc.errores},
        headers=exc.headers or None,
    )


@app.get("/health", tags=["infraestructura"], summary="Estado de salud")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_, exc: RequestValidationError):
    errors = [
        {"loc": error["loc"], "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "detail": "La solicitud contiene datos invalidos",
            "code": "datos_invalidos",
            "errors": errors,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(_, exc: StarletteHTTPException):
    mensajes = {
        404: ("El recurso solicitado no existe", "no_encontrado"),
        405: ("El metodo HTTP no esta permitido", "metodo_no_permitido"),
    }
    detail, code = mensajes.get(exc.status_code, (str(exc.detail), "error_http"))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail, "code": code, "errors": []},
        headers=exc.headers,
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(proveedores.router)
app.include_router(productos.router)
app.include_router(ventas.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
