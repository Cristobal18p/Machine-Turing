"""Pruebas unitarias para el modulo maquina_turing.py"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.maquina_turing import MaquinaTuring
from logica.transicion import Transicion


def _crear_transiciones_basicas() -> dict[tuple[str, str], Transicion]:
    """Crea un diccionario de transiciones de prueba.
    
    Maquina que avanza sobre 'a', al encontrar 'b' la cambia a 'a'
    y termina aceptando cuando llega al blanco 'B'.
    """
    t1 = Transicion("q0", "a", "q0", "a", "R")
    t2 = Transicion("q0", "b", "q1", "a", "R")
    t3 = Transicion("q1", "a", "q1", "a", "R")
    t4 = Transicion("q1", "b", "q1", "b", "R")
    t5 = Transicion("q1", "B", "qf", "B", "L")
    
    return {
        ("q0", "a"): t1,
        ("q0", "b"): t2,
        ("q1", "a"): t3,
        ("q1", "b"): t4,
        ("q1", "B"): t5,
    }


class TestMaquinaTuringIniciacion(unittest.TestCase):
    """Verifica el estado inicial de la maquina y el Paso 0."""

    def test_estado_inicial_sin_iniciar(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        self.assertEqual(motor.estado_ejecucion, "NO_INICIADA")
        self.assertIsNone(motor.cinta)
        self.assertEqual(len(motor.historial), 0)

    def test_iniciar_crea_paso_0(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("ab")
        
        self.assertEqual(motor.estado_ejecucion, "EN_CURSO")
        self.assertEqual(motor.paso_actual, 0)
        self.assertEqual(motor.estado_actual, "q0")
        
        # Debe haber guardado exactamente una configuracion (Paso 0)
        self.assertEqual(len(motor.historial), 1)
        cfg0 = motor.historial[0]
        
        self.assertEqual(cfg0.paso, 0)
        self.assertEqual(cfg0.estado, "q0")
        self.assertEqual(cfg0.simbolo_leido, "a")
        self.assertIsNone(cfg0.transicion_aplicada)
        
        # q0, a -> q0, a, R
        self.assertIsNotNone(cfg0.transicion_pendiente)
        self.assertEqual(cfg0.transicion_pendiente.movimiento, "R")
        self.assertIsNone(cfg0.motivo_detencion)

    def test_iniciar_directamente_aceptado_si_empieza_en_qf(self):
        """Si por alguna razon el estado inicial es qf, debe aceptar de inmediato."""
        t_dummy = Transicion("qf", "a", "qf", "a", "R")
        motor = MaquinaTuring({("qf", "a"): t_dummy})
        # Truco para forzar qf al iniciar (en vez de q0)
        motor.ESTADO_INICIAL = "qf"
        motor.iniciar("a")
        
        self.assertEqual(motor.estado_ejecucion, "ACEPTADA")
        self.assertEqual(motor.historial[0].motivo_detencion, motor.RESULTADO_ACEPTADA)


class TestMaquinaTuringPasoAPaso(unittest.TestCase):
    """Verifica la ejecucion paso a paso del motor."""

    def test_un_paso(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("b")  # En q0 con 'b' -> pasa a q1 con 'a', R
        
        continuar = motor.paso()
        self.assertTrue(continuar)
        self.assertEqual(motor.paso_actual, 1)
        self.assertEqual(motor.estado_actual, "q1")
        self.assertEqual(len(motor.historial), 2)
        
        cfg1 = motor.historial[1]
        self.assertEqual(cfg1.estado, "q1")
        # El cabezal se movio a R (posicion 1), donde hay un Blanco (B)
        self.assertEqual(cfg1.simbolo_leido, "B")
        # Cinta original "b", cambio a "a". En pos 1 leemos "B"
        self.assertEqual(cfg1.cinta_como_lista(), ["a", "B"])

    def test_llegar_a_aceptacion(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("b")  # paso 0
        motor.paso()        # paso 1: lee 'b', va a q1, B
        
        # En q1 con 'B' -> pasa a qf, B, L
        continuar = motor.paso()
        self.assertFalse(continuar)  # No puede continuar porque llego a qf
        self.assertEqual(motor.estado_ejecucion, "ACEPTADA")
        
        # Verificamos la configuracion final
        cfg_final = motor.historial[-1]
        self.assertEqual(cfg_final.estado, "qf")
        self.assertEqual(cfg_final.motivo_detencion, motor.RESULTADO_ACEPTADA)
        self.assertIsNone(cfg_final.transicion_pendiente)
        self.assertIsNotNone(cfg_final.transicion_aplicada)

    def test_rechazo_por_falta_de_transicion(self):
        """Si se encuentra una combinacion sin transicion, se rechaza."""
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("x")  # q0 leyendo 'x' -> No existe transicion
        
        self.assertEqual(motor.estado_ejecucion, "RECHAZADA")
        cfg0 = motor.historial[0]
        self.assertIsNone(cfg0.transicion_pendiente)
        self.assertIn("No existe transicion", cfg0.motivo_detencion)


class TestMaquinaTuringEjecutarTodo(unittest.TestCase):
    """Verifica la ejecucion completa sin paradas manuales."""

    def test_ejecutar_todo_hasta_aceptar(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        # "ab" tomara 3 pasos:
        # P0: q0, a
        # P1: q0, b
        # P2: q1, B
        # P3: qf, B (Termina)
        motor.iniciar("ab")
        motor.ejecutar_todo()
        
        self.assertEqual(motor.estado_ejecucion, "ACEPTADA")
        self.assertEqual(motor.paso_actual, 3)
        self.assertEqual(len(motor.historial), 4)  # Pasos 0, 1, 2, 3


class TestMaquinaTuringDetencion(unittest.TestCase):
    """Verifica que el usuario pueda interrumpir la ejecucion."""

    def test_detener_manualmente(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("ab")
        
        motor.detener()
        self.assertEqual(motor.estado_ejecucion, "DETENIDA")
        
        # Intentar dar un paso no deberia hacer nada
        continuar = motor.paso()
        self.assertFalse(continuar)
        self.assertEqual(motor.paso_actual, 0)
        
        # La ultima configuracion debe reflejar la detencion
        cfg = motor.historial[-1]
        self.assertEqual(cfg.motivo_detencion, motor.RESULTADO_DETENIDA)
        self.assertIsNone(cfg.transicion_pendiente)

    def test_detener_cuando_ya_termino(self):
        """Si ya termino, detener() no deberia alterar el resultado."""
        motor = MaquinaTuring(_crear_transiciones_basicas())
        motor.iniciar("x")  # RECHAZADA en paso 0
        
        motor.detener()
        
        # Debe mantenerse RECHAZADA, no DETENIDA
        self.assertEqual(motor.estado_ejecucion, "RECHAZADA")


class TestMaquinaTuringReiniciar(unittest.TestCase):
    """Verifica que la misma instancia pueda ejecutar cadenas distintas."""

    def test_reiniciar_misma_maquina(self):
        motor = MaquinaTuring(_crear_transiciones_basicas())
        
        # Primera ejecucion
        motor.iniciar("x")
        self.assertEqual(motor.estado_ejecucion, "RECHAZADA")
        
        # Segunda ejecucion con cadena valida
        motor.iniciar("ab")
        motor.ejecutar_todo()
        
        self.assertEqual(motor.estado_ejecucion, "ACEPTADA")
        self.assertEqual(motor.paso_actual, 3)
        # El historial de la segunda cadena no se mezcla con la primera
        self.assertEqual(len(motor.historial), 4)


if __name__ == "__main__":
    unittest.main()