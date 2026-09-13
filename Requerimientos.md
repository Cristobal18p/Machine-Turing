# Requerimientos del Simulador de Maquina de Turing

## 1. Descripcion general

El sistema debe permitir cargar y ejecutar maquinas de Turing deterministas de una cinta. La maquina se define mediante un archivo de transiciones y la cadena que se desea validar se introduce desde la interfaz grafica.

El simulador debe ser generico: no debe estar limitado a una cadena, un alfabeto, una cantidad fija de estados o un conjunto especifico de transiciones.

## 2. Objetivo general

Desarrollar una aplicacion en Python que permita visualizar y ejecutar una maquina de Turing, mostrando su tabla de transiciones, su diagrama de estados, la evolucion de la cinta y la descripcion instantanea completa hasta que la cadena sea aceptada, rechazada o la ejecucion sea detenida por el usuario.

## 3. Alcance

El sistema debe incluir:

- Carga de archivos de transiciones.
- Validacion del archivo cargado.
- Generacion dinamica de la tabla de transiciones.
- Generacion del diagrama de transiciones.
- Entrada de una cadena desde la interfaz.
- Ejecucion automatica.
- Ejecucion paso a paso.
- Pausa o detencion manual.
- Reinicio de la simulacion.
- Control de velocidad.
- Visualizacion de la cinta y del cabezal.
- Historial de descripciones instantaneas.
- Resultado final de aceptacion o rechazo.

## 4. Convenciones de la maquina

El simulador utilizara las siguientes convenciones:

- `q0` es el estado inicial.
- `qf` es el estado final de aceptacion.
- `B` representa el simbolo blanco.
- `R` representa movimiento hacia la derecha.
- `L` representa movimiento hacia la izquierda.
- El cabezal inicia sobre el primer caracter de la cadena.
- La maquina escribe el nuevo simbolo antes de realizar el movimiento.
- La cinta puede extenderse hacia ambos lados usando el simbolo blanco.
- La cinta se representara con `dict[int, str]`, comenzando la cadena en la posicion `0`.
- Las posiciones menores que `0` se utilizaran cuando el cabezal se mueva hacia la izquierda.
- La cinta no se renumerara al extenderse.
- Si la maquina llega a `qf`, la cadena es aceptada.
- Si no existe una transicion para el estado y simbolo actuales, la cadena es rechazada.
- No se utilizara un limite automatico de pasos.
- El usuario podra detener manualmente una maquina que no termine.

## 5. Formato del archivo de transiciones

El archivo debe contener unicamente las transiciones de la maquina. La cadena a validar se introducira desde la interfaz.

Cada linea debe utilizar el siguiente formato:

```text
estado_actual, simbolo_leido -> estado_siguiente, simbolo_escrito, movimiento
```

Ejemplo:

```text
q0, a -> q0, a, R
q0, b -> q1, a, R
q1, a -> q1, a, R
q1, b -> q1, b, R
q1, B -> qf, B, L
```

Los espacios deben ser opcionales. El sistema debe aceptar tanto:

```text
q0,a->q1,b,R
```

como:

```text
q0, a -> q1, b, R
```

Se permitiran comentarios con `#` y lineas vacias:

```text
# Avanza sobre el simbolo a
q0, a -> q0, a, R

q0, b -> qf, b, R  # Acepta despues de leer b
```

## 6. Herramientas y tecnologias de desarrollo

### 6.1. Lenguaje y version

- Lenguaje principal: Python 3.
- Version recomendada: Python 3.11 o superior.
- El proyecto debe ejecutarse en Windows y conservar compatibilidad con otros sistemas cuando sea posible.

### 6.2. Entorno de desarrollo

- Editor recomendado: Visual Studio Code.
- Control de versiones: Git.
- Terminal de trabajo: PowerShell en Windows o una terminal compatible.
- Entorno virtual recomendado: `venv`.

### 6.3. Interfaz grafica

