"""Caso de uso principal: procesar la transaccion de una cena.

Orquesta el dominio y los puertos sin conocer las tecnologias concretas:
1. calcula la recompensa con la politica,
2. acredita los beneficios en la cuenta del cliente,
3. persiste la cuenta,
4. (opcional) publica un evento de notificacion.
"""

import logging
from dataclasses import dataclass

from ..domain.modelos import (
    CalculoRecompensa,
    CuentaRecompensas,
    EventoNotificacion,
    TransaccionCena,
)
from .puertos import PoliticaRecompensas, PublicadorEventos, RepositorioRecompensas

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoProcesamiento:
    """Salida del caso de uso, util para pruebas y para el llamador."""

    calculo: CalculoRecompensa
    cuenta: CuentaRecompensas
    notificado: bool


class ProcesarTransaccionCena:
    """Servicio de aplicacion que coordina el flujo de recompensas."""

    def __init__(
        self,
        politica: PoliticaRecompensas,
        repositorio: RepositorioRecompensas,
        publicador: PublicadorEventos | None = None,
        canal_notificacion: str = "email",
    ) -> None:
        self._politica = politica
        self._repositorio = repositorio
        self._publicador = publicador
        self._canal_notificacion = canal_notificacion

    def ejecutar(self, transaccion: TransaccionCena) -> ResultadoProcesamiento:
        calculo = self._politica.calcular(transaccion)

        cuenta = self._repositorio.obtener(transaccion.id_cuenta)
        if cuenta is None:
            cuenta = CuentaRecompensas.nueva(
                transaccion.id_cuenta, transaccion.tarjeta_enmascarada
            )

        cuenta.acreditar(calculo)
        self._repositorio.guardar(cuenta)

        logger.info(
            "Recompensa procesada: nivel=%s puntos=%s cashback=%s tarjeta=%s",
            calculo.nivel,
            calculo.puntos,
            calculo.cashback,
            transaccion.tarjeta_enmascarada,
        )

        notificado = self._notificar(transaccion, calculo)
        return ResultadoProcesamiento(calculo=calculo, cuenta=cuenta, notificado=notificado)

    def _notificar(
        self, transaccion: TransaccionCena, calculo: CalculoRecompensa
    ) -> bool:
        if self._publicador is None:
            return False
        evento = EventoNotificacion(
            tarjeta_enmascarada=transaccion.tarjeta_enmascarada,
            canal=self._canal_notificacion,
            mensaje=(
                f"Recompensa {calculo.nivel}: +{calculo.puntos} puntos y "
                f"{calculo.cashback} de cashback por su consumo."
            ),
        )
        self._publicador.publicar(evento)
        return True
