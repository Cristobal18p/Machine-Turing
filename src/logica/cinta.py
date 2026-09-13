"""Modulo de cinta de la Maquina de Turing.

Representa la cinta infinita y las operaciones del cabezal:
lectura, escritura y movimiento en ambas direcciones.

La cinta se implementa como un diccionario {posicion: simbolo}
para permitir extension en ambas direcciones usando posiciones
negativas hacia la izquierda.

Reglas:
  - La posicion inicial del cabezal es 0 (primer caracter de la cadena).
  - La cinta contiene un blanco 'B' a la derecha de la entrada.
  - Si el cabezal se mueve fuera del rango conocido, se crea una celda 'B'.
  - No se elimina informacion escrita anteriormente.
"""

from __future__ import annotations

BLANCO = "B"


class Cinta:
    """Cinta de una Maquina de Turing con extension en ambas direcciones.

    Attributes:
        _celdas: Diccionario {posicion_entera: simbolo} con el contenido.
        _posicion: Posicion actual del cabezal.
    """

    def __init__(self, cadena: str) -> None:
        """Inicializa la cinta a partir de una cadena de entrada.

        Cada caracter se coloca en las posiciones 0, 1, 2, ...
        Se agrega un blanco 'B' inmediatamente despues del ultimo caracter.
        El cabezal se coloca en la posicion 0.

        Args:
            cadena: Cadena de entrada para la maquina. Puede estar vacia.
        """
        self._celdas: dict[int, str] = {}
        for i, caracter in enumerate(cadena):
            self._celdas[i] = caracter
        # Blanco a la derecha de la entrada.
        self._celdas[len(cadena)] = BLANCO
        self._posicion: int = 0


    #  Propiedades                                                        
    @property
    def posicion(self) -> int:
        """Posicion actual del cabezal."""
        return self._posicion


    #  Operaciones del cabezal                                            
    def leer(self) -> str:
        """Lee el simbolo en la posicion actual del cabezal.

        Si la posicion no tiene una celda explicita, devuelve BLANCO.

        Returns:
            El simbolo bajo el cabezal.
        """
        return self._celdas.get(self._posicion, BLANCO)

    def escribir(self, simbolo: str) -> None:
        """Escribe un simbolo en la posicion actual del cabezal.

        Cada celda de la cinta contiene exactamente un caracter.

        Args:
            simbolo: Simbolo a escribir en la celda actual (1 caracter).

        Raises:
            ValueError: Si el simbolo no es exactamente un caracter.
        """
        if len(simbolo) != 1:
            raise ValueError(
                f"El simbolo debe ser exactamente un caracter, "
                f"se recibio: '{simbolo}' ({len(simbolo)} caracteres)."
            )
        self._celdas[self._posicion] = simbolo

    def mover_derecha(self) -> None:
        """Mueve el cabezal una posicion a la derecha.

        Si la nueva posicion no existe en la cinta, se crea con BLANCO.
        """
        self._posicion += 1
        if self._posicion not in self._celdas:
            self._celdas[self._posicion] = BLANCO

    def mover_izquierda(self) -> None:
        """Mueve el cabezal una posicion a la izquierda.

        Si la nueva posicion no existe (incluyendo posiciones negativas),
        se crea con BLANCO.
        """
        self._posicion -= 1
        if self._posicion not in self._celdas:
            self._celdas[self._posicion] = BLANCO

    def mover(self, direccion: str) -> None:
        """Mueve el cabezal en la direccion indicada.

        Args:
            direccion: 'R' para derecha, 'L' para izquierda.

        Raises:
            ValueError: Si la direccion no es 'L' ni 'R'.
        """
        if direccion == "R":
            self.mover_derecha()
        elif direccion == "L":
            self.mover_izquierda()
        else:
            raise ValueError(f"Direccion invalida: '{direccion}'")

    #  Vista para la interfaz y para Configuracion                        
    def obtener_contenido(self) -> dict[int, str]:
        """Devuelve una copia del contenido de la cinta.

        La copia es independiente: modificarla no afecta la cinta real.
        Se usa para crear fotografias inmutables en Configuracion.

        Returns:
            Diccionario {posicion: simbolo} con todas las celdas conocidas.
        """
        return dict(self._celdas)

    def contenido_como_lista(self) -> list[str]:
        """Devuelve el contenido de la cinta como lista ordenada.

        Returns:
            Lista de simbolos desde la posicion minima hasta la maxima.
        """
        if not self._celdas:
            return []
        pos_min = min(self._celdas)
        pos_max = max(self._celdas)
        return [self._celdas.get(i, BLANCO) for i in range(pos_min, pos_max + 1)]

    def __str__(self) -> str:
        """Representacion legible de la cinta con el cabezal marcado."""
        simbolos = self.contenido_como_lista()
        if not simbolos:
            return "[B]  ^"
        pos_min = min(self._celdas)
        indice_cabezal = self._posicion - pos_min
        partes = []
        for i, s in enumerate(simbolos):
            if i == indice_cabezal:
                partes.append(f"[{s}]")
            else:
                partes.append(f" {s} ")
        return "".join(partes)