"""Pruebas unitarias para el modulo parser.py"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logica.parser import parsear_archivo, ResultadoParser
from logica.transicion import Transicion
from logica.errores import ErrorArchivo, ErrorParser


def _crear_archivo(contenido: str) -> str:
    """Crea un archivo temporal con el contenido dado y devuelve su ruta."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    f.write(contenido)
    f.close()
    return f.name


class TestParserArchivoCorrecto(unittest.TestCase):
    """Verifica la lectura de un archivo valido de transiciones."""

    def test_archivo_basico(self):
        ruta = _crear_archivo(
            "q0, a -> q0, a, R\n"
            "q0, b -> q1, a, R\n"
            "q1, a -> q1, a, R\n"
            "q1, b -> q1, b, R\n"
            "q1, B -> qf, B, L\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(len(resultado.transiciones), 5)

        # Verificar una transicion concreta.
        t = resultado.transiciones[("q0", "b")]
        self.assertEqual(t.estado_origen, "q0")
        self.assertEqual(t.simbolo_leido, "b")
        self.assertEqual(t.estado_destino, "q1")
        self.assertEqual(t.simbolo_escrito, "a")
        self.assertEqual(t.movimiento, "R")

        os.unlink(ruta)

    def test_sin_espacios(self):
        ruta = _crear_archivo("q0,a->q1,b,R\n")
        resultado = parsear_archivo(ruta)

        t = resultado.transiciones[("q0", "a")]
        self.assertEqual(t.estado_destino, "q1")
        self.assertEqual(t.simbolo_escrito, "b")
        self.assertEqual(t.movimiento, "R")

        os.unlink(ruta)

    def test_espacios_variados(self):
        """Formas con y sin espacios deben producir el mismo resultado."""
        ruta1 = _crear_archivo("q0,a->q1,b,R\n")
        ruta2 = _crear_archivo("q0 , a  ->  q1 , b , R\n")

        r1 = parsear_archivo(ruta1)
        r2 = parsear_archivo(ruta2)

        self.assertEqual(
            r1.transiciones[("q0", "a")],
            r2.transiciones[("q0", "a")],
        )

        os.unlink(ruta1)
        os.unlink(ruta2)

    def test_estados_arbitrarios(self):
        ruta = _crear_archivo("inicio, X -> fin, Y, R\n")
        resultado = parsear_archivo(ruta)

        self.assertIn(("inicio", "X"), resultado.transiciones)
        t = resultado.transiciones[("inicio", "X")]
        self.assertEqual(t.estado_destino, "fin")

        os.unlink(ruta)

    def test_simbolos_numericos(self):
        ruta = _crear_archivo(
            "q0, 1 -> q1, 0, R\n"
            "q0, 0 -> q0, 0, R\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(len(resultado.transiciones), 2)
        self.assertIn(("q0", "1"), resultado.transiciones)
        self.assertIn(("q0", "0"), resultado.transiciones)

        os.unlink(ruta)


class TestParserComentariosYVacias(unittest.TestCase):
    """Verifica que se permitan comentarios con '#' y lineas vacias."""

    def test_comentario_linea_completa(self):
        ruta = _crear_archivo(
            "# Esta es una maquina de ejemplo\n"
            "q0, a -> q0, a, R\n"
            "# Transicion de aceptacion\n"
            "q0, B -> qf, B, L\n"
        )
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 2)

        os.unlink(ruta)

    def test_comentario_al_final_de_linea(self):
        ruta = _crear_archivo(
            "q0, a -> q0, a, R  # Avanza sobre a\n"
            "q0, b -> qf, b, R  # Acepta\n"
        )
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 2)
        self.assertIn(("q0", "a"), resultado.transiciones)
        self.assertIn(("q0", "b"), resultado.transiciones)

        os.unlink(ruta)

    def test_lineas_vacias_ignoradas(self):
        ruta = _crear_archivo(
            "\n"
            "q0, a -> q0, a, R\n"
            "\n"
            "\n"
            "q0, B -> qf, B, L\n"
            "\n"
        )
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 2)

        os.unlink(ruta)

    def test_archivo_solo_comentarios_y_vacias(self):
        ruta = _crear_archivo(
            "# Solo comentarios\n"
            "\n"
            "# Nada mas\n"
        )
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 0)
        self.assertEqual(resultado.estados, [])
        self.assertEqual(resultado.simbolos, [])

        os.unlink(ruta)


