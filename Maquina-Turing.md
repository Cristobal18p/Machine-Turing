 # Simulador de Maquina de Turing

## 1. Objetivo del proyecto

Construir un simulador en Python para maquinas de Turing deterministas de una cinta. El usuario cargara un archivo que contiene las transiciones, introducira una cadena desde la interfaz y podra observar:

- La tabla de transiciones.
- El diagrama de transiciones.
- La ejecucion de la maquina.
- La descripcion instantanea paso a paso.
- La cadena resultante y el resultado de aceptacion o rechazo.

El simulador debe ser generico. No debe contener reglas especificas para una cadena, un alfabeto o una maquina concreta.

## 2. Convenciones del simulador

Estas convenciones son parte del contrato general:

- Estado inicial: `q0`.
- Estado final de aceptacion: `qf`.
- Simbolo blanco: `B`.
- Movimiento a la derecha: `R`.
- Movimiento a la izquierda: `L`.
- El cabezal inicia sobre el primer caracter de la cadena.
- La maquina escribe el simbolo y despues mueve el cabezal.
- Si llega a `qf`, la cadena es aceptada.
- Si no existe una transicion para el estado y simbolo actuales, la cadena es rechazada.
- No se impone un limite automatico de pasos. La ejecucion depende de las transiciones y puede no terminar si la maquina contiene un ciclo.
- La interfaz debe ofrecer una accion para detener una ejecucion que no finaliza.

## 3. Formato del archivo de transiciones

El archivo contiene unicamente transiciones. La cadena se introduce posteriormente desde la interfaz.

```text
q0, a -> q0, a, R
q0, b -> q1, a, R
q1, a -> q1, a, R
q1, b -> q1, b, R
q1, B -> qf, B, L
```

La estructura de cada linea es:

```text
estado_actual, simbolo_leido -> estado_siguiente, simbolo_escrito, movimiento
```

Los espacios son opcionales. Por ejemplo, estas formas deben significar lo mismo:

```text
q0,a->q1,b,R
q0, a -> q1, b, R
```

El archivo puede usar cualquier nombre de estado y cualquier simbolo, excepto que `q0`, `qf`, `B`, `L` y `R` tienen el significado indicado por las convenciones del simulador.

## 4. Arquitectura por modulos

