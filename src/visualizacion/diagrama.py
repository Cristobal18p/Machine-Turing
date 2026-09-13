"""Modulo para generar el diagrama de transiciones usando Graphviz.

Este modulo construye la representacion visual del grafo. Si la libreria
graphviz no esta disponible en el entorno, proporciona mecanismos para 
manejar su ausencia sin romper la aplicacion (degradacion elegante).
"""

from __future__ import annotations

import logging

try:
    import graphviz
    GRAPHVIZ_DISPONIBLE = True
except ImportError:
    GRAPHVIZ_DISPONIBLE = False

from logica.parser import ResultadoParser


class GeneradorDiagrama:
    """Construye el diagrama de transiciones de la Maquina de Turing."""

    def __init__(self, parser_resultado: ResultadoParser) -> None:
        """Inicializa el generador con los datos parseados.

        Args:
            parser_resultado: Objeto con transiciones, estados y simbolos.
        """
        self.estados = parser_resultado.estados
        self.transiciones = parser_resultado.transiciones.values()

    def construir_grafo(self) -> "graphviz.Digraph | None":
        """Construye el objeto Digraph de Graphviz.

        Returns:
            El objeto Digraph configurado listo para renderizar, o None
            si la libreria graphviz no esta instalada en el sistema.
        """
        if not GRAPHVIZ_DISPONIBLE:
            logging.warning("Libreria graphviz no encontrada. Diagrama deshabilitado.")
            return None

        # Crear grafo dirigido con orientacion de Izquierda a Derecha (LR)
        dot = graphviz.Digraph(
            name="Maquina_de_Turing",
            comment="Diagrama de Transiciones",
            format="png"
        )
        dot.attr(rankdir="LR")

        # 1. Configurar los nodos (estados)
        for estado in self.estados:
            if estado == "qf":
                # Estado final con doble circulo
                dot.node(estado, estado, shape="doublecircle")
            else:
                # Estados normales con circulo simple
                dot.node(estado, estado, shape="circle")

        # 2. Flecha de entrada al estado inicial (convencion de automatas)
        if "q0" in self.estados:
            dot.node("start", "", shape="none", width="0", height="0")
            dot.edge("start", "q0")

        # 3. Agrupar transiciones por (origen, destino)
        # Esto evita multiples flechas entre los mismos dos nodos,
        # unificando las etiquetas con saltos de linea.
        aristas: dict[tuple[str, str], list[str]] = {}
        for t in self.transiciones:
            clave = (t.estado_origen, t.estado_destino)
            if clave not in aristas:
                aristas[clave] = []
            aristas[clave].append(t.etiqueta_diagrama())

        # 4. Crear las aristas
        for (origen, destino), etiquetas in aristas.items():
            # Unir multiples etiquetas con salto de linea
            label = "\n".join(etiquetas)
            dot.edge(origen, destino, label=label)

        return dot