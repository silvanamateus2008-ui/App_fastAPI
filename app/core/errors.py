"""Errores de negocio con su codigo HTTP ya resuelto."""

from typing import Any


class ErrorNegocio(Exception):
    """Base de todos los errores de negocio de la fabrica."""

    status_code = 400
    codigo = "error_negocio"
    mensaje = "Se produjo un error de negocio"

    def __init__(
        self,
        mensaje: str | None = None,
        errores: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.mensaje = mensaje or self.mensaje
        self.errores = errores or []
        self.headers = headers or {}
        super().__init__(self.mensaje)


class NoAutorizadoError(ErrorNegocio):
    status_code = 401
    codigo = "no_autorizado"
    mensaje = "Credenciales de autenticacion invalidas"

    def __init__(
        self,
        mensaje: str | None = None,
        errores: list[dict[str, Any]] | None = None,
    ):
        super().__init__(mensaje, errores, {"WWW-Authenticate": "Bearer"})


class NoEncontradoError(ErrorNegocio):
    status_code = 404
    codigo = "no_encontrado"
    mensaje = "El recurso solicitado no existe"


class ConflictoError(ErrorNegocio):
    status_code = 409
    codigo = "conflicto"
    mensaje = "La operacion entra en conflicto con el estado actual"


class ReglaNegocioError(ErrorNegocio):
    status_code = 422
    codigo = "regla_negocio"
    mensaje = "La operacion viola una regla de negocio"


class PermisoError(ErrorNegocio):
    status_code = 403
    codigo = "permiso"
    mensaje = "No tienes permisos para realizar esta accion"


class StockInsuficienteError(ConflictoError):
    codigo = "stock_insuficiente"
    mensaje = "No hay stock suficiente del producto solicitado"