- Libreria principal: `tkinter`.
- `tkinter` se utilizara para ventanas, botones, campos de entrada, tablas, areas de texto, controles de velocidad y visualizacion de la cinta.
- No se utilizara una libreria grafica externa como requisito obligatorio.

### 6.4. Diagrama de transiciones

- Herramienta principal: Graphviz.
- Paquete Python opcional: `graphviz`.
- El motor de la maquina y la tabla deben funcionar aunque Graphviz no este instalado.
- Si Graphviz no esta disponible, la aplicacion debe informar el problema sin impedir la ejecucion del simulador.

Instalacion opcional del paquete Python:

```powershell
python -m pip install graphviz
```

En Windows tambien puede ser necesario instalar el programa Graphviz del sistema y agregar su carpeta `bin` al `PATH`.

### 6.5. Ejecucion automatica

- Herramientas: `threading`, `queue` y `after()` de `tkinter`.
- `threading` permitira ejecutar la maquina sin congelar la ventana.
- `queue` permitira enviar configuraciones desde el motor hacia la interfaz.
- `after()` permitira actualizar los controles graficos desde el hilo principal de `tkinter`.
- El hilo de ejecucion no debe modificar directamente widgets de la interfaz.

### 6.6. Pruebas

- Framework: `unittest`.
- `unittest` se utilizara para probar el parser, la cinta, el motor y las validaciones.
- Las pruebas de logica no deben requerir abrir la interfaz grafica.

Ejemplo de ejecucion:

```powershell
python -m unittest discover -s test -v
```

### 6.7. Bibliotecas de la biblioteca estandar

Cuando sea suficiente, se utilizaran herramientas incluidas en Python:

- `dataclasses` para modelos de datos.
- `pathlib` para rutas y archivos.
- `re` para validar el formato de las transiciones.
- `threading` para la ejecucion automatica.
- `queue` para comunicar el motor con la interfaz.
- `unittest` para pruebas.

### 6.8. Organizacion del entorno

El proyecto debe conservar esta separacion:

```text
src/       Codigo de la aplicacion.
test/      Pruebas automatizadas.
archivo_ejemplo/  Archivos de transiciones para pruebas manuales.
```

Las dependencias opcionales deben documentarse y no deben incorporarse directamente dentro de la logica del motor.

## 7. Requerimientos funcionales

### RF-01. Cargar maquina

El usuario debe poder seleccionar un archivo de transiciones desde la interfaz.

Al cargarlo, el sistema debe leer, analizar y validar todas sus transiciones.

### RF-02. Validar archivo

El sistema debe informar errores cuando:

- El archivo no exista.
- El archivo no pueda leerse.
- Una linea no contenga `->`.
- Una transicion tenga campos incompletos.
- Existan campos vacios.
- El movimiento no sea `L` ni `R`.
- Existan transiciones duplicadas para el mismo estado y simbolo leido.

Los mensajes de error deben indicar la linea donde se encontro el problema.

### RF-03. Mostrar tabla de transiciones

Despues de cargar correctamente la maquina, el sistema debe mostrar una tabla dinamica.

- Las filas representan los estados.
- Las columnas representan los simbolos que pueden leerse.
- Cada celda contiene la transicion correspondiente.
- Una celda sin transicion debe mostrar `-`.

Ejemplo:

```text
Estado  | 1          | 0          | B
q0      | q1, 1, R   | q0, 0, R   | -
q1      | q1, 1, R   | q2, 0, L   | qf, B, R
```

El contenido de cada celda debe tener el formato:

```text
estado_siguiente, simbolo_escrito, movimiento
```

### RF-04. Mostrar diagrama de transiciones

Despues de cargar correctamente la maquina, el sistema debe mostrar un diagrama dirigido.

El diagrama debe incluir:

- Todos los estados encontrados.
- El estado inicial `q0`.
- El estado final `qf`.
- Una flecha por cada transicion.
- La etiqueta de cada flecha.

