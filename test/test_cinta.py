"""Pruebas unitarias para el modulo cinta.py"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.cinta import Cinta, BLANCO



#  Creacion e inicializacion                                          
class TestCintaCreacion(unittest.TestCase):
    """Verifica la inicializacion de la cinta a partir de una cadena."""

    def test_cadena_normal(self):
        c = Cinta("ababb")
        self.assertEqual(c.posicion, 0)
        self.assertEqual(c.leer(), "a")
        self.assertEqual(
            c.contenido_como_lista(), ["a", "b", "a", "b", "b"]
        )

    def test_cadena_un_caracter(self):
        c = Cinta("x")
        self.assertEqual(c.posicion, 0)
        self.assertEqual(c.leer(), "x")
        self.assertEqual(c.contenido_como_lista(), ["x"])

    def test_cadena_vacia(self):
        """Una cadena vacia debe tener solo un blanco en posicion 0."""
        c = Cinta("")
        self.assertEqual(c.posicion, 0)
        self.assertEqual(c.leer(), "B")
        self.assertEqual(c.contenido_como_lista(), [])

    def test_blanco_a_la_derecha(self):
        c = Cinta("ab")
        c.mover_derecha()
        c.mover_derecha()
        self.assertEqual(c.leer(), "B")

    def test_cabezal_inicia_en_posicion_0(self):
        c = Cinta("abc")
        self.assertEqual(c.posicion, 0)

    def test_cadena_con_simbolos_numericos(self):
        c = Cinta("101")
        self.assertEqual(c.contenido_como_lista(), ["1", "0", "1"])


#  Lectura                                                            #
class TestCintaLectura(unittest.TestCase):
    """Verifica la lectura del simbolo bajo el cabezal."""

    def test_leer_primer_caracter(self):
        c = Cinta("abc")
        self.assertEqual(c.leer(), "a")

    def test_leer_despues_de_mover(self):
        c = Cinta("abc")
        c.mover_derecha()
        self.assertEqual(c.leer(), "b")

    def test_leer_blanco_al_final(self):
        c = Cinta("a")
        c.mover_derecha()
        self.assertEqual(c.leer(), "B")


#  Escritura                                                          
class TestCintaEscritura(unittest.TestCase):
    """Verifica la escritura de simbolos."""

    def test_escribir_simbolo_diferente(self):
        """Escribir un simbolo diferente al leido debe cambiar la celda."""
        c = Cinta("ab")
        self.assertEqual(c.leer(), "a")
        c.escribir("X")
        self.assertEqual(c.leer(), "X")
        self.assertEqual(c.contenido_como_lista(), ["X", "b"])

    def test_escribir_mismo_simbolo(self):
        c = Cinta("ab")
        c.escribir("a")
        self.assertEqual(c.leer(), "a")

    def test_escribir_no_pierde_datos_anteriores(self):
        """Escribir sobre una celda no debe afectar celdas vecinas."""
        c = Cinta("abc")
        c.mover_derecha()
        c.escribir("X")
        self.assertEqual(c.contenido_como_lista(), ["a", "X", "c"])

    def test_escribir_en_blanco(self):
        c = Cinta("a")
        c.mover_derecha()  # ahora en B
        c.escribir("Y")
        self.assertEqual(c.leer(), "Y")

    def test_escribir_blanco_sobre_simbolo(self):
        c = Cinta("ab")
        c.escribir("B")
        self.assertEqual(c.leer(), "B")
        self.assertEqual(c.contenido_como_lista(), ["B", "b"])

    def test_escribir_simbolo_invalido_multiples_caracteres(self):
        c = Cinta("ab")
        with self.assertRaises(ValueError) as ctx:
            c.escribir("XYZ")
        self.assertIn("exactamente un caracter", str(ctx.exception))
        
    def test_escribir_simbolo_invalido_vacio(self):
        c = Cinta("ab")
        with self.assertRaises(ValueError) as ctx:
            c.escribir("")
        self.assertIn("exactamente un caracter", str(ctx.exception))


#  Movimiento a la derecha                                            
class TestCintaMovimientoDerecha(unittest.TestCase):
    """Verifica el movimiento del cabezal a la derecha."""

    def test_mover_derecha_basico(self):
        c = Cinta("ab")
        c.mover_derecha()
        self.assertEqual(c.posicion, 1)
        self.assertEqual(c.leer(), "b")

    def test_mover_derecha_sobre_blanco(self):
        """Mover a la derecha mas alla de la cadena debe leer B."""
        c = Cinta("a")
        c.mover_derecha()  # posicion 1 = B (ya existe)
        self.assertEqual(c.leer(), "B")
        c.mover_derecha()  # posicion 2 = B (nueva celda creada)
        self.assertEqual(c.leer(), "B")
        self.assertEqual(c.posicion, 2)

    def test_mover_derecha_crea_celda_B(self):
        """Moverse mas alla del ultimo blanco debe crear nuevas celdas B."""
        c = Cinta("a")
        c.mover_derecha()  # pos 1: B existente
        c.mover_derecha()  # pos 2: nueva celda B
        c.mover_derecha()  # pos 3: nueva celda B
        self.assertEqual(c.leer(), "B")

    def test_mover_con_R(self):
        c = Cinta("ab")
        c.mover("R")
        self.assertEqual(c.posicion, 1)



#  Movimiento a la izquierda                                          
class TestCintaMovimientoIzquierda(unittest.TestCase):
    """Verifica el movimiento del cabezal a la izquierda."""

    def test_mover_izquierda_desde_posicion_1(self):
        c = Cinta("ab")
        c.mover_derecha()  # pos 1
        c.mover_izquierda()  # pos 0
        self.assertEqual(c.posicion, 0)
        self.assertEqual(c.leer(), "a")

    def test_mover_izquierda_desde_posicion_0(self):
        """Moverse a la izquierda desde 0 debe ir a posicion -1 con B."""
        c = Cinta("ab")
        c.mover_izquierda()
        self.assertEqual(c.posicion, -1)
        self.assertEqual(c.leer(), "B")

    def test_mover_izquierda_no_pierde_cadena(self):
        """Al moverse a la izquierda la cadena original debe conservarse."""
        c = Cinta("ab")
        c.mover_izquierda()  # pos -1
        # La cadena sigue intacta.
        contenido = c.obtener_contenido()
        self.assertEqual(contenido[0], "a")
        self.assertEqual(contenido[1], "b")
        pass

    def test_mover_izquierda_crea_celda_B(self):
        c = Cinta("a")
        c.mover_izquierda()
        self.assertEqual(c.leer(), "B")

    def test_mover_con_L(self):
        c = Cinta("ab")
        c.mover("L")
        self.assertEqual(c.posicion, -1)

    def test_mover_direccion_invalida(self):
        c = Cinta("a")
        with self.assertRaises(ValueError):
            c.mover("U")


#  Expansiones repetidas                                              
class TestCintaExpansionesRepetidas(unittest.TestCase):
    """Verifica que la cinta se extienda correctamente en ambas direcciones."""

    def test_expansion_derecha_repetida(self):
        c = Cinta("a")
        for _ in range(5):
            c.mover_derecha()
        self.assertEqual(c.posicion, 5)
        self.assertEqual(c.leer(), "B")
        # Todas las posiciones 1..5 deben ser B.
        pass

    def test_expansion_izquierda_repetida(self):
        c = Cinta("a")
        for _ in range(5):
            c.mover_izquierda()
        self.assertEqual(c.posicion, -5)
        self.assertEqual(c.leer(), "B")
        pass

    def test_expansion_ambas_direcciones(self):
        c = Cinta("ab")
        c.mover_izquierda()   # -1
        c.mover_izquierda()   # -2
        c.escribir("X")
        # Volver al centro y seguir a la derecha.
        for _ in range(5):
            c.mover_derecha()  # -1, 0, 1, 2 (B), 3
        c.escribir("Y")
        contenido = c.obtener_contenido()
        self.assertEqual(contenido[-2], "X")
        self.assertEqual(contenido[0], "a")
        self.assertEqual(contenido[1], "b")
        self.assertEqual(contenido[3], "Y")

    def test_ida_y_vuelta(self):
        """Moverse derecha e izquierda repetidamente no debe perder datos."""
        c = Cinta("abc")
        for _ in range(10):
            c.mover_derecha()
        for _ in range(10):
            c.mover_izquierda()
        self.assertEqual(c.posicion, 0)
        self.assertEqual(c.leer(), "a")
        # La cadena original sigue intacta.
        contenido = c.obtener_contenido()
        self.assertEqual(contenido[0], "a")
        self.assertEqual(contenido[1], "b")
        self.assertEqual(contenido[2], "c")


#  Escritura durante movimiento                    
class TestCintaSimulacionReal(unittest.TestCase):
    """Simula una secuencia real de operaciones de la maquina."""

    def test_secuencia_escribir_mover(self):
        """Escribe, mueve, escribe, mueve — como haria el motor."""
        c = Cinta("aba")
        # Paso 1: leer 'a', escribir 'X', mover R.
        self.assertEqual(c.leer(), "a")
        c.escribir("X")
        c.mover_derecha()
        # Paso 2: leer 'b', escribir 'Y', mover R.
        self.assertEqual(c.leer(), "b")
        c.escribir("Y")
        c.mover_derecha()
        # Paso 3: leer 'a', escribir 'Z', mover L.
        self.assertEqual(c.leer(), "a")
        c.escribir("Z")
        c.mover_izquierda()
        # Verificar que todo se conservo.
        self.assertEqual(c.posicion, 1)
        self.assertEqual(c.leer(), "Y")
        contenido = c.obtener_contenido()
        self.assertEqual(contenido[0], "X")
        self.assertEqual(contenido[1], "Y")
        self.assertEqual(contenido[2], "Z")

    def test_primera_b_cambiada_a_a(self):
        """Reproduce la maquina de ejemplo: cambia primera 'b' por 'a'."""
        c = Cinta("ababb")
        # q0, a -> q0, a, R (no cambia nada)
        c.escribir("a")
        c.mover_derecha()
        # q0, b -> q1, a, R (cambia 'b' por 'a')
        self.assertEqual(c.leer(), "b")
        c.escribir("a")
        c.mover_derecha()
        # q1, a -> q1, a, R
        c.escribir("a")
        c.mover_derecha()
        # q1, b -> q1, b, R
        c.escribir("b")
        c.mover_derecha()
        # q1, b -> q1, b, R
        c.escribir("b")
        c.mover_derecha()
        # q1, B -> qf, B, L
        self.assertEqual(c.leer(), "B")
        c.escribir("B")
        c.mover_izquierda()
        # Resultado: "aaabb" con cabezal en posicion 4.
        self.assertEqual(c.posicion, 4)
        self.assertEqual(
            c.contenido_como_lista(), ["a", "a", "a", "b", "b", "B"]
        )


#  Vista y obtener_contenido    
class TestCintaVista(unittest.TestCase):
    """Verifica las vistas de la cinta."""

    def test_obtener_contenido_es_copia(self):
        """Modificar el dict devuelto no debe afectar la cinta."""
        c = Cinta("ab")
        contenido = c.obtener_contenido()
        contenido[0] = "X"
        contenido[99] = "Z"
        # La cinta no se modifico.
        self.assertEqual(c.leer(), "a")
        self.assertNotIn(99, c.obtener_contenido())

    def test_contenido_como_lista_orden(self):
        c = Cinta("ab")
        c.mover_izquierda()
        c.escribir("X")
        # Posiciones: -1: X, 0: a, 1: b, 2: B
        self.assertEqual(c.contenido_como_lista(), ["X", "a", "b"])

    def test_str_marca_cabezal(self):
        c = Cinta("ab")
        texto = str(c)
        self.assertIn("[a]", texto)

    def test_str_cabezal_en_medio(self):
        c = Cinta("ab")
        c.mover_derecha()
        texto = str(c)
        self.assertIn("[b]", texto)


if __name__ == "__main__":
    unittest.main()