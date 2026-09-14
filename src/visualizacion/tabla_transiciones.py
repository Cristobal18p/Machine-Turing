"""Modulo para generar los datos de la tabla de transiciones.

Transforma la estructura de datos del parser en una matriz de
cadenas de texto, lista para ser consumida por el componente
visual de la interfaz grafica (ej. Treeview de tkinter).

No contiene dependencias de GUI.
"""

from __future__ import annotations
import re

from logica.parser import ResultadoParser


class GeneradorTabla:
    """Prepara los datos matriciales para la tabla de transiciones."""

    def __init__(self, parser_resultado: ResultadoParser) -> None:
        """Inicializa el generador con los datos parseados y ordenados."""
        self.transiciones = parser_resultado.transiciones
        
        # Ordenamiento inteligente de los simbolos
        self.simbolos = sorted(list(parser_resultado.simbolos), key=self._clave_orden_simbolos)
        
        # Ordenamiento inteligente de los estados
        self.estados = sorted(parser_resultado.estados, key=self._clave_orden_estados)

    def _clave_orden_simbolos(self, simbolo: str) -> tuple:
        """Prioridades: 0 -> Numeros, 1 -> Letras alfabeticamente, 2 -> 'B' (Blanco) al final."""
        if simbolo == 'B':
            return (2, simbolo)
        if simbolo.isdigit():
            return (0, int(simbolo), simbolo)
        return (1, simbolo.lower(), simbolo)

    def _clave_orden_estados(self, estado: str) -> tuple:
        """Genera una clave de ordenamiento natural.
        
        Prioridades:
        0 -> Estado inicial (q0)
        1 -> Estados normales ordenados por el numero que contienen
        2 -> Estados de aceptacion/finales al final
        """
        estado_lower = estado.lower()
        if estado_lower == 'q0':
            return (0, 0, estado)
        if estado_lower in ('qf', 'qa', 'qr', 'aceptada', 'rechazada', 'final'):
            return (2, 0, estado)
            
        match = re.search(r'\d+', estado)
        if match:
            return (1, int(match.group()), estado)
            
        return (1, 0, estado)

    def obtener_columnas(self) -> list[str]:
        """Devuelve los encabezados de las columnas."""
        return ["Estado"] + self.simbolos

    def obtener_filas(self) -> list[list[str]]:
        """Genera las filas de la tabla ordenadas."""
        filas = []
        for estado in self.estados:
            fila = [estado]
            for simbolo in self.simbolos:
                transicion = self.transiciones.get((estado, simbolo))
                if transicion is not None:
                    celda = (
                        f"{transicion.estado_destino}, "
                        f"{transicion.simbolo_escrito}, "
                        f"{transicion.movimiento}"
                    )
                else:
                    celda = "-"
                fila.append(celda)
            filas.append(fila)

        return filas