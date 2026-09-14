"""Interfaz grafica principal del simulador de Maquina de Turing."""

import os
import time
import tempfile
import threading
import queue
import tkinter as tk

# Solucionar escalado borroso y tamaños enormes en pantallas a 125% o mas (Windows)
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass
from tkinter import ttk, filedialog, messagebox

try:
    import graphviz
    from graphviz.backend.execute import ExecutableNotFound
except ImportError:
    graphviz = None
    ExecutableNotFound = Exception

from logica.parser import parsear_archivo, ResultadoParser
from logica.errores import ErrorArchivo, ErrorParser
from logica.maquina_turing import MaquinaTuring
from logica.configuracion import Configuracion
from visualizacion.tabla_transiciones import GeneradorTabla
from visualizacion.diagrama import GeneradorDiagrama


class SimuladorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simulador de Maquina de Turing")
        
        # Dimension base de respaldo
        self.root.geometry("1200x800")
        
        # Maximizar ventana dinamicamente para cualquier pantalla
        try:
            self.root.state('zoomed') # Nativo en Windows
        except tk.TclError:
            try:
                self.root.attributes('-zoomed', True) # Linux X11
            except tk.TclError:
                # Fallback universal si los anteriores fallan
                w = self.root.winfo_screenwidth()
                h = self.root.winfo_screenheight()
                self.root.geometry(f"{w}x{h}+0+0")
        
        self._configurar_estilos()

        # Variables de estado
        self.resultado_parser: ResultadoParser | None = None
        self.motor: MaquinaTuring | None = None
        self._img_diagrama = None
        
        # Variables de concurrencia e historial
        self.hilo_ejecucion: threading.Thread | None = None
        self.evento_detener = threading.Event()
        self.cola_actualizaciones = queue.Queue()
        self.ultimo_paso_mostrado = -1
        
        self._construir_menu()
        self._construir_ui()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("Treeview", font=("Consolas", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Consolas", 11, "bold"))

    def _construir_menu(self):
        menubar = tk.Menu(self.root)
        
        menu_pref = tk.Menu(menubar, tearoff=0)
        self.var_velocidad = tk.StringVar(value="Media")
        
        menu_velocidad = tk.Menu(menu_pref, tearoff=0)
        menu_velocidad.add_radiobutton(label="Lenta (1s)", variable=self.var_velocidad, value="Lenta")
        menu_velocidad.add_radiobutton(label="Media (0.5s)", variable=self.var_velocidad, value="Media")
        menu_velocidad.add_radiobutton(label="Rapida (0.1s)", variable=self.var_velocidad, value="Rapida")
        menu_velocidad.add_radiobutton(label="Inmediata (Sin espera)", variable=self.var_velocidad, value="Inmediata")
        
        menu_pref.add_cascade(label="Velocidad de ejecucion", menu=menu_velocidad)
        menubar.add_cascade(label="Preferencias", menu=menu_pref)
        
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Manual de uso", command=self._mostrar_manual)
        menu_ayuda.add_separator()
        menu_ayuda.add_command(label="Acerca del simulador", command=self._mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        self.root.config(menu=menubar)


    def _mostrar_manual(self):
        info = (
            "MANUAL DE USUARIO - ARCHIVO DE TRANSICIONES\n\n"
            "Para utilizar el simulador, debe cargar un archivo de texto (.txt) que defina las reglas de transicion.\n\n"
            "FORMATO REQUERIDO DE CADA LINEA:\n"
            "estado_actual, simbolo_leido -> estado_siguiente, simbolo_escrito, movimiento\n\n"
            "REGLAS FUNDAMENTALES:\n"
            "1. Estados: El estado inicial para arrancar la maquina siempre debe ser 'q0'. El estado de finalizacion (exito) siempre debe ser 'qf'.\n"
            "2. Movimiento: Solo se permite usar 'R' (Derecha) o 'L' (Izquierda).\n"
            "3. Simbolo Blanco: Se representa estrictamente con la letra 'B' mayuscula.\n"
            "4. Comentarios: Se pueden escribir libremente colocando un '#' al inicio o final de la linea.\n\n"
            "EJEMPLO:\n"
            "# Cambiar 1 por 0 y mover a la derecha\n"
            "q0, 1 -> q1, 0, R\n"
            "q1, B -> qf, B, R  # Terminar al encontrar un blanco"
        )
        messagebox.showinfo("Manual de uso", info)

    def _mostrar_acerca_de(self):
        info = (
            "Universidad de Panamá\n"
            "Facultad de Informática, Electrónica y Comunicación\n"
            "Ingeniería en Informática\n\n"
            "Simulador de Máquina de Turing\n"
            "Desarrollado por: Cristobal Prados , Carlos Gonzalez\n"
            "Año: 2026"
        )
        messagebox.showinfo("Acerca del simulador", info)

    def _construir_ui(self):
        # CONTROLES (Fila Superior Fija)
        frame_controles = ttk.LabelFrame(self.root, text="Controles de ejecucion", padding=10)
        frame_controles.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(frame_controles, text="Cargar archivo", command=self._cargar_archivo).pack(side=tk.LEFT, padx=5)
        self.lbl_archivo = ttk.Label(frame_controles, text="Sin archivo", foreground="gray")
        self.lbl_archivo.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_controles, text="Cadena:").pack(side=tk.LEFT, padx=(20, 5))
        self.var_cadena = tk.StringVar()
        self.var_cadena.trace_add("write", self._actualizar_cinta_previa)
        self.entry_cadena = ttk.Entry(frame_controles, textvariable=self.var_cadena, width=25)
        self.entry_cadena.pack(side=tk.LEFT, padx=5)
        
        self.btn_iniciar = ttk.Button(frame_controles, text="Iniciar Automatica", command=self._iniciar_maquina, state=tk.DISABLED)
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)
        
        self.btn_paso = ttk.Button(frame_controles, text="Paso Manual", command=self._paso_a_paso, state=tk.DISABLED)
        self.btn_paso.pack(side=tk.LEFT, padx=5)

        self.btn_stop = ttk.Button(frame_controles, text="Detener", command=self._detener, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.lbl_estado = ttk.Label(frame_controles, text="NO INICIADA", font=("Arial", 10, "bold"))
        self.lbl_estado.pack(side=tk.RIGHT, padx=10)

        # CUADRICULA PRINCIPAL 2x2
        self.panel_principal = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # FILA 1 (Top) 
        self.panel_fila1 = ttk.PanedWindow(self.panel_principal, orient=tk.HORIZONTAL)
        self.panel_principal.add(self.panel_fila1, weight=1)

        # [1, 1] Tabla de Transiciones
        frame_tabla = ttk.LabelFrame(self.panel_fila1, text="Tabla de Transiciones")
        self.panel_fila1.add(frame_tabla, weight=1)
        self.canvas_tabla = tk.Canvas(frame_tabla, bg="white", highlightthickness=0)
        scroll_t_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.canvas_tabla.yview)
        scroll_t_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.canvas_tabla.xview)
        self.canvas_tabla.configure(yscrollcommand=scroll_t_y.set, xscrollcommand=scroll_t_x.set)
        scroll_t_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_t_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_tabla.pack(fill=tk.BOTH, expand=True)

        # [1, 2] Diagrama de Transiciones
        frame_diagrama = ttk.LabelFrame(self.panel_fila1, text="Diagrama de Transiciones")
        self.panel_fila1.add(frame_diagrama, weight=1)
        self.canvas_diagrama = tk.Canvas(frame_diagrama, bg="white")
        scroll_d_y = ttk.Scrollbar(frame_diagrama, orient=tk.VERTICAL, command=self.canvas_diagrama.yview)
        scroll_d_x = ttk.Scrollbar(frame_diagrama, orient=tk.HORIZONTAL, command=self.canvas_diagrama.xview)
        self.canvas_diagrama.configure(yscrollcommand=scroll_d_y.set, xscrollcommand=scroll_d_x.set)
        scroll_d_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_d_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_diagrama.pack(fill=tk.BOTH, expand=True)
        self.lbl_diagrama_fallback = ttk.Label(self.canvas_diagrama, text="Cargue un archivo para ver el diagrama.")
        self.lbl_diagrama_fallback.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        #  FILA 2 (Bottom) 
        self.panel_fila2 = ttk.PanedWindow(self.panel_principal, orient=tk.HORIZONTAL)
        self.panel_principal.add(self.panel_fila2, weight=1)

        # [2, 1] Cinta Visual
        frame_cinta = ttk.LabelFrame(self.panel_fila2, text="Cinta Visual")
        self.panel_fila2.add(frame_cinta, weight=1)
        self.canvas_cinta = tk.Canvas(frame_cinta, bg="white")
        scroll_c_y = ttk.Scrollbar(frame_cinta, orient=tk.VERTICAL, command=self.canvas_cinta.yview)
        scroll_c_x = ttk.Scrollbar(frame_cinta, orient=tk.HORIZONTAL, command=self.canvas_cinta.xview)
        self.canvas_cinta.configure(yscrollcommand=scroll_c_y.set, xscrollcommand=scroll_c_x.set)
        scroll_c_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_c_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_cinta.pack(fill=tk.BOTH, expand=True)

        # [2, 2] Transcripcion Paso a Paso (Tabla elegante)
        frame_historial = ttk.LabelFrame(self.panel_fila2, text="Descripción Instantanea")
        self.panel_fila2.add(frame_historial, weight=1)
        
        self.tree_historial = ttk.Treeview(frame_historial, columns=("Paso", "Descripcion"), show="headings")
        self.tree_historial.heading("Paso", text="N.º")
        self.tree_historial.heading("Descripcion", text="Recorrido")
        self.tree_historial.column("Paso", width=80, anchor=tk.CENTER, stretch=False)
        self.tree_historial.column("Descripcion", width=500, anchor=tk.W, stretch=True)
        
        scroll_h_y = ttk.Scrollbar(frame_historial, orient=tk.VERTICAL, command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scroll_h_y.set)
        
        # [CORECCION]: Empacamos primero la etiqueta al BOTTOM. Asi nunca se ocultara,
        # sin importar que tan pequeña sea la pantalla.
        self.lbl_solucion = ttk.Label(frame_historial, text="", font=("Consolas", 14, "bold"), foreground="green")
        self.lbl_solucion.pack(side=tk.BOTTOM, pady=5)

        # Ahora si empacamos la tabla, la cual tomara unicamente el espacio que sobre.
        scroll_h_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_historial.pack(fill=tk.BOTH, expand=True)
        
        self.tree_historial.tag_configure('fila_par', background='#F0F8FF')
        self.tree_historial.tag_configure('fila_impar', background='#FFFFFF')

    def _generar_id_formal(self, cfg: Configuracion) -> str:
        if not cfg.cinta:
            return f"{cfg.estado} B"
            
        indices = list(cfg.cinta.keys())
        min_idx = min(indices + [cfg.posicion_cabezal])
        max_idx = max(indices + [cfg.posicion_cabezal])
        
        while min_idx < cfg.posicion_cabezal and cfg.cinta.get(min_idx, "B") == "B":
            min_idx += 1
        while max_idx > cfg.posicion_cabezal and cfg.cinta.get(max_idx, "B") == "B":
            max_idx -= 1
            
        partes = []
        for i in range(min_idx, max_idx + 1):
            if i == cfg.posicion_cabezal:
                partes.append(cfg.estado)
            partes.append(cfg.cinta.get(i, "B"))
            
        return " ".join(partes)


    def _actualizar_cinta_previa(self, *args):
        # Bloquear vista previa si la maquina esta en medio de una ejecucion
        if self.motor and self.motor.estado_ejecucion in ["EN_CURSO", "DETENIDA"]:
            return
            
        # Si termino y el usuario empieza a escribir, limpiamos para una nueva prueba
        if self.motor and self.motor.estado_ejecucion in ["ACEPTADA", "RECHAZADA"]:
            self.motor = None
            self._limpiar_historial()
            self._cambiar_estado_lbl("CARGADO" if self.resultado_parser else "NO INICIADA", "blue")
            self._actualizar_botones()

        cadena = self.var_cadena.get().strip()
        estado_inicial = "q0"
        if self.resultado_parser and self.resultado_parser.estados:
            estado_inicial = self.resultado_parser.estados[0]
            
        cinta_sim = {i: c for i, c in enumerate(cadena)}
        
        simbolo_leido = cadena[0] if cadena else "B"
        cfg_temp = Configuracion(
            estado=estado_inicial,
            cinta=cinta_sim,
            posicion_cabezal=0,
            paso=0,
            simbolo_leido=simbolo_leido,
            transicion_aplicada=None,
            transicion_pendiente=None
        )
        self._dibujar_cinta_visual(cfg_temp)
        self._actualizar_botones()

    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de transiciones",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            self.resultado_parser = parsear_archivo(ruta)
            self.lbl_archivo.config(text=os.path.basename(ruta), foreground="black")
            self._limpiar_historial()
            self._actualizar_tabla()
            self._actualizar_diagrama()

            self._actualizar_botones()
            self._cambiar_estado_lbl("CARGADO", "blue")

        except ErrorArchivo as e:
            messagebox.showerror("Error de Archivo", str(e))
        except ErrorParser as e:
            messagebox.showerror("Error de Parser", f"Error en linea {e.linea}:\n\n{e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _actualizar_tabla(self):
        self.canvas_tabla.delete("all")
        if not self.resultado_parser: return
        gen = GeneradorTabla(self.resultado_parser)
        columnas = gen.obtener_columnas()
        filas = gen.obtener_filas()

        ancho_celda = 130
        alto_celda = 32
        margen = 8
        ancho_estado = 105
        anchos = [ancho_estado] + [ancho_celda] * len(columnas[1:])

        x = margen
        for indice, columna in enumerate(columnas):
            ancho = anchos[indice]
            self.canvas_tabla.create_rectangle(
                x, margen, x + ancho, margen + alto_celda,
                fill="#DCE6F1", outline="#667085", width=1
            )
            self.canvas_tabla.create_text(
                x + ancho / 2, margen + alto_celda / 2,
                text=columna, font=("Consolas", 11, "bold"), fill="#1F2937"
            )
            x += ancho

        for fila_indice, fila in enumerate(filas):
            x = margen
            y = margen + (fila_indice + 1) * alto_celda
            fondo = "#F0F8FF" if fila_indice % 2 == 0 else "#FFFFFF"
            for columna_indice, valor in enumerate(fila):
                ancho = anchos[columna_indice]
                self.canvas_tabla.create_rectangle(
                    x, y, x + ancho, y + alto_celda,
                    fill=fondo, outline="#98A2B3", width=1
                )
                self.canvas_tabla.create_text(
                    x + ancho / 2, y + alto_celda / 2,
                    text=valor, font=("Consolas", 10), fill="#1F2937"
                )
                x += ancho

        ancho_total = margen * 2 + sum(anchos)
        alto_total = margen * 2 + (len(filas) + 1) * alto_celda
        self.canvas_tabla.configure(scrollregion=(0, 0, ancho_total, alto_total))

    def _actualizar_diagrama(self):
        if not self.resultado_parser: return
        self.canvas_diagrama.delete("all")
        gen = GeneradorDiagrama(self.resultado_parser)
        dot = gen.construir_grafo()
        if dot is None:
            self.lbl_diagrama_fallback.config(text="Graphviz no esta instalado.\nDiagrama deshabilitado.")
            self.lbl_diagrama_fallback.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            return
        try:
            ruta_base = os.path.join(tempfile.gettempdir(), ".diagrama_temp_turing")
            ruta_img = dot.render(filename=ruta_base, format="png", cleanup=True)
            self._img_diagrama = tk.PhotoImage(file=ruta_img)
            self.lbl_diagrama_fallback.place_forget()
            self.canvas_diagrama.create_image(0, 0, anchor=tk.NW, image=self._img_diagrama)
            self.canvas_diagrama.config(scrollregion=self.canvas_diagrama.bbox(tk.ALL))
        except ExecutableNotFound:
            self.lbl_diagrama_fallback.config(text="Libreria 'dot' no encontrada.\nInstala Graphviz.")
            self.lbl_diagrama_fallback.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _preparar_motor(self):
        """Valida e inicializa el motor desde el estado cero."""
        if not self.resultado_parser: return False
        cadena = self.var_cadena.get().strip()
        if not cadena:
            messagebox.showwarning("Cadena Vacia", "Debes ingresar una cadena de entrada antes de ejecutar.")
            return False
            
        self.motor = MaquinaTuring(self.resultado_parser.transiciones)
        self.motor.iniciar(cadena)
        self._limpiar_historial()
        return True

    def _iniciar_maquina(self):
        # Iniciar significa "preparar y ejecutar todo automaticamente" de un solo golpe.
        if self._preparar_motor():
            self._ejecutar_todo()

    def _paso_a_paso(self):
        # Si no esta iniciada o ya detuvimos una, reiniciamos el motor y damos 1 paso
        if not self.motor or self.motor.estado_ejecucion not in ["EN_CURSO", "DETENIDA"]:
            if not self._preparar_motor():
                return
                
        # Avanzar exactamente 1 paso
        if self.motor.estado_ejecucion == "EN_CURSO":
            self.motor.paso()
            self._refrescar_ui_desde_motor()
            self._actualizar_botones()

    def _ejecutar_todo(self):
        if not self.motor or self.motor.estado_ejecucion != "EN_CURSO": return

        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_paso.config(state=tk.DISABLED)
        self.entry_cadena.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        while not self.cola_actualizaciones.empty():
            self.cola_actualizaciones.get()
        self.evento_detener.clear()

        self.hilo_ejecucion = threading.Thread(target=self._bucle_hilo, daemon=True)
        self.hilo_ejecucion.start()
        self._procesar_cola()

    def _bucle_hilo(self):
        velocidades = {"Lenta": 1.0, "Media": 0.5, "Rapida": 0.1, "Inmediata": 0.0}
        delay = velocidades.get(self.var_velocidad.get(), 0.5)

        while not self.evento_detener.is_set():
            continuar = self.motor.paso()
            self.cola_actualizaciones.put("PASO")
            if not continuar: break
            if delay > 0: time.sleep(delay)
                
        if self.evento_detener.is_set():
            self.motor.detener()
            self.cola_actualizaciones.put("PASO")

        self.cola_actualizaciones.put("FIN")

    def _procesar_cola(self):
        try:
            while True:
                msg = self.cola_actualizaciones.get_nowait()
                if msg == "PASO":
                    self._refrescar_ui_desde_motor()
                elif msg == "FIN":
                    self._actualizar_botones()
                    return
        except queue.Empty:
            pass
        self.root.after(50, self._procesar_cola)

    def _detener(self):
        if self.hilo_ejecucion and self.hilo_ejecucion.is_alive():
            self.evento_detener.set()

    def _refrescar_ui_desde_motor(self):
        if not self.motor or not self.motor.historial: return
        cfg_ultima = self.motor.historial[-1]
        
        self._dibujar_cinta_visual(cfg_ultima)

        for i in range(self.ultimo_paso_mostrado + 1, len(self.motor.historial)):
            cfg = self.motor.historial[i]
            id_formal = self._generar_id_formal(cfg)
            tag = 'fila_par' if cfg.paso % 2 == 0 else 'fila_impar'
            
            # Insertamos en la tabla del historial
            item = self.tree_historial.insert("", tk.END, values=(cfg.paso, id_formal), tags=(tag,))
            self.tree_historial.see(item)
            
            # Solo muestra solucion final SI es aceptada. Si fue rechazada, omitimos.
            if self.motor.estado_ejecucion == "ACEPTADA" and i == len(self.motor.historial) - 1:
                indices = list(cfg.cinta.keys())
                if indices:
                    min_idx = min(indices)
                    max_idx = max(indices)
                    # Solucion extraida literalmente de la memoria (incluye Blancos intencionales, ignora el infinito)
                    solucion_cinta = "".join([cfg.cinta.get(idx, "B") for idx in range(min_idx, max_idx + 1)])
                else:
                    solucion_cinta = "B"
                self.lbl_solucion.config(text=f"Cadena Resultante: {solucion_cinta}")
            
            elif self.motor.estado_ejecucion == "RECHAZADA" and i == len(self.motor.historial) - 1:
                self.lbl_solucion.config(text="") # No mostrar solucion final si es rechazada

        self.ultimo_paso_mostrado = len(self.motor.historial) - 1

        est = self.motor.estado_ejecucion
        texto_estado = "EN CURSO" if est == "EN_CURSO" else est
        color = {"EN_CURSO": "orange", "ACEPTADA": "green", "RECHAZADA": "red", "DETENIDA": "purple"}.get(est, "black")
        self._cambiar_estado_lbl(texto_estado, color)

    def _dibujar_cinta_visual(self, cfg: Configuracion):
        self.canvas_cinta.delete("all")
        indices = list(cfg.cinta.keys()) if cfg.cinta else [0]
            
        min_idx = min(indices + [cfg.posicion_cabezal])
        max_idx = max(indices + [cfg.posicion_cabezal])
        start = min_idx - 2
        end = max_idx + 2
        
        celda_w = 45; celda_h = 45
        pad_x = 20; pad_y = 50 
        
        x = pad_x
        for i in range(start, end + 1):
            simbolo = cfg.cinta.get(i, "B")
            es_cabezal = (i == cfg.posicion_cabezal)
            color_fondo = "#e0f7fa" if es_cabezal else "white"
            color_borde = "red" if es_cabezal else "black"
            grosor = 2 if es_cabezal else 1
            
            self.canvas_cinta.create_rectangle(x, pad_y, x + celda_w, pad_y + celda_h, fill=color_fondo, outline=color_borde, width=grosor)
            self.canvas_cinta.create_text(x + celda_w/2, pad_y + celda_h/2, text=simbolo, font=("Consolas", 14, "bold"))
            
            if es_cabezal:
                self.canvas_cinta.create_text(x + celda_w/2, pad_y + celda_h + 10, text="^", font=("Consolas", 16, "bold"), fill="red")
                self.canvas_cinta.create_text(x + celda_w/2, pad_y + celda_h + 25, text=cfg.estado, font=("Consolas", 12, "bold"), fill="red")
            
            x += celda_w
            
        self.canvas_cinta.config(scrollregion=self.canvas_cinta.bbox(tk.ALL))
        self.canvas_cinta.update_idletasks()
        bbox = self.canvas_cinta.bbox(tk.ALL)
        w_visible = self.canvas_cinta.winfo_width()
        
        if bbox and w_visible > 1:
            total_w = bbox[2]
            if total_w > w_visible:
                idx_relativo = cfg.posicion_cabezal - start
                pos_x_cabezal = pad_x + (idx_relativo * celda_w) + (celda_w / 2)
                fraccion = max(0.0, min(1.0, (pos_x_cabezal - (w_visible / 2)) / total_w))
                self.canvas_cinta.xview_moveto(fraccion)

    def _limpiar_historial(self):
        self.ultimo_paso_mostrado = -1
        self.canvas_cinta.delete("all")
        self.lbl_solucion.config(text="")
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)

    def _actualizar_botones(self):
        cadena_valida = bool(self.var_cadena.get().strip())
        archivo_cargado = bool(self.resultado_parser)
        
        # Validacion de botones dependiente de que exista configuracion
        if not self.motor or self.motor.estado_ejecucion in ["NO_INICIADA", "DETENIDA", "ACEPTADA", "RECHAZADA"]:
            estado_btn = tk.NORMAL if (cadena_valida and archivo_cargado) else tk.DISABLED
            self.btn_iniciar.config(state=estado_btn)
            self.btn_paso.config(state=estado_btn)
            self.btn_stop.config(state=tk.DISABLED)
            self.entry_cadena.config(state=tk.NORMAL)
        elif self.hilo_ejecucion and self.hilo_ejecucion.is_alive():
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_paso.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.entry_cadena.config(state=tk.DISABLED)
        else:
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_paso.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.entry_cadena.config(state=tk.NORMAL)

    def _cambiar_estado_lbl(self, texto: str, color: str):
        self.lbl_estado.config(text=texto, foreground=color)


def run_app():
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()