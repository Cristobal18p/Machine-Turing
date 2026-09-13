"""Pruebas unitarias para el modulo configuracion.py"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.configuracion import Configuracion
from logica.transicion import Transicion


class TestConfiguracionCreacion(unittest.TestCase):
    """Verifica que la configuracion conserve todos sus datos."""

    def test_crear_configuracion_inicial_paso_0(self):
        """Paso 0: solo transicion pendiente, sin aplicada."""
        cinta = {0: "a", 1: "b", 2: "a", 3: "B"}
        t_pendiente = Transicion("q0", "a", "q0", "a", "R")
        cfg = Configuracion(
            paso=0,
            estado="q0",
            posicion_cabezal=0,
            cinta=cinta,
            simbolo_leido="a",
            transicion_aplicada=None,
            transicion_pendiente=t_pendiente,
        )
        self.assertEqual(cfg.paso, 0)
        self.assertEqual(cfg.estado, "q0")
        self.assertEqual(cfg.posicion_cabezal, 0)
        self.assertEqual(cfg.simbolo_leido, "a")
        self.assertIsNone(cfg.transicion_aplicada)
        self.assertEqual(cfg.transicion_pendiente, t_pendiente)
        self.assertIsNone(cfg.motivo_detencion)

    def test_crear_configuracion_paso_intermedio(self):
        """Paso N: tiene aplicada (como llego) y pendiente (que hara)."""
        cinta = {0: "a", 1: "b", 2: "B"}
        t_aplicada = Transicion("q0", "a", "q0", "a", "R")
        t_pendiente = Transicion("q0", "b", "q1", "a", "R")
        cfg = Configuracion(
            paso=1,
            estado="q0",
            posicion_cabezal=1,
            cinta=cinta,
            simbolo_leido="b",
            transicion_aplicada=t_aplicada,
            transicion_pendiente=t_pendiente,
        )
        self.assertEqual(cfg.transicion_aplicada, t_aplicada)
        self.assertEqual(cfg.transicion_pendiente, t_pendiente)

    def test_crear_configuracion_rechazada(self):
        """Configuracion final: aplicada presente, sin pendiente, con motivo."""
        cinta = {0: "a", 1: "B"}
        t_aplicada = Transicion("q0", "a", "q2", "a", "R")
        cfg = Configuracion(
            paso=3,
            estado="q2",
            posicion_cabezal=1,
            cinta=cinta,
            simbolo_leido="B",
            transicion_aplicada=t_aplicada,
            transicion_pendiente=None,
            motivo_detencion="RECHAZADA",
        )
        self.assertEqual(cfg.transicion_aplicada, t_aplicada)
        self.assertIsNone(cfg.transicion_pendiente)
        self.assertEqual(cfg.motivo_detencion, "RECHAZADA")

    def test_crear_configuracion_aceptada(self):
        """Configuracion final aceptada: llego a qf."""
        cinta = {0: "a", 1: "a", 2: "B"}
        t_aplicada = Transicion("q1", "B", "qf", "B", "L")
        cfg = Configuracion(
            paso=5,
            estado="qf",
            posicion_cabezal=1,
            cinta=cinta,
            simbolo_leido="a",
            transicion_aplicada=t_aplicada,
            transicion_pendiente=None,
            motivo_detencion="ACEPTADA",
        )
        self.assertEqual(cfg.estado, "qf")
        self.assertEqual(cfg.motivo_detencion, "ACEPTADA")


# ------------------------------------------------------------------ #
#  Cinta inmutable (Decision tecnica 1)                               #
# ------------------------------------------------------------------ #


class TestConfiguracionCintaInmutable(unittest.TestCase):
    """Verifica que la cinta sea una copia inmutable (MappingProxyType)."""

    def test_cinta_es_copia_no_referencia(self):
        """Modificar el dict original NO debe afectar la configuracion."""
        cinta_original = {0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(0, "q0", 0, cinta_original, "a")

        # Modificar el dict original despues de crear la configuracion.
        cinta_original[0] = "X"
        cinta_original[99] = "Z"

        # La configuracion debe conservar los valores originales.
        self.assertEqual(cfg.cinta[0], "a")
        self.assertNotIn(99, cfg.cinta)

    def test_cinta_no_se_puede_modificar(self):
        """La cinta dentro de la configuracion debe ser de solo lectura."""
        cinta = {0: "a", 1: "B"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")

        with self.assertRaises(TypeError):
            cfg.cinta[0] = "X"

    def test_cinta_no_permite_agregar_claves(self):
        cinta = {0: "a"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")

        with self.assertRaises(TypeError):
            cfg.cinta[5] = "B"

    def test_cinta_no_permite_eliminar_claves(self):
        cinta = {0: "a", 1: "B"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")

        with self.assertRaises(TypeError):
            del cfg.cinta[0]

    def test_dos_configuraciones_independientes(self):
        """Dos configuraciones con la misma cinta deben ser independientes."""
        cinta_motor = {0: "a", 1: "b", 2: "B"}
        cfg1 = Configuracion(0, "q0", 0, dict(cinta_motor), "a")

        # El motor modifica la cinta y crea otra configuracion.
        cinta_motor[0] = "X"
        cfg2 = Configuracion(1, "q1", 1, dict(cinta_motor), "b")

        # cfg1 conserva 'a', cfg2 tiene 'X'.
        self.assertEqual(cfg1.cinta[0], "a")
        self.assertEqual(cfg2.cinta[0], "X")


# ------------------------------------------------------------------ #
#  Cinta como lista                                                   #
# ------------------------------------------------------------------ #


class TestConfiguracionCintaComoLista(unittest.TestCase):
    """Verifica la conversion de cinta dict a lista ordenada."""

    def test_cinta_simple(self):
        cinta = {0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")
        self.assertEqual(cfg.cinta_como_lista(), ["a", "b", "B"])

    def test_cinta_con_posiciones_negativas(self):
        cinta = {-1: "B", 0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(1, "q0", -1, cinta, "B")
        self.assertEqual(cfg.cinta_como_lista(), ["B", "a", "b", "B"])

    def test_cinta_vacia(self):
        cfg = Configuracion(0, "q0", 0, {}, "B")
        self.assertEqual(cfg.cinta_como_lista(), [])

    def test_cinta_con_hueco_rellena_B(self):
        cinta = {0: "a", 2: "b"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")
        self.assertEqual(cfg.cinta_como_lista(), ["a", "B", "b"])


# ------------------------------------------------------------------ #
#  Indice del cabezal                                                 #
# ------------------------------------------------------------------ #


class TestConfiguracionIndiceCabezal(unittest.TestCase):
    """Verifica el calculo del indice del cabezal en la lista."""

    def test_cabezal_al_inicio(self):
        cinta = {0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")
        self.assertEqual(cfg.indice_cabezal_en_lista(), 0)

    def test_cabezal_en_medio(self):
        cinta = {0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(1, "q0", 1, cinta, "b")
        self.assertEqual(cfg.indice_cabezal_en_lista(), 1)

    def test_cabezal_con_posicion_negativa(self):
        cinta = {-1: "B", 0: "a", 1: "b"}
        cfg = Configuracion(1, "q0", 0, cinta, "a")
        self.assertEqual(cfg.indice_cabezal_en_lista(), 1)

    def test_cabezal_en_posicion_negativa(self):
        cinta = {-2: "B", -1: "B", 0: "a"}
        cfg = Configuracion(1, "q0", -2, cinta, "B")
        self.assertEqual(cfg.indice_cabezal_en_lista(), 0)


# ------------------------------------------------------------------ #
#  Formato bloque (Decision tecnica 2: pendiente vs aplicada)         #
# ------------------------------------------------------------------ #


class TestConfiguracionFormatoBloque(unittest.TestCase):
    """Verifica la generacion de la descripcion instantanea."""

    def test_paso_0_solo_pendiente(self):
        """Paso 0 debe mostrar Transicion pendiente, NO aplicada."""
        cinta = {0: "a", 1: "b", 2: "a", 3: "b", 4: "b", 5: "B"}
        t = Transicion("q0", "a", "q0", "a", "R")
        cfg = Configuracion(0, "q0", 0, cinta, "a", transicion_pendiente=t)
        texto = cfg.formato_bloque()

        self.assertIn("Paso: 0", texto)
        self.assertIn("Estado: q0", texto)
        self.assertIn("Cinta: a  b  a  b  b  B", texto)
        self.assertIn("Simbolo leido: a", texto)
        self.assertIn("Transicion pendiente: q0, a -> q0, a, R", texto)
        self.assertNotIn("Transicion aplicada", texto)

    def test_paso_intermedio_ambas_transiciones(self):
        """Un paso intermedio debe mostrar aplicada Y pendiente."""
        cinta = {0: "a", 1: "b", 2: "B"}
        t_aplicada = Transicion("q0", "a", "q0", "a", "R")
        t_pendiente = Transicion("q0", "b", "q1", "a", "R")
        cfg = Configuracion(
            1, "q0", 1, cinta, "b",
            transicion_aplicada=t_aplicada,
            transicion_pendiente=t_pendiente,
        )
        texto = cfg.formato_bloque()

        self.assertIn("Transicion aplicada: q0, a -> q0, a, R", texto)
        self.assertIn("Transicion pendiente: q0, b -> q1, a, R", texto)
        # La aplicada debe aparecer ANTES de la pendiente.
        pos_aplicada = texto.index("Transicion aplicada")
        pos_pendiente = texto.index("Transicion pendiente")
        self.assertLess(pos_aplicada, pos_pendiente)

    def test_paso_final_rechazada(self):
        """Rechazo: muestra aplicada, sin pendiente, con resultado."""
        cinta = {0: "a", 1: "B"}
        t_aplicada = Transicion("q0", "a", "q2", "a", "R")
        cfg = Configuracion(
            2, "q2", 1, cinta, "B",
            transicion_aplicada=t_aplicada,
            motivo_detencion="RECHAZADA",
        )
        texto = cfg.formato_bloque()

        self.assertIn("Transicion aplicada:", texto)
        self.assertNotIn("Transicion pendiente", texto)
        self.assertIn("Resultado: RECHAZADA", texto)

    def test_paso_final_aceptada(self):
        """Aceptacion: llego a qf, muestra aplicada y resultado."""
        cinta = {0: "a", 1: "a", 2: "B"}
        t_aplicada = Transicion("q1", "B", "qf", "B", "L")
        cfg = Configuracion(
            5, "qf", 1, cinta, "a",
            transicion_aplicada=t_aplicada,
            motivo_detencion="ACEPTADA",
        )
        texto = cfg.formato_bloque()

        self.assertIn("Estado: qf", texto)
        self.assertIn("Transicion aplicada:", texto)
        self.assertIn("Resultado: ACEPTADA", texto)

    def test_formato_str_es_bloque(self):
        cinta = {0: "a", 1: "B"}
        cfg = Configuracion(0, "q0", 0, cinta, "a")
        self.assertEqual(str(cfg), cfg.formato_bloque())

    def test_cabezal_apunta_al_simbolo_correcto(self):
        cinta = {0: "a", 1: "b", 2: "B"}
        cfg = Configuracion(1, "q0", 1, cinta, "b")
        texto = cfg.formato_bloque()
        lineas = texto.split("\n")
        linea_cabezal = [l for l in lineas if "Cabezal:" in l][0]
        linea_cinta = [l for l in lineas if "Cinta:" in l][0]
        prefijo_cinta = "Cinta: "
        prefijo_cabezal = "Cabezal: "
        contenido_cinta = linea_cinta[len(prefijo_cinta):]
        contenido_cabezal = linea_cabezal[len(prefijo_cabezal):]
        pos_cursor = contenido_cabezal.index("^")
        self.assertEqual(contenido_cinta[pos_cursor], "b")


# ------------------------------------------------------------------ #
#  Inmutabilidad de la configuracion                                  #
# ------------------------------------------------------------------ #


class TestConfiguracionInmutabilidad(unittest.TestCase):
    """Verifica que la configuracion sea inmutable."""

    def test_no_modificar_paso(self):
        cfg = Configuracion(0, "q0", 0, {0: "a"}, "a")
        with self.assertRaises(AttributeError):
            cfg.paso = 1

    def test_no_modificar_estado(self):
        cfg = Configuracion(0, "q0", 0, {0: "a"}, "a")
        with self.assertRaises(AttributeError):
            cfg.estado = "q1"

    def test_no_modificar_cinta(self):
        cfg = Configuracion(0, "q0", 0, {0: "a"}, "a")
        with self.assertRaises(AttributeError):
            cfg.cinta = {0: "X"}


if __name__ == "__main__":
    unittest.main()