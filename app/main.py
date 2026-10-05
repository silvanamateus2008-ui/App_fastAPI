from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ErrorNegocio
from app.routers import auth, clientes, productos, proveedores, ventas

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API de gestion de inventario y ventas de una fabrica.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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


app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(proveedores.router)
app.include_router(productos.router)
app.include_router(ventas.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