class TestParserEstadosYSimbolos(unittest.TestCase):
    """Verifica el descubrimiento y ordenamiento de estados y simbolos."""

    def test_orden_estados_q0_primero_qf_ultimo(self):
        ruta = _crear_archivo(
            "q1, a -> q2, a, R\n"
            "q0, a -> q1, a, R\n"
            "q2, B -> qf, B, L\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(resultado.estados[0], "q0")
        self.assertEqual(resultado.estados[-1], "qf")
        # q1 y q2 en el medio, en orden de aparicion.
        self.assertIn("q1", resultado.estados)
        self.assertIn("q2", resultado.estados)

        os.unlink(ruta)

    def test_orden_simbolos_B_ultimo(self):
        ruta = _crear_archivo(
            "q0, B -> q1, a, R\n"
            "q0, a -> q0, b, R\n"
            "q1, b -> qf, B, L\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(resultado.simbolos[-1], "B")
        # Los demas en orden de aparicion.
        self.assertIn("a", resultado.simbolos)
        self.assertIn("b", resultado.simbolos)

        os.unlink(ruta)

    def test_estados_sin_q0(self):
        """Si no aparece q0, no debe forzarse."""
        ruta = _crear_archivo("inicio, x -> fin, y, R\n")
        resultado = parsear_archivo(ruta)
        self.assertEqual(resultado.estados, ["inicio", "fin"])

        os.unlink(ruta)

    def test_simbolos_sin_B(self):
        """Si no aparece B, no debe forzarse."""
        ruta = _crear_archivo("q0, a -> q1, b, R\n")
        resultado = parsear_archivo(ruta)
        self.assertEqual(resultado.simbolos, ["a", "b"])

        os.unlink(ruta)


# ------------------------------------------------------------------ #
#  Validaciones de error                                              #
# ------------------------------------------------------------------ #


class TestParserArchivoInexistente(unittest.TestCase):
    """Verifica el error al intentar leer un archivo que no existe."""

    def test_archivo_inexistente(self):
        with self.assertRaises(ErrorArchivo) as ctx:
            parsear_archivo("/ruta/que/no/existe/transiciones.txt")
        self.assertIn("no existe", str(ctx.exception))


class TestParserArchivoVacio(unittest.TestCase):
    """Verifica el comportamiento con un archivo completamente vacio."""

    def test_archivo_vacio(self):
        ruta = _crear_archivo("")
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 0)
        self.assertEqual(resultado.estados, [])
        self.assertEqual(resultado.simbolos, [])

        os.unlink(ruta)


class TestParserFaltaFlecha(unittest.TestCase):
    """Verifica el error cuando falta '->' en una linea."""

    def test_linea_sin_flecha(self):
        ruta = _crear_archivo(
            "q0, a -> q0, a, R\n"
            "q0, b, q1, a, R\n"
        )
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 2)
        self.assertIn("->", str(ctx.exception))

        os.unlink(ruta)

    def test_multiples_flechas(self):
        ruta = _crear_archivo("q0, a -> q1 -> b, R\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)

        os.unlink(ruta)


class TestParserCamposIncompletos(unittest.TestCase):
    """Verifica errores cuando faltan campos."""

    def test_falta_campo_izquierdo(self):
        ruta = _crear_archivo("q0 -> q1, b, R\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)
        self.assertIn("2 campos", str(ctx.exception))

        os.unlink(ruta)

    def test_sobran_campos_izquierdo(self):
        ruta = _crear_archivo("q0, a, x -> q1, b, R\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)

        os.unlink(ruta)

    def test_falta_campo_derecho(self):
        ruta = _crear_archivo("q0, a -> q1, b\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)
        self.assertIn("3 campos", str(ctx.exception))

        os.unlink(ruta)

    def test_sobran_campos_derecho(self):
        ruta = _crear_archivo("q0, a -> q1, b, R, extra\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)

        os.unlink(ruta)

    def test_campo_vacio_estado_origen(self):
        ruta = _crear_archivo(", a -> q1, b, R\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)
        self.assertIn("vacio", str(ctx.exception).lower())

        os.unlink(ruta)

    def test_campo_vacio_simbolo_leido(self):
        ruta = _crear_archivo("q0,  -> q1, b, R\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)

        os.unlink(ruta)


class TestParserMovimientoInvalido(unittest.TestCase):
    """Verifica el error cuando el movimiento no es L ni R."""

    def test_movimiento_U(self):
        ruta = _crear_archivo("q0, a -> q1, b, U\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)
        self.assertIn("invalido", str(ctx.exception).lower())

        os.unlink(ruta)

    def test_movimiento_minuscula(self):
        ruta = _crear_archivo("q0, a -> q1, b, r\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 1)

        os.unlink(ruta)


class TestParserTransicionDuplicada(unittest.TestCase):
    """Verifica el error con transiciones duplicadas."""

    def test_duplicada_exacta(self):
        ruta = _crear_archivo(
            "q0, a -> q1, b, R\n"
            "q0, a -> q2, c, L\n"
        )
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 2)
        self.assertIn("duplicada", str(ctx.exception).lower())

        os.unlink(ruta)

    def test_no_duplicada_diferente_simbolo(self):
        """Mismo estado pero diferente simbolo: NO es duplicado."""
        ruta = _crear_archivo(
            "q0, a -> q1, b, R\n"
            "q0, b -> q2, c, L\n"
        )
        resultado = parsear_archivo(ruta)
        self.assertEqual(len(resultado.transiciones), 2)

        os.unlink(ruta)


class TestParserNumeroDeLinea(unittest.TestCase):
    """Verifica que los errores indiquen la linea correcta."""

    def test_error_en_linea_3_con_comentarios(self):
        ruta = _crear_archivo(
            "# Comentario\n"
            "q0, a -> q0, a, R\n"
            "q0, b, q1, a, R\n"
        )
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 3)

        os.unlink(ruta)

    def test_error_en_linea_4_con_vacias(self):
        ruta = _crear_archivo(
            "\n"
            "q0, a -> q0, a, R\n"
            "\n"
            "malo\n"
        )
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertEqual(ctx.exception.linea, 4)

        os.unlink(ruta)

    def test_mensaje_incluye_numero(self):
        ruta = _crear_archivo("malo\n")
        with self.assertRaises(ErrorParser) as ctx:
            parsear_archivo(ruta)
        self.assertIn("Linea 1", str(ctx.exception))

        os.unlink(ruta)


class TestParserIntegracion(unittest.TestCase):
    """Prueba el parser con el archivo de ejemplo completo de la especificacion."""

    def test_ejemplo_especificacion(self):
        ruta = _crear_archivo(
            "# Avanza sobre el simbolo a\n"
            "q0, a -> q0, a, R\n"
            "\n"
            "q0, b -> qf, b, R  # Acepta despues de leer b\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(len(resultado.transiciones), 2)
        self.assertEqual(resultado.estados, ["q0", "qf"])
        self.assertEqual(resultado.simbolos, ["a", "b"])

        t1 = resultado.transiciones[("q0", "a")]
        self.assertEqual(str(t1), "q0, a -> q0, a, R")

        t2 = resultado.transiciones[("q0", "b")]
        self.assertEqual(str(t2), "q0, b -> qf, b, R")

        os.unlink(ruta)

    def test_maquina_completa_5_transiciones(self):
        ruta = _crear_archivo(
            "q0, a -> q0, a, R\n"
            "q0, b -> q1, a, R\n"
            "q1, a -> q1, a, R\n"
            "q1, b -> q1, b, R\n"
            "q1, B -> qf, B, L\n"
        )
        resultado = parsear_archivo(ruta)

        self.assertEqual(len(resultado.transiciones), 5)
        self.assertEqual(resultado.estados, ["q0", "q1", "qf"])
        self.assertEqual(resultado.simbolos, ["a", "b", "B"])

        # La clave (q1, B) debe mapear a la transicion de aceptacion.
        t = resultado.transiciones[("q1", "B")]
        self.assertEqual(t.estado_destino, "qf")
        self.assertEqual(t.movimiento, "L")

        os.unlink(ruta)


if __name__ == "__main__":
    unittest.main()