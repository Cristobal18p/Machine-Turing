"""Pruebas unitarias para el modulo tabla.py (Enfoque Dinamico)"""

import sys
import os
import unittest
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.parser import ResultadoParser
from logica.transicion import Transicion
from visualizacion.tabla_transiciones import GeneradorTabla


class TestGeneradorTablaDinamico(unittest.TestCase):
    """Verifica la generacion de la tabla garantizando las reglas dinamicas."""

    def _verificar_generador(self, resultado: ResultadoParser):
        """Verifica dinamicamente que el generador cumpla las reglas para los datos dados.
        
        No utiliza valores fijos, sino que reconstruye la expectativa basandose
        unicamente en los datos del ResultadoParser ingresado.
        """
        gen = GeneradorTabla(resultado)
        columnas = gen.obtener_columnas()
        filas = gen.obtener_filas()

        # Regla 1: Las columnas deben ser ["Estado"] seguido de todos los simbolos
        esperado_columnas = ["Estado"] + resultado.simbolos
        self.assertEqual(
            columnas, esperado_columnas, 
            "Las columnas no coinciden con los simbolos definidos."
        )

        # Regla 2: Debe haber exactamente una fila por cada estado
        self.assertEqual(
            len(filas), len(resultado.estados), 
            "La cantidad de filas no coincide con los estados."
        )

        # Regla 3: El contenido de cada celda debe corresponder al diccionario
        for i, estado in enumerate(resultado.estados):
            fila = filas[i]
            # La primera celda de la fila debe ser el nombre del estado
            self.assertEqual(
                fila[0], estado, 
                f"La primera columna de la fila {i} debe ser el estado '{estado}'."
            )
            
            # Las siguientes celdas corresponden a cada simbolo
            for j, simbolo in enumerate(resultado.simbolos):
                celda_actual = fila[j + 1]
                transicion = resultado.transiciones.get((estado, simbolo))
                
                # Si existe, el formato es especifico. Si no, es "-"
                if transicion is not None:
                    celda_esperada = (
                        f"{transicion.estado_destino}, "
                        f"{transicion.simbolo_escrito}, "
                        f"{transicion.movimiento}"
                    )
                else:
                    celda_esperada = "-"
                    
                self.assertEqual(
                    celda_actual, celda_esperada, 
                    f"Falla en celda del estado '{estado}' y simbolo '{simbolo}'. "
                    f"Se esperaba '{celda_esperada}', pero se obtuvo '{celda_actual}'."
                )

    def test_datos_aleatorios(self):
        """Prueba con datos generados arbitrariamente (sin valores fijos predeterminados)."""
        # 1. Generar estados abstractos (ej. S_0, S_1...) y simbolos abstractos (x_0, x_1...)
        estados_random = [f"S_{i}" for i in range(6)]
        simbolos_random = [chr(97 + i) for i in range(4)] + ["B"]  # a, b, c, d, B
        
        # 2. Poblar transiciones aleatoriamente
        transiciones_random = {}
        # Usamos semilla fija solo para que la prueba sea determinista si falla
        random.seed(42) 
        for estado in estados_random:
            for simbolo in simbolos_random:
                # 50% de probabilidad de que exista una transicion
                if random.choice([True, False]):
                    est_dest = random.choice(estados_random)
                    sim_esc = random.choice(simbolos_random)
                    mov = random.choice(["L", "R"])
                    transiciones_random[(estado, simbolo)] = Transicion(
                        estado_origen=estado,
                        simbolo_leido=simbolo,
                        estado_destino=est_dest,
                        simbolo_escrito=sim_esc,
                        movimiento=mov
                    )
        
        resultado = ResultadoParser(
            transiciones=transiciones_random,
            estados=estados_random,
            simbolos=simbolos_random
        )
        
        # 3. Verificar que la tabla se arme perfectamente para esta maquina abstracta
        self._verificar_generador(resultado)

    def test_datos_minimos(self):
        """Prueba con la minima expresion de datos validos."""
        t = Transicion("A", "0", "B", "1", "R")
        resultado = ResultadoParser(
            transiciones={("A", "0"): t},
            estados=["A", "B"],
            simbolos=["0", "1"]
        )
        self._verificar_generador(resultado)

    def test_sin_transiciones(self):
        """Prueba una maquina vacia donde no se cargo nada."""
        resultado_vacio = ResultadoParser(transiciones={}, estados=[], simbolos=[])
        self._verificar_generador(resultado_vacio)


if __name__ == "__main__":
    unittest.main()