```text
src/
|-- main.py
|-- logica/
|   |-- transicion.py
|   |-- parser.py
|   |-- cinta.py
|   |-- configuracion.py
|   |-- maquina_turing.py
|   `-- errores.py
|-- visualizacion/
|   |-- tabla_transiciones.py
|   `-- diagrama.py
`-- interfaz/
	`-- ventana_principal.py

test/
|-- test_parser.py
|-- test_cinta.py
|-- test_maquina_turing.py
`-- test_visualizacion.py
```

La estructura es una guia. Se pueden dividir o combinar archivos cuando exista una razon tecnica, pero las responsabilidades y dependencias descritas abajo deben mantenerse.

## 5. Modulo de dominio: `transicion.py`

### Responsabilidad

Representar una transicion individual de forma estructurada.

### Datos

- `estado_origen`
- `simbolo_leido`
- `estado_destino`
- `simbolo_escrito`
- `movimiento`

### Reglas

- El movimiento solo puede ser `L` o `R`.
- Los valores no deben modificarse durante la ejecucion.
- El modulo no debe conocer la interfaz, la cinta ni Graphviz.

### Salida esperada

Debe poder producir una etiqueta de diagrama con este formato:

```text
b, a, R
```

## 6. Modulo de lectura: `parser.py`

### Responsabilidad

Leer el archivo de transiciones y convertirlo en objetos `Transicion`.

### Entrada

- Ruta de un archivo de texto.

### Salida

Una estructura indexada por estado y simbolo leido:

```python
transiciones[("q0", "a")] = transicion
```

Tambien debe entregar los estados y simbolos descubiertos para alimentar la tabla y el diagrama.

### Validaciones

- Archivo inexistente o ilegible.
- Linea vacia o comentario, si se decide permitirlos.
- Falta de `->`.
- Cantidad incorrecta de campos.
- Movimiento distinto de `L` o `R`.
- Transiciones duplicadas para el mismo par `(estado_origen, simbolo_leido)`.
- Campos vacios.

Los errores deben indicar la linea que los produce. El parser no debe ejecutar la maquina ni mostrar ventanas.

## 7. Modulo de cinta: `cinta.py`

### Responsabilidad

Representar la cinta y las operaciones del cabezal.

### Operaciones

- Crear la cinta a partir de una cadena.
- Leer el simbolo de la posicion actual.
- Escribir un simbolo.
- Mover a la izquierda.
- Mover a la derecha.
- Obtener una vista de la cinta para la interfaz.

### Reglas

- La posicion inicial del cabezal es la primera posicion de la cadena.
- La cinta debe contener blanco a la derecha de la entrada.
- Si el cabezal sale del rango conocido, la cinta debe crear una celda `B`.
- Tambien debe permitir movimiento hacia la izquierda.
- No debe eliminar informacion escrita anteriormente.

La cinta se representara con un diccionario `dict[int, str]`. La cadena comenzara en la posicion `0` y se usaran indices negativos cuando el cabezal se mueva a la izquierda de esa posicion. No se renumerara la cinta al extenderla.

Ejemplo:

```python
cinta = {-1: "B", 0: "a", 1: "b", 2: "B"}
posicion_cabezal = -1
```

## 8. Modulo de configuracion: `configuracion.py`

### Responsabilidad

Guardar una fotografia de la maquina en un instante determinado.

### Datos minimos

- Numero de paso.
- Estado actual.
- Posicion del cabezal.
- Cinta visible.
- Simbolo leido.
- Transicion aplicada, si existe.
- Motivo de detencion, si la maquina se detuvo.

### Uso

La configuracion es la unidad que se agrega al historial y que la interfaz muestra como descripcion instantanea. Debe ser independiente de los widgets.

## 9. Modulo de ejecucion: `maquina_turing.py`

### Responsabilidad

Controlar el ciclo de ejecucion y producir configuraciones instantaneas.

### Operaciones

- Inicializar una cadena en `q0`.
- Ejecutar una transicion.
- Ejecutar un solo paso.
- Ejecutar hasta detenerse.
- Detener manualmente la ejecucion.
- Reiniciar usando la misma maquina y otra cadena.
- Consultar el historial.

### Algoritmo de un paso

Antes de ejecutar la primera transicion, el historial debe contener siempre la configuracion inicial como `Paso 0`.

1. Inicializar el estado en `q0`, el cabezal en la posicion `0` y la cinta con la cadena de entrada.
2. Registrar la configuracion inicial como `Paso 0`.
3. Leer el estado actual y el simbolo debajo del cabezal.
4. Si el estado es `qf`, finalizar como aceptada.
5. Buscar `(estado_actual, simbolo_leido)`.
6. Si no existe, registrar el motivo y finalizar como rechazada.
7. Escribir el nuevo simbolo.
8. Mover el cabezal. Si se mueve a la izquierda de `0`, usar una posicion negativa.
9. Cambiar al estado siguiente.
10. Registrar la nueva configuracion como el siguiente paso.

Por tanto:

- `Paso 0` representa la cinta inicial, antes de aplicar transiciones.
- `Paso 1` representa el resultado de aplicar la primera transicion.
- Cada paso posterior representa el resultado de una sola transicion.
- La configuracion donde falta una transicion debe conservarse con el motivo del rechazo.
- La configuracion donde se alcanza `qf` debe conservarse con el resultado de aceptacion.

La logica no debe depender de botones, velocidad, ventanas ni librerias graficas.

### Resultados posibles

- `ACEPTADA`: la maquina llega a `qf`.
- `RECHAZADA`: no existe una transicion aplicable.
- `DETENIDA`: el usuario interrumpe la ejecucion.

## 10. Modulo de descripcion instantanea

### Responsabilidad

Mostrar el proceso completo hasta el punto en que la maquina acepta, rechaza o se detiene.

La representacion principal debe indicar el estado y marcar el caracter leido. Por ejemplo:

```text
Paso 0
Estado: q0
Cinta: a b a b b B
Cabezal: ^
Simbolo leido: a
Transicion pendiente: q0, a -> q0, a, R

Paso 1
Cinta: a b a b b B
Cabezal:   ^
Estado: q0
Simbolo leido: b
Transicion aplicada: q0, a -> q0, a, R

Representacion lineal de apoyo:
q0 a b a b b B
			 ^
```

Despues de mover el cabezal:

```text
Paso 1: a q0 babb
			   ^
		 lee: b
