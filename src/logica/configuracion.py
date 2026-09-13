"""Modelo de la configuracion instantanea de la Maquina de Turing.

Una configuracion es una fotografia de la maquina en un instante
determinado. Es la unidad que se agrega al historial y que la
interfaz muestra como descripcion instantanea.

Decisiones tecnicas:
  - La cinta se almacena como MappingProxyType (copia inmutable)
    para garantizar que cada configuracion sea una fotografia real
    que no se corrompe cuando el motor modifica la cinta despues.
  - Se distingue entre transicion_aplicada (la que produjo este
    estado) y transicion_pendiente (la que se ejecutara a
    continuacion), porque ambas pueden mostrarse en un mismo paso.

Este modulo es independiente de los widgets y de la interfaz grafica.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logica.transicion import Transicion


@dataclass(frozen=True, slots=True)
class Configuracion:
    """Fotografia inmutable de la maquina en un instante determinado.

    Attributes:
        paso: Numero de paso (0 = configuracion inicial).
        estado: Estado actual de la maquina.
        posicion_cabezal: Posicion del cabezal sobre la cinta.
        cinta: Vista de solo lectura del contenido de la cinta
               {posicion: simbolo}. Se almacena como MappingProxyType
               para impedir modificaciones accidentales.
        simbolo_leido: Simbolo que el cabezal lee en la posicion actual.
        transicion_aplicada: Transicion que se aplico para llegar a este
                             estado, o None si es la configuracion inicial.
        transicion_pendiente: Transicion que se aplicara a continuacion,
                              o None si la maquina se detuvo o no existe
                              transicion disponible.
        motivo_detencion: Razon por la que la maquina se detuvo, o None
                          si la maquina no se ha detenido en este paso.
    """

    paso: int
    estado: str
    posicion_cabezal: int
    cinta: MappingProxyType
    simbolo_leido: str
    transicion_aplicada: "Transicion | None" = field(default=None)
    transicion_pendiente: "Transicion | None" = field(default=None)
    motivo_detencion: str | None = field(default=None)

    def __post_init__(self) -> None:
        """Convierte la cinta a MappingProxyType si se recibio un dict."""
        if isinstance(self.cinta, dict):
            object.__setattr__(
                self, "cinta", MappingProxyType(dict(self.cinta))
            )

    def cinta_como_lista(self) -> list[str]:
        """Devuelve el contenido de la cinta como lista ordenada por posicion.

        Returns:
            Lista de simbolos desde la posicion minima hasta la maxima.
        """
        if not self.cinta:
            return []
        pos_min = min(self.cinta)
        pos_max = max(self.cinta)
        return [self.cinta.get(i, "B") for i in range(pos_min, pos_max + 1)]

    def indice_cabezal_en_lista(self) -> int:
        """Devuelve el indice del cabezal relativo a la lista de cinta_como_lista().

        Returns:
            Indice entero (0-indexado) del cabezal dentro de la lista.
        """
        if not self.cinta:
            return 0
        return self.posicion_cabezal - min(self.cinta)

    def formato_bloque(self) -> str:
        """Genera la descripcion instantanea en formato de bloque.

        Ejemplo para Paso 0 (solo pendiente):
            Paso: 0
            Estado: q0
            Cinta: a  b  a  b  b  B
            Cabezal: ^
            Simbolo leido: a
            Transicion pendiente: q0, a -> q0, a, R

        Ejemplo para Paso 1 (aplicada + pendiente):
            Paso: 1
            Estado: q0
            Cinta: a  b  a  b  b  B
            Cabezal:    ^
            Simbolo leido: b
            Transicion aplicada: q0, a -> q0, a, R
            Transicion pendiente: q0, b -> q1, a, R

        Returns:
            Cadena multilinea con la descripcion instantanea.
        """
        simbolos = self.cinta_como_lista()
        indice = self.indice_cabezal_en_lista()

        cinta_str = "  ".join(simbolos)

        # Calcular la posicion del cursor '^' bajo el simbolo correcto.
        desplazamiento = 0
        for i in range(indice):
            desplazamiento += len(simbolos[i]) + 2  # simbolo + "  "
        cabezal_str = " " * desplazamiento + "^"

        lineas = [
            f"Paso: {self.paso}",
            f"Estado: {self.estado}",
            f"Cinta: {cinta_str}",
            f"Cabezal: {cabezal_str}",
            f"Simbolo leido: {self.simbolo_leido}",
        ]

        if self.transicion_aplicada is not None:
            lineas.append(f"Transicion aplicada: {self.transicion_aplicada}")

        if self.transicion_pendiente is not None:
            lineas.append(f"Transicion pendiente: {self.transicion_pendiente}")

        if self.motivo_detencion is not None:
            lineas.append(f"Resultado: {self.motivo_detencion}")

        return "\n".join(lineas)

    def __str__(self) -> str:
        return self.formato_bloque()