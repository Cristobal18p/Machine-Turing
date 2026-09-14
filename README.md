# Simulador de Máquina de Turing

## Descripción del Simulador
Este proyecto es una herramienta gráfica e interactiva desarrollada para visualizar y procesar transiciones y descripciones instantáneas de Máquinas de Turing. Permite a los usuarios cargar reglas mediante archivos de texto, introducir una cadena de entrada, y observar el comportamiento de la cinta, la tabla de transiciones y el historial de ejecución en tiempo real (ya sea de forma automática o paso a paso).

## Requisitos de Ejecución
Para ejecutar el simulador desde su código fuente, es necesario contar con lo siguiente en su sistema:
1. **Python:** Versión 3.10 o superior instalado en el equipo.
2. **Tkinter:** Librería gráfica nativa (generalmente viene preinstalada con Python en Windows/macOS; en distribuciones Linux puede requerir instalar el paquete `python3-tk`).
3. **Graphviz (Muy Importante):** Necesario para que el panel del diagrama de estados funcione.
   - **En Windows:** Descargue el instalador desde su página oficial: [https://graphviz.org/download/](https://graphviz.org/download/). *Nota:* Durante la instalación, asegúrese de marcar la casilla **"Add Graphviz to system PATH"**, ya que el instalador de Windows no lo hace por defecto.
   - **En Linux / macOS:** Instálelo directamente desde su terminal (ej. `sudo apt install graphviz` para Ubuntu/Debian, o `brew install graphviz` en Mac). En estos sistemas, el PATH se configura de forma automática.

**Comando para iniciar el programa (desde la raíz del proyecto):**
```bash
python main.py
```

## Cómo Cargar una Máquina de Turing (Transiciones)
Para ejecutar una máquina, debe crear y cargar un archivo de texto plano (`.txt`) que contenga las reglas de transición. 

**Formato estricto requerido por cada línea:**
```text
estado_actual, simbolo_leido -> estado_siguiente, simbolo_escrito, movimiento
```

**Reglas de diseño obligatorias:**
* **Estados de inicio y fin:** La máquina siempre debe iniciar en el estado `q0` y finalizar en el estado de aceptación `qf`. Si el archivo no incluye estos estados, el simulador rechazará la carga del archivo.
* **Movimientos permitidos:** Solo se permite usar `R` (movimiento hacia la Derecha) o `L` (movimiento hacia la Izquierda).
* **Símbolo Blanco:** El espacio en vacío de la cinta se representa estrictamente con la letra mayúscula `B`.
* **Comentarios:** Puede usar el símbolo `#` para agregar anotaciones en su archivo; el programa ignorará todo texto que esté después de este símbolo.

**Ejemplo válido de archivo (.txt):**
```text
# Ejemplo: Cambiar todos los 1 por 0 y terminar al leer un blanco
q0, 1 -> q1, 0, R
q1, 1 -> q1, 0, R
q1, B -> qf, B, R
```

---

## Referencia de Desarrollo
**Universidad de Panamá - Facultad de Informática, Electrónica y Comunicación**  
**Desarrollado por:** Cristobal Prados, Carlos Gonzalez  
**Año:** 2026