```

Tambien puede presentarse en bloque:

```text
Paso 1
Cinta:       a  b  a  b  b  B
Cabezal:        ^
Estado:      q0
Lee:         b
Transicion:  q0, b -> q1, a, R
```

La vista debe mostrar el historial, no solo la configuracion actual, para que el usuario pueda revisar todos los pasos.

## 11. Modulo de tabla: `visualizacion/tabla_transiciones.py`

### Responsabilidad

Construir la tabla a partir de las transiciones cargadas.

### Formato

Las columnas son los simbolos leidos y las filas son los estados:

```text
Estado  | 1          | 0          | B
q0      | q1, 1, R   | q0, 0, R   | -
q1      | q1, 1, R   | q2, 0, L   | qf, B, R
q3      | -          | -          | qf, B, R
```

Una celda debe mostrar:

```text
estado_siguiente, simbolo_escrito, movimiento
```

Cuando no exista transicion, debe mostrar `-`.

Las filas y columnas deben generarse dinamicamente; no se deben fijar simbolos como `0`, `1` o `B` en el codigo.

## 12. Modulo de diagrama: `visualizacion/diagrama.py`

### Responsabilidad

Construir el grafo a partir de las mismas transiciones usadas por el motor.

### Reglas visuales

- Cada estado es un nodo.
- `q0` se identifica como estado inicial.
- `qf` se representa como estado final, preferiblemente con doble circulo.
- Cada flecha muestra:

```text
simbolo_leido, simbolo_escrito, movimiento
```

Ejemplo:

```text
q0 -- b, a, R --> q1
```

El diagrama no debe tener una segunda copia de las transiciones. Debe recibirlas del parser o de un modelo comun.

## 13. Modulo de interfaz: `interfaz/ventana_principal.py`

### Responsabilidad

Coordinar la interaccion del usuario sin contener la logica de la maquina.

### Controles

- `Cargar maquina`.
- Campo para la cadena a validar.
- `Ejecutar`.
- `Paso a paso`.
- `Pausar` o `Detener`.
- `Reiniciar`.
- Selector de velocidad: corto, medio y alto.

### Areas de informacion

- Diagrama de transiciones.
- Tabla de transiciones.
- Cinta y cabezal.
- Historial de descripciones instantaneas.
- Cadena resultante.
- Mensajes de validacion y resultado.

### Reglas de dependencia

- La interfaz puede llamar al parser, al motor y a los visualizadores.
- La interfaz no debe modificar directamente la cinta.
- La interfaz no debe interpretar el archivo linea por linea.
- La interfaz debe poder ejecutar el motor sin diagrama para facilitar las pruebas.

## 14. Punto de entrada: `main.py`

### Responsabilidad

Crear la aplicacion y abrir la ventana principal.

No debe contener la implementacion del parser, la cinta, el algoritmo de transiciones ni la construccion del diagrama.

## 15. Etapas de desarrollo

### Etapa 1: contrato y modelos

Implementar:

- `Transicion`.
- Estructura de errores.
- `Configuracion`.
- Convenciones del simulador.

Validar:

- Que una transicion conserve sus cinco datos.
- Que solo acepte `L` y `R`.

No crear interfaz en esta etapa.

### Etapa 2: parser

Implementar la lectura del archivo y las validaciones de sintaxis.

Validar con:

- Archivo correcto.
- Linea incompleta.
- Movimiento invalido.
- Transicion duplicada.
- Archivo vacio.

El resultado de esta etapa es un conjunto de transiciones listo para el motor.

### Etapa 3: cinta

Implementar lectura, escritura y movimiento en ambas direcciones.

Validar:

- Cadena normal.
- Escritura de un simbolo diferente.
- Movimiento a la derecha sobre `B`.
- Movimiento a la izquierda desde la primera posicion.
- Expansiones repetidas.

### Etapa 4: motor y descripcion instantanea

Implementar `MaquinaTuring` y el historial.

Validar:

- Aceptacion al llegar a `qf`.
- Rechazo por falta de transicion.
- Cadena modificada durante la ejecucion.
- Historial completo hasta el punto de detencion.
- Detencion manual de una maquina con ciclo.

Esta es la primera version funcional del simulador, aun sin interfaz.

### Etapa 5: tabla de transiciones

Construir la tabla dinamicamente usando el resultado del parser.

Validar:

- Estados como filas.
- Simbolos como columnas.
- `-` para transiciones inexistentes.
- Formato `estado, simbolo, movimiento` en cada celda.

### Etapa 6: diagrama

Construir el diagrama con las mismas transiciones del parser.

Validar:

- Todos los estados visibles.
- `q0` identificado como inicio.
- `qf` identificado como final.
- Etiquetas con formato `lee, escribe, movimiento`.

### Etapa 7: interfaz grafica

Integrar carga de archivo, entrada de cadena, tabla, diagrama, cinta, historial y controles.

Validar por flujo:

1. Cargar una maquina valida.
2. Ver tabla y diagrama.
3. Introducir una cadena.
4. Ejecutar automaticamente.
5. Ejecutar paso a paso.
6. Reiniciar.
7. Cambiar velocidad.
8. Detener una ejecucion no terminante.

### Etapa 8: pruebas de integracion y documentacion

Probar el flujo completo y documentar instalacion, ejecucion, formato del archivo y ejemplos.

## 16. Reglas para no afectar otros modulos

- Cada modulo debe tener una responsabilidad unica.
- Los modulos de logica no deben importar la interfaz.
- La tabla y el diagrama deben consumir el mismo modelo de transiciones.
- Los cambios visuales no deben modificar el algoritmo de la maquina.
- Antes de integrar una etapa, deben pasar las pruebas de las etapas anteriores.
- Los errores deben comunicarse mediante excepciones o resultados estructurados, no mediante `print` dentro de la logica.
- Las operaciones lentas de ejecucion deben poder detenerse sin bloquear la interfaz.
- No se deben duplicar reglas de aceptacion, rechazo o movimiento en la interfaz.

## 17. Criterios de finalizacion

El proyecto se considera terminado cuando:

- Puede cargar cualquier archivo valido de transiciones.
- Puede validar distintas cadenas sin recargar la maquina.
- Construye la tabla dinamicamente.
- Construye el diagrama con etiquetas `lee, escribe, movimiento`.
- Muestra el estado y el caracter actual en cada paso.
- Conserva y muestra todo el historial de descripciones instantaneas.
- Identifica aceptacion, rechazo y detencion manual.
- Permite ejecutar automaticamente, paso a paso y reiniciar.
- Permite seleccionar la velocidad.
- Informa errores de archivo y de ejecucion claramente.
- Las pruebas de logica funcionan sin iniciar la interfaz grafica.