Las etiquetas deben utilizar el formato:

```text
simbolo_leido, simbolo_escrito, movimiento
```

Ejemplo:

```text
q0 -- b, a, R --> q1
```

### RF-05. Introducir cadena

El usuario debe poder escribir en la interfaz la cadena que desea validar despues de cargar la maquina.

La misma maquina debe poder utilizarse para validar varias cadenas sin volver a cargar el archivo de transiciones.

### RF-06. Inicializar cinta

Al iniciar una validacion:

- La cinta debe contener la cadena introducida.
- El cabezal debe comenzar en el primer caracter.
- El estado actual debe ser `q0`.
- Debe existir espacio blanco `B` despues de la cadena.
- La cinta debe poder extenderse hacia la izquierda y la derecha.

### RF-07. Ejecutar un paso

El sistema debe permitir ejecutar una sola transicion cada vez.

Antes de ejecutar la primera transicion, el sistema debe registrar la configuracion inicial como `Paso 0`:

```text
Paso: 0
Estado: q0
Cinta: a b a b b B
Cabezal: ^
Simbolo leido: a
Transicion pendiente: q0, a -> q0, a, R
```

En cada paso debe:

1. Leer el estado actual.
2. Leer el simbolo bajo el cabezal.
3. Buscar la transicion correspondiente.
4. Escribir el nuevo simbolo.
5. Mover el cabezal a la izquierda o derecha.
6. Cambiar al estado siguiente.
7. Registrar el resultado como el siguiente paso del historial.

La numeracion debe seguir estas reglas:

- `Paso 0` es la configuracion inicial, antes de aplicar transiciones.
- `Paso 1` es el resultado de aplicar la primera transicion.
- Cada paso representa una unica transicion ejecutada.
- Si no existe una transicion, se conserva la configuracion actual y se registra el motivo del rechazo.
- Si se llega a `qf`, se conserva la configuracion final y se registra la aceptacion.

### RF-08. Ejecutar automaticamente

El sistema debe permitir ejecutar la maquina automaticamente hasta que:

- Llegue a `qf`.
- No exista una transicion aplicable.
- El usuario detenga la ejecucion.

La ejecucion automatica no debe bloquear la interfaz.

### RF-09. Mostrar descripcion instantanea

El sistema debe mostrar el proceso completo paso a paso hasta el punto de detencion.

Cada descripcion debe incluir:

- Numero de paso.
- Estado actual.
- Contenido de la cinta.
- Posicion del cabezal.
- Simbolo leido.
- Transicion aplicada, si existe.
- Estado siguiente, cuando corresponda.

La vista principal debe utilizar un formato en bloque:

```text
Paso: 2
Estado: q1
Cinta: a a a b b B
Cabezal:       ^
Simbolo leido: b
Transicion: q1, b -> q1, b, R
```

Tambien puede mostrar una representacion lineal de apoyo:

```text
a a a q1 b b B
```

### RF-10. Mostrar resultado

Al finalizar la ejecucion, el sistema debe informar uno de estos resultados:

```text
CADENA ACEPTADA
```

```text
CADENA RECHAZADA
```

```text
EJECUCION DETENIDA POR EL USUARIO
```

Cuando corresponda, debe mostrar la razon, por ejemplo:

```text
No existe transicion para el estado q1 y el simbolo B.
```

### RF-11. Pausar o detener

El usuario debe poder detener una ejecucion automatica, incluso si la maquina contiene un ciclo y no termina por si misma.

### RF-12. Reiniciar

El usuario debe poder reiniciar la simulacion para:

- Volver al estado `q0`.
- Restaurar la cadena original.
- Colocar el cabezal en la primera posicion.
- Limpiar el historial anterior.
- Ejecutar nuevamente la misma cadena.

### RF-13. Controlar velocidad

La interfaz debe incluir tres velocidades:

- Corta.
- Media.
- Alta.

