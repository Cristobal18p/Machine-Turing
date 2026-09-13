"""Modulo de lectura del archivo de transiciones.

Lee un archivo de texto con transiciones y produce:
  - Un diccionario indexado por (estado, simbolo_leido) -> Transicion.
  - La lista ordenada de estados descubiertos.
  - La lista ordenada de simbolos descubiertos.

Formato esperado de cada linea:
  estado_actual, simbolo_leido -> estado_siguiente, simbolo_escrito, movimiento

Se permiten:
  - Lineas vacias.
  - Comentarios con '#' (linea completa o al final de una transicion).
  - Espacios opcionales alrededor de las comas y la flecha.

El parser no ejecuta la maquina ni muestra ventanas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from logica.errores import ErrorArchivo, ErrorParser
from logica.transicion import Transicion


@dataclass
class ResultadoParser:
    """Resultado del analisis de un archivo de transiciones.

    Attributes:
        transiciones: Diccionario {(estado, simbolo): Transicion}.
        estados: Lista ordenada de estados (q0 primero, qf ultimo).
        simbolos: Lista ordenada de simbolos (B ultimo).
    """

    transiciones: dict[tuple[str, str], Transicion] = field(default_factory=dict)
    estados: list[str] = field(default_factory=list)
    simbolos: list[str] = field(default_factory=list)


def parsear_archivo(ruta: str | Path) -> ResultadoParser:
    """Lee un archivo de transiciones y lo convierte en objetos Transicion.

    Args:
        ruta: Ruta al archivo de texto con las transiciones.

    Returns:
        ResultadoParser con las transiciones, estados y simbolos descubiertos.

    Raises:
        ErrorArchivo: Si el archivo no existe o no puede leerse.
        ErrorParser: Si alguna linea contiene un error de sintaxis.
    """
    ruta = Path(ruta)

    if not ruta.exists():
        raise ErrorArchivo(f"El archivo no existe: {ruta}")

    try:
        contenido = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ErrorArchivo(f"No se puede leer el archivo: {ruta} ({e})")

    lineas = contenido.splitlines()

    transiciones: dict[tuple[str, str], Transicion] = {}
    estados_vistos: dict[str, None] = {}  # dict como set ordenado
    simbolos_vistos: dict[str, None] = {}

    for num_linea, linea_cruda in enumerate(lineas, start=1):
        # Eliminar comentarios en linea.
        linea = linea_cruda.split("#")[0].strip()

        # Saltar lineas vacias.
        if not linea:
            continue

        transicion = _parsear_linea(linea, linea_cruda.strip(), num_linea)

        # Verificar transiciones duplicadas.
        clave = (transicion.estado_origen, transicion.simbolo_leido)
        if clave in transiciones:
            raise ErrorParser(
                f"Transicion duplicada para "
                f"({transicion.estado_origen}, {transicion.simbolo_leido}).",
                linea=num_linea,
            )

        transiciones[clave] = transicion

        # Registrar estados en orden de aparicion.
        for estado in (transicion.estado_origen, transicion.estado_destino):
            if estado not in estados_vistos:
                estados_vistos[estado] = None

        # Registrar simbolos en orden de aparicion.
        for simbolo in (transicion.simbolo_leido, transicion.simbolo_escrito):
            if simbolo not in simbolos_vistos:
                simbolos_vistos[simbolo] = None

    estados = _ordenar_estados(list(estados_vistos.keys()))
    simbolos = _ordenar_simbolos(list(simbolos_vistos.keys()))

    return ResultadoParser(
        transiciones=transiciones,
        estados=estados,
        simbolos=simbolos,
    )


def _parsear_linea(linea: str, linea_cruda: str, num_linea: int) -> Transicion:
    """Analiza una linea y devuelve la Transicion correspondiente.

    Args:
        linea: Linea ya limpia (sin comentarios ni espacios extremos).
        linea_cruda: Linea original tal como aparece en el archivo.
        num_linea: Numero de linea (1-indexado) para mensajes de error.

    Returns:
        Objeto Transicion con los cinco campos validados.

    Raises:
        ErrorParser: Si la linea no cumple el formato esperado.
    """
    # Verificar que contenga '->'.
    if "->" not in linea:
        raise ErrorParser(
            f"Falta el separador '->' en la transicion: '{linea_cruda}'",
            linea=num_linea,
        )

    partes = linea.split("->")
    if len(partes) != 2:
        raise ErrorParser(
            f"La linea contiene mas de un '->': '{linea_cruda}'",
            linea=num_linea,
        )

    lado_izq = partes[0].strip()
    lado_der = partes[1].strip()

    # --- Lado izquierdo: estado_actual, simbolo_leido ---
    campos_izq = [c.strip() for c in lado_izq.split(",")]
    if len(campos_izq) != 2:
        raise ErrorParser(
            f"Se esperan 2 campos antes de '->': estado, simbolo. "
            f"Se encontraron {len(campos_izq)}: '{lado_izq}'",
            linea=num_linea,
        )

    estado_origen, simbolo_leido = campos_izq

    # --- Lado derecho: estado_siguiente, simbolo_escrito, movimiento ---
    campos_der = [c.strip() for c in lado_der.split(",")]
    if len(campos_der) != 3:
        raise ErrorParser(
            f"Se esperan 3 campos despues de '->': estado, simbolo, movimiento. "
            f"Se encontraron {len(campos_der)}: '{lado_der}'",
            linea=num_linea,
        )

    estado_destino, simbolo_escrito, movimiento = campos_der

    # --- Validar campos vacios ---
    campos = {
        "estado_origen": estado_origen,
        "simbolo_leido": simbolo_leido,
        "estado_destino": estado_destino,
        "simbolo_escrito": simbolo_escrito,
        "movimiento": movimiento,
    }
    for nombre, valor in campos.items():
        if not valor:
            raise ErrorParser(
                f"El campo '{nombre}' esta vacio.",
                linea=num_linea,
            )

    # --- Validar movimiento ---
    if movimiento not in ("L", "R"):
        raise ErrorParser(
            f"Movimiento invalido: '{movimiento}'. Solo se permite 'L' o 'R'.",
            linea=num_linea,
        )

    # --- Crear transicion ---
    try:
        return Transicion(
            estado_origen=estado_origen,
            simbolo_leido=simbolo_leido,
            estado_destino=estado_destino,
            simbolo_escrito=simbolo_escrito,
            movimiento=movimiento,
        )
    except Exception as e:
        raise ErrorParser(str(e), linea=num_linea)


def _ordenar_estados(estados: list[str]) -> list[str]:
    """Ordena estados: q0 primero, qf ultimo, el resto en orden de aparicion."""
    otros = [e for e in estados if e not in ("q0", "qf")]
    resultado = []
    if "q0" in estados:
        resultado.append("q0")
    resultado.extend(otros)
    if "qf" in estados:
        resultado.append("qf")
    return resultado


def _ordenar_simbolos(simbolos: list[str]) -> list[str]:
    """Ordena simbolos: B al final, el resto en orden de aparicion."""
    resultado = [s for s in simbolos if s != "B"]
    if "B" in simbolos:
        resultado.append("B")
    return resultado