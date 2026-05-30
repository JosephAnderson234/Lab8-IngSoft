from datetime import datetime, timezone
from decimal import Decimal

from rewards.application.caso_uso import ProcesarTransaccionCena
from rewards.application.politica import PoliticaRecompensasEstandar
from rewards.domain.modelos import TransaccionCena
from rewards.infrastructure.messaging.memoria import (
    BrokerEnMemoria,
    PublicadorEventosEnMemoria,
)
from rewards.infrastructure.persistence.repositorio_memoria import (
    RepositorioRecompensasEnMemoria,
)


def _transaccion(monto="150.00", tarjeta="4111111111111111"):
    return TransaccionCena(
        id_transaccion="t-1",
        monto=Decimal(monto),
        numero_tarjeta=tarjeta,
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )


def _caso_uso(con_publicador=True):
    broker = BrokerEnMemoria()
    repositorio = RepositorioRecompensasEnMemoria()
    publicador = PublicadorEventosEnMemoria(broker) if con_publicador else None
    caso = ProcesarTransaccionCena(
        politica=PoliticaRecompensasEstandar(),
        repositorio=repositorio,
        publicador=publicador,
    )
    return caso, repositorio, broker


def test_procesa_y_persiste_cuenta_nueva():
    caso, repositorio, broker = _caso_uso()
    resultado = caso.ejecutar(_transaccion("150.00"))

    assert resultado.calculo.nivel == "PLATA"
    assert resultado.notificado is True
    cuenta = repositorio.obtener(resultado.cuenta.id_cuenta)
    assert cuenta.puntos_totales == 150
    assert cuenta.cashback_total == Decimal("4.50")
    assert len(broker.notificaciones) == 1
    # La notificacion no debe exponer el numero real de tarjeta.
    assert "4111111111111111" not in broker.notificaciones[0].mensaje


def test_acumula_sobre_cuenta_existente():
    caso, repositorio, _ = _caso_uso()
    caso.ejecutar(_transaccion("100.00"))
    resultado = caso.ejecutar(_transaccion("100.00"))
    cuenta = repositorio.obtener(resultado.cuenta.id_cuenta)
    assert cuenta.puntos_totales == 200


def test_sin_publicador_no_notifica():
    caso, _, broker = _caso_uso(con_publicador=False)
    resultado = caso.ejecutar(_transaccion())
    assert resultado.notificado is False
    assert broker.notificaciones == []