La velocidad solo debe modificar el tiempo entre pasos y no el resultado de la maquina.

## 8. Requerimientos no funcionales

### RNF-01. Separacion de responsabilidades

La logica de la maquina, el parser, la cinta, la tabla, el diagrama y la interfaz deben estar separados en modulos.

### RNF-02. Independencia de la interfaz

El motor debe poder ejecutarse y probarse sin iniciar la interfaz grafica.

### RNF-03. Generalidad

El sistema no debe tener condiciones especificas para cadenas, estados o simbolos concretos.

### RNF-04. Mantenibilidad

Los cambios en la interfaz no deben modificar el algoritmo de ejecucion.

### RNF-05. Responsividad

La ejecucion automatica debe ejecutarse en un hilo separado para evitar que la ventana se congele.

### RNF-06. Portabilidad

La aplicacion debe utilizar Python y `tkinter` como libreria grafica principal, evitando dependencias obligatorias adicionales.

### RNF-07. Tolerancia de Graphviz

La tabla y el motor deben seguir funcionando si Graphviz no esta instalado. El sistema debe mostrar un mensaje claro cuando no pueda generar el diagrama.

### RNF-08. Pruebas

La logica debe probarse con `unittest`, sin requerir iniciar la interfaz grafica.

## 9. Casos de aceptacion

### CA-01. Cargar archivo valido

Dado un archivo con transiciones validas, al pulsar `Cargar maquina`, el sistema debe mostrar la tabla y el diagrama.

### CA-02. Rechazar archivo invalido

Dado un archivo con una transicion mal formada, el sistema debe informar el numero de linea y no iniciar la maquina.

### CA-03. Aceptar una cadena

Dada una maquina que alcanza `qf`, al ejecutar una cadena valida, el sistema debe mostrar todas las descripciones instantaneas y `CADENA ACEPTADA`.

### CA-04. Rechazar por falta de transicion

Dada una maquina sin transicion para el estado y simbolo actuales, el sistema debe detenerse y mostrar `CADENA RECHAZADA` con la razon correspondiente.

### CA-05. Mostrar modificaciones de la cinta

Si una transicion escribe un simbolo diferente al leido, el historial debe mostrar la cinta modificada desde ese paso.

### CA-06. Moverse hacia la izquierda

Si el cabezal se mueve a la izquierda desde la posicion inicial, la cinta debe crear o consultar una celda blanca con una posicion negativa, sin renumerar ni perder la cadena original.

### CA-06a. Registrar la configuracion inicial

Al iniciar una validacion, el historial debe contener un `Paso 0` antes de ejecutar cualquier transicion. Este paso debe mostrar el estado `q0`, la cadena original, la posicion inicial del cabezal y el simbolo leido.

### CA-07. Ejecutar paso a paso

Al pulsar `Paso a paso`, el sistema debe avanzar una sola transicion y actualizar el estado, la cinta, el cabezal y el historial.

### CA-08. Detener una maquina no terminante

Si la maquina entra en un ciclo, el usuario debe poder detenerla sin cerrar la aplicacion.

### CA-09. Reiniciar

Al pulsar `Reiniciar`, la maquina debe volver al estado inicial y borrar el historial de la ejecucion anterior.

### CA-10. Probar varias cadenas

Una maquina cargada debe poder validar distintas cadenas de entrada sin volver a cargar sus transiciones.

## 10. Criterios de finalizacion

El sistema se considerara terminado cuando:

- Cargue y valide archivos de transiciones.
- Genere la tabla de forma dinamica.
- Genere o informe correctamente el estado del diagrama.
- Permita introducir distintas cadenas.
- Ejecute automaticamente y paso a paso.
- Muestre la descripcion instantanea completa.
- Muestre la cinta resultante.
- Distinga aceptacion, rechazo y detencion manual.
- Permita reiniciar y cambiar la velocidad.
- Mantenga separada la logica de la interfaz.
- Cumpla los casos de aceptacion.
