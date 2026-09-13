"""Modelo de una transicion individual de la Maquina de Turing.

Representa de forma inmutable los cinco datos de una transicion:
estado_origen, simbolo_leido, estado_destino, simbolo_escrito y movimiento.

Este modulo no conoce la interfaz, la cinta ni Graphviz.
"""

from dataclasses import dataclass

from logica.errores import ErrorTransicion

_MOVIMIENTOS_VALIDOS = frozenset({"L", "R"})


@dataclass(frozen=True, slots=True)
class Transicion:
    """Transicion individual de una Maquina de Turing.

    Attributes:
        estado_origen: Estado en el que se encuentra la maquina.
        simbolo_leido: Simbolo que lee el cabezal.
        estado_destino: Estado al que transita la maquina.
        simbolo_escrito: Simbolo que escribe el cabezal.
        movimiento: Direccion del movimiento del cabezal ('L' o 'R').
    """

    estado_origen: str
    simbolo_leido: str
    estado_destino: str
    simbolo_escrito: str
    movimiento: str

    def __post_init__(self) -> None:
        # Validar que ningun campo este vacio.
        campos = {
            "estado_origen": self.estado_origen,
            "simbolo_leido": self.simbolo_leido,
            "estado_destino": self.estado_destino,
            "simbolo_escrito": self.simbolo_escrito,
            "movimiento": self.movimiento,
        }
        for nombre, valor in campos.items():
            if not valor or not valor.strip():
                raise ErrorTransicion(
                    f"El campo '{nombre}' no puede estar vacio."
                )

        # Validar que el movimiento sea L o R.
        if self.movimiento not in _MOVIMIENTOS_VALIDOS:
            raise ErrorTransicion(
                f"Movimiento invalido: '{self.movimiento}'. "
                f"Solo se permite 'L' o 'R'."
            )

    def etiqueta_diagrama(self) -> str:
        """Produce la etiqueta para una arista del diagrama de transiciones.

        Formato: 'simbolo_leido, simbolo_escrito, movimiento'

        Returns:
            Cadena con el formato requerido por el diagrama.
        """
        return f"{self.simbolo_leido}, {self.simbolo_escrito}, {self.movimiento}"

    def __str__(self) -> str:
        """Representacion legible de la transicion completa."""
        return (
            f"{self.estado_origen}, {self.simbolo_leido} -> "
            f"{self.estado_destino}, {self.simbolo_escrito}, {self.movimiento}"
        )