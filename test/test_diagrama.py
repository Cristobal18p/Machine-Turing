"""Pruebas unitarias para el modulo diagrama.py"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.parser import ResultadoParser
from logica.transicion import Transicion
from visualizacion.diagrama import GeneradorDiagrama, GRAPHVIZ_DISPONIBLE


class TestGeneradorDiagrama(unittest.TestCase):
    """Verifica la correcta generacion del codigo fuente DOT de Graphviz."""

    def setUp(self):
        """Prepara una maquina de prueba."""
        t1 = Transicion("q0", "a", "q0", "a", "R")
        t2 = Transicion("q0", "b", "q1", "a", "R")
        t3 = Transicion("q1", "B", "qf", "B", "L")
        
        self.resultado = ResultadoParser(
            transiciones={
                ("q0", "a"): t1,
                ("q0", "b"): t2,
                ("q1", "B"): t3,
            },
            estados=["q0", "q1", "qf"],
            simbolos=["a", "b", "B"]
        )

    def test_comportamiento_sin_graphviz(self):
        """Verifica la degradacion elegante simulando que graphviz no esta."""
        import visualizacion.diagrama as modulo_diag
        
        # Guardar el estado original
        estado_original = modulo_diag.GRAPHVIZ_DISPONIBLE
        
        try:
            # Simular que no esta instalado
            modulo_diag.GRAPHVIZ_DISPONIBLE = False
            
            gen = GeneradorDiagrama(self.resultado)
            dot = gen.construir_grafo()
            
            # Debe retornar None si no esta disponible
            self.assertIsNone(dot)
        finally:
            # Restaurar para no afectar otras pruebas
            modulo_diag.GRAPHVIZ_DISPONIBLE = estado_original

    @unittest.skipIf(not GRAPHVIZ_DISPONIBLE, "graphviz no esta instalado")
    def test_nodos_y_formas(self):
        """Verifica que qf sea doublecircle y el resto circle."""
        generador = GeneradorDiagrama(self.resultado)
        dot = generador.construir_grafo()
        self.assertIsNotNone(dot)
        
        fuente = dot.source
        
        # Verificar configuracion general
        self.assertIn('rankdir=LR', fuente)
        
        # Nodo inicial invisible
        self.assertIn('start [', fuente)
        self.assertIn('label=""', fuente)
        self.assertIn('shape=none', fuente)
        self.assertIn('start -> q0', fuente)
        
        # q0 y q1 en circle
        self.assertIn('q0 [label=q0 shape=circle]', fuente)
        self.assertIn('q1 [label=q1 shape=circle]', fuente)
        
        # qf en doublecircle
        self.assertIn('qf [label=qf shape=doublecircle]', fuente)

    @unittest.skipIf(not GRAPHVIZ_DISPONIBLE, "graphviz no esta instalado")
    def test_agrupacion_de_transiciones(self):
        """Verifica que transiciones entre los mismos nodos se unan."""
        generador = GeneradorDiagrama(self.resultado)
        dot = generador.construir_grafo()
        fuente = dot.source
        
        # La transicion q0 -> q1 (t2)
        self.assertIn('q0 -> q1 [label="b, a, R"]', fuente)
        
        # La transicion q1 -> qf (t3)
        self.assertIn('q1 -> qf [label="B, B, L"]', fuente)

    @unittest.skipIf(not GRAPHVIZ_DISPONIBLE, "graphviz no esta instalado")
    def test_unificacion_multilinea(self):
        """Si hay dos transiciones qA -> qB, deben unirse con \\n."""
        t_x = Transicion("qA", "0", "qB", "1", "R")
        t_y = Transicion("qA", "1", "qB", "0", "L")
        
        resultado = ResultadoParser(
            transiciones={("qA", "0"): t_x, ("qA", "1"): t_y},
            estados=["qA", "qB"],
            simbolos=["0", "1"]
        )
        
        gen = GeneradorDiagrama(resultado)
        dot = gen.construir_grafo()
        fuente = dot.source
        
        # Verificar que aparezcan ambas etiquetas unidas por un salto de linea real en el DOT
        self.assertIn('label="0, 1, R\n1, 0, L"', fuente)


if __name__ == "__main__":
    unittest.main()