"""Motor de ejecucion de la Maquina de Turing.

Controla el ciclo de ejecucion y produce el historial de
descripciones instantaneas (configuraciones).

Resultados posibles:
  - EN_CURSO: La maquina esta ejecutandose.
  - ACEPTADA: La maquina llego al estado 'qf'.
  - RECHAZADA: No existe una transicion aplicable.
  - DETENIDA: El usuario interrumpio la ejecucion manualmente.
"""

from __future__ import annotations

from logica.cinta import Cinta
from logica.configuracion import Configuracion
from logica.transicion import Transicion


class MaquinaTuring:
    """Simulador del motor de una Maquina de Turing."""

    ESTADO_INICIAL = "q0"
    ESTADO_FINAL = "qf"

    RESULTADO_ACEPTADA = "CADENA ACEPTADA"
    RESULTADO_RECHAZADA = "CADENA RECHAZADA"
    RESULTADO_DETENIDA = "EJECUCION DETENIDA POR EL USUARIO"

    def __init__(self, transiciones: dict[tuple[str, str], Transicion]) -> None:
        """Inicializa el motor con un conjunto de transiciones.

        Args:
            transiciones: Diccionario indexado por (estado, simbolo_leido).
        """
        self.transiciones = transiciones
        self.cinta: Cinta | None = None
        self.estado_actual: str = ""
        self.paso_actual: int = 0
        self.estado_ejecucion: str = "NO_INICIADA"
        self.ultima_transicion: Transicion | None = None
        self.historial: list[Configuracion] = []

    def iniciar(self, cadena: str) -> None:
        """Inicializa la maquina para validar una nueva cadena.

        Coloca el cabezal en 0, el estado en 'q0' y guarda el Paso 0.

        Args:
            cadena: La cadena de entrada que se procesara.
        """
        self.cinta = Cinta(cadena)
        self.estado_actual = self.ESTADO_INICIAL
        self.paso_actual = 0
        self.estado_ejecucion = "EN_CURSO"
        self.ultima_transicion = None
        self.historial = []

        # Guardar la configuracion inicial (Paso 0)
        self._registrar_configuracion()

    def paso(self) -> bool:
        """Ejecuta una sola transicion.

        Returns:
            True si la maquina sigue en curso despues del paso.
            False si se detuvo (aceptada, rechazada o detenida manualmente).
        """
        if self.estado_ejecucion != "EN_CURSO" or self.cinta is None:
            return False

        simbolo = self.cinta.leer()
        transicion = self.transiciones.get((self.estado_actual, simbolo))

        # Defensa por si acaso (el chequeo real se hizo en el registro anterior)
        if not transicion:
            self.estado_ejecucion = "RECHAZADA"
            return False

        # 1. Escribir el nuevo simbolo
        self.cinta.escribir(transicion.simbolo_escrito)
        # 2. Mover el cabezal
        self.cinta.mover(transicion.movimiento)
        # 3. Cambiar al estado siguiente
        self.estado_actual = transicion.estado_destino
        # 4. Actualizar contadores
        self.paso_actual += 1
        self.ultima_transicion = transicion

        # 5. Guardar la nueva configuracion
        self._registrar_configuracion()

        return self.estado_ejecucion == "EN_CURSO"

    def ejecutar_todo(self) -> None:
        """Ejecuta pasos consecutivamente hasta que la maquina se detenga."""
        while self.estado_ejecucion == "EN_CURSO":
            self.paso()

    def detener(self) -> None:
        """Detiene manualmente una ejecucion en curso."""
        if self.estado_ejecucion == "EN_CURSO":
            self.estado_ejecucion = "DETENIDA"
            # Si hay historial, actualizamos la ultima fotografia para
            # reflejar que fue detenida.
            if self.historial:
                ultima = self.historial.pop()
                cfg_detenida = Configuracion(
                    paso=ultima.paso,
                    estado=ultima.estado,
                    posicion_cabezal=ultima.posicion_cabezal,
                    cinta=ultima.cinta,
                    simbolo_leido=ultima.simbolo_leido,
                    transicion_aplicada=ultima.transicion_aplicada,
                    transicion_pendiente=None,
                    motivo_detencion=self.RESULTADO_DETENIDA,
                )
                self.historial.append(cfg_detenida)

    def _registrar_configuracion(self) -> None:
        """Evalua el estado actual y guarda una fotografia en el historial."""
        if self.cinta is None:
            return

        simbolo = self.cinta.leer()
        pendiente = self.transiciones.get((self.estado_actual, simbolo))
        motivo = None

        if self.estado_ejecucion == "DETENIDA":
            motivo = self.RESULTADO_DETENIDA
            pendiente = None
        elif self.estado_actual == self.ESTADO_FINAL:
            self.estado_ejecucion = "ACEPTADA"
            motivo = self.RESULTADO_ACEPTADA
            pendiente = None
        elif not pendiente:
            self.estado_ejecucion = "RECHAZADA"
            motivo = f"No existe transicion para el estado {self.estado_actual} y el simbolo {simbolo}."

        cfg = Configuracion(
            paso=self.paso_actual,
            estado=self.estado_actual,
            posicion_cabezal=self.cinta.posicion,
            cinta=self.cinta.obtener_contenido(),
            simbolo_leido=simbolo,
            transicion_aplicada=self.ultima_transicion,
            transicion_pendiente=pendiente,
            motivo_detencion=motivo,
        )
        self.historial.append(cfg)