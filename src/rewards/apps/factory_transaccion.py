"""Construccion de transacciones de cena (compartido por las apps y pruebas)."""

from datetime import datetime, timezone
from decimal import Decimal

from ..domain.modelos import TransaccionCena


def construir_transaccion(
    id_transaccion: str,
    monto,
    numero_tarjeta: str,
    codigo_restaurante: str,
    fecha_hora: datetime | None = None,
) -> TransaccionCena:
    """Crea y valida una transaccion de cena a partir de datos simples."""
    return TransaccionCena(
        id_transaccion=id_transaccion,
        monto=Decimal(str(monto)),
        numero_tarjeta=numero_tarjeta,
        codigo_restaurante=codigo_restaurante,
        fecha_hora=fecha_hora or datetime.now(timezone.utc),
    )
