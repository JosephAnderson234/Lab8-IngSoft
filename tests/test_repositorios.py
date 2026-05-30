from decimal import Decimal

import pytest

from rewards.domain.modelos import CalculoRecompensa, CuentaRecompensas
from rewards.infrastructure.persistence.repositorio_memoria import (
    RepositorioRecompensasEnMemoria,
)
from rewards.infrastructure.persistence.repositorio_sqlite import (
    RepositorioRecompensasSqlite,
)


def _cuenta():
    cuenta = CuentaRecompensas.nueva("id-1", "**** 1111")
    cuenta.acreditar(CalculoRecompensa(puntos=10, cashback=Decimal("2.50"), nivel="PLATA"))
    return cuenta


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request, tmp_path):
    if request.param == "memoria":
        return RepositorioRecompensasEnMemoria()
    return RepositorioRecompensasSqlite(str(tmp_path / "test.db"))


def test_obtener_inexistente_devuelve_none(repositorio):
    assert repositorio.obtener("desconocido") is None


def test_guardar_y_obtener(repositorio):
    cuenta = _cuenta()
    repositorio.guardar(cuenta)
    recuperada = repositorio.obtener("id-1")
    assert recuperada.puntos_totales == 10
    assert recuperada.cashback_total == Decimal("2.50")
    assert recuperada.tarjeta_enmascarada == "**** 1111"


def test_actualizar_existente(repositorio):
    cuenta = _cuenta()
    repositorio.guardar(cuenta)
    cuenta.acreditar(CalculoRecompensa(puntos=5, cashback=Decimal("1.00"), nivel="BRONCE"))
    repositorio.guardar(cuenta)
    recuperada = repositorio.obtener("id-1")
    assert recuperada.puntos_totales == 15
    assert recuperada.cashback_total == Decimal("3.50")


def test_memoria_devuelve_copia_independiente():
    repo = RepositorioRecompensasEnMemoria()
    cuenta = _cuenta()
    repo.guardar(cuenta)
    recuperada = repo.obtener("id-1")
    recuperada.puntos_totales = 999  # mutar la copia no afecta al repositorio
    assert repo.obtener("id-1").puntos_totales == 10


def test_sqlite_persiste_actualizada_en(tmp_path):
    repo = RepositorioRecompensasSqlite(str(tmp_path / "t.db"))
    cuenta = _cuenta()
    repo.guardar(cuenta)
    assert repo.obtener("id-1").actualizada_en is not None
    repo.cerrar()
