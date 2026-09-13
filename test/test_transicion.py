"""Pruebas unitarias para el modulo transicion.py"""

import sys
import os
import unittest

# Agregar src al path para importar los modulos de logica.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.transicion import Transicion
from logica.errores import ErrorTransicion


class TestTransicionCreacion(unittest.TestCase):
    """Verifica que una transicion conserve sus cinco datos."""

    def test_crear_transicion_valida_R(self):
        t = Transicion("q0", "a", "q1", "b", "R")
        self.assertEqual(t.estado_origen, "q0")
        self.assertEqual(t.simbolo_leido, "a")
        self.assertEqual(t.estado_destino, "q1")
        self.assertEqual(t.simbolo_escrito, "b")
        self.assertEqual(t.movimiento, "R")

    def test_crear_transicion_valida_L(self):
        t = Transicion("q1", "B", "qf", "B", "L")
        self.assertEqual(t.estado_origen, "q1")
        self.assertEqual(t.simbolo_leido, "B")
        self.assertEqual(t.estado_destino, "qf")
        self.assertEqual(t.simbolo_escrito, "B")
        self.assertEqual(t.movimiento, "L")

    def test_transicion_con_estados_arbitrarios(self):
        t = Transicion("inicio", "X", "fin", "Y", "R")
        self.assertEqual(t.estado_origen, "inicio")
        self.assertEqual(t.estado_destino, "fin")

    def test_transicion_con_simbolos_numericos(self):
        t = Transicion("q0", "1", "q1", "0", "R")
        self.assertEqual(t.simbolo_leido, "1")
        self.assertEqual(t.simbolo_escrito, "0")


class TestTransicionInmutabilidad(unittest.TestCase):
    """Verifica que los valores no puedan modificarse despues de la creacion."""

    def test_no_modificar_estado_origen(self):
        t = Transicion("q0", "a", "q1", "b", "R")
        with self.assertRaises(AttributeError):
            t.estado_origen = "q2"

    def test_no_modificar_movimiento(self):
        t = Transicion("q0", "a", "q1", "b", "R")
        with self.assertRaises(AttributeError):
            t.movimiento = "L"


class TestTransicionValidacion(unittest.TestCase):
    """Verifica que solo acepte L y R, y que rechace campos vacios."""

    def test_movimiento_invalido(self):
        with self.assertRaises(ErrorTransicion) as ctx:
            Transicion("q0", "a", "q1", "b", "U")
        self.assertIn("invalido", str(ctx.exception).lower())

    def test_movimiento_minuscula_rechazado(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "a", "q1", "b", "r")

    def test_movimiento_vacio(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "a", "q1", "b", "")

    def test_estado_origen_vacio(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("", "a", "q1", "b", "R")

    def test_simbolo_leido_vacio(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "", "q1", "b", "R")

    def test_simbolo_leido_multiples_caracteres(self):
        with self.assertRaises(ErrorTransicion) as ctx:
            Transicion("q0", "ab", "q1", "b", "R")
        self.assertIn("exactamente un caracter", str(ctx.exception))

    def test_simbolo_escrito_multiples_caracteres(self):
        with self.assertRaises(ErrorTransicion) as ctx:
            Transicion("q0", "a", "q1", "XYZ", "R")
        self.assertIn("exactamente un caracter", str(ctx.exception))

    def test_estado_destino_vacio(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "a", "", "b", "R")

    def test_simbolo_escrito_vacio(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "a", "q1", "", "R")

    def test_campo_solo_espacios(self):
        with self.assertRaises(ErrorTransicion):
            Transicion("q0", "a", "  ", "b", "R")


class TestTransicionEtiqueta(unittest.TestCase):
    """Verifica el formato de la etiqueta del diagrama."""

    def test_etiqueta_diagrama_formato(self):
        t = Transicion("q0", "b", "q1", "a", "R")
        self.assertEqual(t.etiqueta_diagrama(), "b, a, R")

    def test_etiqueta_diagrama_con_blanco(self):
        t = Transicion("q1", "B", "qf", "B", "L")
        self.assertEqual(t.etiqueta_diagrama(), "B, B, L")

    def test_str_formato_completo(self):
        t = Transicion("q0", "b", "q1", "a", "R")
        self.assertEqual(str(t), "q0, b -> q1, a, R")


class TestTransicionIgualdad(unittest.TestCase):
    """Verifica que dos transiciones iguales sean comparables."""

    def test_transiciones_iguales(self):
        t1 = Transicion("q0", "a", "q1", "b", "R")
        t2 = Transicion("q0", "a", "q1", "b", "R")
        self.assertEqual(t1, t2)

    def test_transiciones_diferentes(self):
        t1 = Transicion("q0", "a", "q1", "b", "R")
        t2 = Transicion("q0", "a", "q1", "b", "L")
        self.assertNotEqual(t1, t2)

    def test_transicion_hasheable(self):
        t = Transicion("q0", "a", "q1", "b", "R")
        s = {t}
        self.assertIn(t, s)


if __name__ == "__main__":
    unittest.main()