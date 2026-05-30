"""Errores del dominio.

Tener una jerarquia propia de errores permite que las capas externas
distingan los fallos de negocio de los fallos tecnicos, manteniendo el
bajo acoplamiento.
"""


class ErrorDominio(Exception):
    """Error base para cualquier violacion de una regla de negocio."""


class TransaccionInvalida(ErrorDominio):
    """La transaccion de cena no cumple las invariantes del dominio."""


class DatosMensajeInvalidos(ErrorDominio):
    """El contenido recibido por mensajeria no se pudo interpretar."""
