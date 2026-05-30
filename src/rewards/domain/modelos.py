"""Entidades y objetos de valor del programa de recompensas.

Estas estructuras concentran las invariantes del negocio (alta cohesion)
y no conocen nada sobre mensajeria, base de datos o frameworks.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from .errores import TransaccionInvalida
from .seguridad import enmascarar_tarjeta, identificador_cuenta

_DOS_DECIMALES = Decimal("0.01")


def _a_decimal(valor) -> Decimal:
    """Convierte un valor monetario a Decimal con dos decimales."""
    try:
        return Decimal(str(valor)).quantize(_DOS_DECIMALES)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise TransaccionInvalida(f"Monto no numerico: {valor!r}") from exc


@dataclass(frozen=True)
class TransaccionCena:
    """Cena consumida por un cliente en un restaurante afiliado.

    Es un objeto de valor inmutable: una vez validado no cambia.
    """

    id_transaccion: str
    monto: Decimal
    numero_tarjeta: str
    codigo_restaurante: str
    fecha_hora: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "monto", _a_decimal(self.monto))
        if not self.id_transaccion:
            raise TransaccionInvalida("La transaccion requiere un identificador")
        if self.monto <= Decimal("0"):
            raise TransaccionInvalida("El monto debe ser mayor que cero")
        if len(self.numero_tarjeta or "") < 4:
            raise TransaccionInvalida("Numero de tarjeta invalido")
        if not self.codigo_restaurante:
            raise TransaccionInvalida("Se requiere el codigo del restaurante")
        if not isinstance(self.fecha_hora, datetime):
            raise TransaccionInvalida("La fecha y hora deben ser datetime")

    @property
    def tarjeta_enmascarada(self) -> str:
        return enmascarar_tarjeta(self.numero_tarjeta)

    @property
    def id_cuenta(self) -> str:
        return identificador_cuenta(self.numero_tarjeta)


@dataclass(frozen=True)
class CalculoRecompensa:
    """Resultado de aplicar la politica de recompensas a una cena."""

    puntos: int
    cashback: Decimal
    nivel: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "cashback", _a_decimal(self.cashback))
        if self.puntos < 0:
            raise TransaccionInvalida("Los puntos no pueden ser negativos")
        if self.cashback < Decimal("0"):
            raise TransaccionInvalida("El cashback no puede ser negativo")


@dataclass
class CuentaRecompensas:
    """Cuenta acumulada de recompensas de un cliente.

    Entidad con identidad propia (``id_cuenta``) y estado mutable: acumula
    los beneficios calculados para cada cena.
    """

    id_cuenta: str
    tarjeta_enmascarada: str
    puntos_totales: int = 0
    cashback_total: Decimal = field(default_factory=lambda: Decimal("0.00"))
    actualizada_en: datetime | None = None

    @classmethod
    def nueva(cls, id_cuenta: str, tarjeta_enmascarada: str) -> "CuentaRecompensas":
        return cls(id_cuenta=id_cuenta, tarjeta_enmascarada=tarjeta_enmascarada)

    def acreditar(self, calculo: CalculoRecompensa, momento: datetime | None = None) -> None:
        """Suma los beneficios calculados a la cuenta."""
        self.puntos_totales += calculo.puntos
        self.cashback_total = _a_decimal(self.cashback_total + calculo.cashback)
        self.actualizada_en = momento or datetime.now(timezone.utc)


@dataclass(frozen=True)
class EventoNotificacion:
    """Evento emitido cuando una recompensa se proceso correctamente."""

    tarjeta_enmascarada: str
    canal: str
    mensaje: str
