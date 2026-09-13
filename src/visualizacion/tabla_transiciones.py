"""Modulo para generar los datos de la tabla de transiciones.

Transforma la estructura de datos del parser en una matriz de
cadenas de texto, lista para ser consumida por el componente
visual de la interfaz grafica (ej. Treeview de tkinter).

No contiene dependencias de GUI.
"""

from __future__ import annotations

from logica.parser import ResultadoParser


class GeneradorTabla:
    """Prepara los datos matriciales para la tabla de transiciones."""

    def __init__(self, parser_resultado: ResultadoParser) -> None:
        """Inicializa el generador con los datos parseados.

        Args:
            parser_resultado: Objeto con transiciones, estados y simbolos.
        """
        self.estados = parser_resultado.estados
        self.simbolos = parser_resultado.simbolos
        self.transiciones = parser_resultado.transiciones

    def obtener_columnas(self) -> list[str]:
        """Devuelve los encabezados de las columnas.

        El primer encabezado siempre es 'Estado'. Los siguientes son
        cada uno de los simbolos del alfabeto (ordenados, con 'B' al final).

        Returns:
            Lista de cadenas con los nombres de las columnas.
        """
        return ["Estado"] + self.simbolos

    def obtener_filas(self) -> list[list[str]]:
        """Genera las filas de la tabla.

        Cada fila corresponde a un estado (en orden: q0 primero, qf ultimo).
        La primera celda de la fila es el nombre del estado.
        Las siguientes celdas contienen la definicion de la transicion:
        'estado_destino, simbolo_escrito, movimiento' o '-' si no existe.

        Returns:
            Lista de filas, donde cada fila es una lista de cadenas.
        """
        filas = []
        for estado in self.estados:
            fila = [estado]
            for simbolo in self.simbolos:
                transicion = self.transiciones.get((estado, simbolo))
                if transicion is not None:
                    # Formato: q1, a, R
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