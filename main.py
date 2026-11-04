import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import io
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
import webbrowser
import re


class HorarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Horarios - Liceo Ana Elpidia Sánchez")
        self.root.geometry("1200x750")

        # Variables
        self.ruta_raw = tk.StringVar()
        self.ruta_salvado = tk.StringVar()
        self.nombre_centro = tk.StringVar(value="Liceo Ana Elpidia Sánchez")
        self.ruta_fet = tk.StringVar()
        self.ruta_html_salida = tk.StringVar()

        # Inicializar base de datos
        self.init_database()

        # Crear tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab principal - Procesar Horarios
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Procesar Horarios")

        # Tab - Gestión XML
        self.xml_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.xml_tab, text="Gestión XML")

        # Tab de datos
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Datos de Configuración")

        self.create_main_tab()
        self.create_xml_tab()
        self.create_data_tab()

        # Cargar datos iniciales
        self.load_data()

    def init_database(self):
        """Inicializar la base de datos SQLite"""
        self.conn = sqlite3.connect('horario_config.db')
        self.cursor = self.conn.cursor()

        # Crear tabla de configuración
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                nombre_centro TEXT,
                ruta_raw TEXT,
                ruta_salvado TEXT,
                ruta_fet TEXT,
                ruta_html_salida TEXT
            )
        ''')

        # Crear tabla de profesores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE
            )
        ''')

        self.conn.commit()

    def load_data(self):
        """Cargar datos de la base de datos"""
        # Cargar configuración
        self.cursor.execute("SELECT nombre_centro, ruta_raw, ruta_salvado, ruta_fet, ruta_html_salida FROM config LIMIT 1")
        config = self.cursor.fetchone()
        if config:
            self.nombre_centro.set(config[0])
            self.ruta_raw.set(config[1] if config[1] else '')
            self.ruta_salvado.set(config[2] if config[2] else '')
            self.ruta_fet.set(config[3] if config[3] else '')
            self.ruta_html_salida.set(config[4] if config[4] else '')
            
            self.nombre_centro_entry.delete(0, tk.END)
            self.nombre_centro_entry.insert(0, config[0])
            self.ruta_raw_entry.delete(0, tk.END)
            self.ruta_raw_entry.insert(0, config[1] if config[1] else '')
            self.ruta_salvado_entry.delete(0, tk.END)
            self.ruta_salvado_entry.insert(0, config[2] if config[2] else '')
            self.ruta_fet_entry.delete(0, tk.END)
            self.ruta_fet_entry.insert(0, config[3] if config[3] else '')
            self.ruta_html_salida_entry.delete(0, tk.END)
            self.ruta_html_salida_entry.insert(0, config[4] if config[4] else '')

        # Cargar profesores
        self.cursor.execute("SELECT nombre FROM profesores ORDER BY nombre")
        profesores = self.cursor.fetchall()

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar profesores
        for prof in profesores:
            self.tree.insert('', 'end', values=(prof[0],))

    def create_main_tab(self):
        """Crear el tab principal para procesar horarios"""
        # Frame para rutas
        frame_rutas = ttk.LabelFrame(self.main_tab, text="Configuración de Rutas", padding=10)
        frame_rutas.pack(fill='x', padx=10, pady=10)

        # Ruta RAW
        ttk.Label(frame_rutas, text="Ruta RAW (FET Results):").grid(row=0, column=0, sticky='w', pady=5)
        self.ruta_raw_entry = ttk.Entry(frame_rutas, textvariable=self.ruta_raw, width=70)
        self.ruta_raw_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_rutas, text="Seleccionar", command=self.select_raw_folder).grid(row=0, column=2, padx=5, pady=5)

        # Ruta Salvado
        ttk.Label(frame_rutas, text="Ruta de Destino:").grid(row=1, column=0, sticky='w', pady=5)
        self.ruta_salvado_entry = ttk.Entry(frame_rutas, textvariable=self.ruta_salvado, width=70)
        self.ruta_salvado_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_rutas, text="Seleccionar", command=self.select_save_folder).grid(row=1, column=2, padx=5, pady=5)

        # Frame para botones de acción
        frame_accion = ttk.LabelFrame(self.main_tab, text="Acciones", padding=10)
        frame_accion.pack(fill='x', padx=10, pady=10)

        ttk.Button(frame_accion, text="Procesar Horarios", command=self.procesar_horarios,
                   style='Accent.TButton').pack(pady=10)

        # Frame para logs
        frame_logs = ttk.LabelFrame(self.main_tab, text="Logs", padding=10)
        frame_logs.pack(fill='both', expand=True, padx=10, pady=10)

        self.log_text = tk.Text(frame_logs, height=10, wrap='word')
        self.log_text.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Estilo para botón de acento
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

    def create_xml_tab(self):
        """Crear el tab para gestión de XML"""
        # Frame para rutas
        frame_rutas = ttk.LabelFrame(self.xml_tab, text="Configuración de Archivos FET", padding=10)
        frame_rutas.pack(fill='x', padx=10, pady=10)

        # Ruta del archivo FET
        ttk.Label(frame_rutas, text="Archivo FET (.fet):").grid(row=0, column=0, sticky='w', pady=5)
        self.ruta_fet_entry = ttk.Entry(frame_rutas, textvariable=self.ruta_fet, width=70)
        self.ruta_fet_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_rutas, text="Seleccionar", command=self.select_fet_file).grid(row=0, column=2, padx=5, pady=5)

        # Ruta de salida HTML
        ttk.Label(frame_rutas, text="Ruta de Salida HTML:").grid(row=1, column=0, sticky='w', pady=5)
        self.ruta_html_salida_entry = ttk.Entry(frame_rutas, textvariable=self.ruta_html_salida, width=70)
        self.ruta_html_salida_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_rutas, text="Seleccionar", command=self.select_html_output_folder).grid(row=1, column=2, padx=5, pady=5)

        # Frame para botones de acción
        frame_accion = ttk.LabelFrame(self.xml_tab, text="Acciones", padding=10)
        frame_accion.pack(fill='x', padx=10, pady=10)

        btn_frame = ttk.Frame(frame_accion)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Generar Carga de Maestros", 
                   command=self.generar_carga_maestros,
                   style='Accent.TButton').pack(side='left', padx=10)

        ttk.Button(btn_frame, text="Generar Restricciones Estudiantes", 
                   command=self.generar_restricciones_estudiantes,
                   style='Accent.TButton').pack(side='left', padx=10)

        ttk.Button(btn_frame, text="Generar Restricciones Profesores", 
                   command=self.generar_restricciones_profesores,
                   style='Accent.TButton').pack(side='left', padx=10)

        ttk.Button(btn_frame, text="Generar Todas las Restricciones", 
                   command=self.generar_todas_restricciones,
                   style='Accent.TButton').pack(side='left', padx=10)

        # Frame para logs XML
        frame_logs = ttk.LabelFrame(self.xml_tab, text="Logs", padding=10)
        frame_logs.pack(fill='both', expand=True, padx=10, pady=10)

        self.xml_log_text = tk.Text(frame_logs, height=10, wrap='word')
        self.xml_log_text.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.xml_log_text)
        scrollbar.pack(side='right', fill='y')
        self.xml_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.xml_log_text.yview)

    def create_data_tab(self):
        """Crear el tab de datos"""
        # Frame para nombre del centro
        frame_centro = ttk.LabelFrame(self.data_tab, text="Nombre del Centro", padding=10)
        frame_centro.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_centro, text="Nombre:").pack(side='left', padx=5)
        self.nombre_centro_entry = ttk.Entry(frame_centro, textvariable=self.nombre_centro, width=60)
        self.nombre_centro_entry.pack(side='left', padx=5)
        ttk.Button(frame_centro, text="Guardar", command=self.guardar_centro).pack(side='left', padx=5)

        # Frame para profesores
        frame_profesores = ttk.LabelFrame(self.data_tab, text="Lista de Profesores", padding=10)
        frame_profesores.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame para agregar profesor
        frame_agregar = ttk.Frame(frame_profesores)
        frame_agregar.pack(fill='x', pady=5)

        ttk.Label(frame_agregar, text="Nuevo Profesor:").pack(side='left', padx=5)
        self.nuevo_profesor_entry = ttk.Entry(frame_agregar, width=50)
        self.nuevo_profesor_entry.pack(side='left', padx=5)
        ttk.Button(frame_agregar, text="Agregar", command=self.agregar_profesor).pack(side='left', padx=5)
        ttk.Button(frame_agregar, text="Cargar Profesores por Defecto",
                   command=self.cargar_profesores_defecto).pack(side='left', padx=5)

        # Tabla de profesores
        frame_tabla = ttk.Frame(frame_profesores)
        frame_tabla.pack(fill='both', expand=True, pady=5)

        columns = ('nombre',)
        self.tree = ttk.Treeview(frame_tabla, columns=columns, show='headings', height=15)
        self.tree.heading('nombre', text='Nombre del Profesor')
        self.tree.column('nombre', width=400)

        scrollbar_y = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')

        # Botones para eliminar
        frame_botones = ttk.Frame(frame_profesores)
        frame_botones.pack(pady=5)

        ttk.Button(frame_botones, text="Eliminar Seleccionado",
                   command=self.eliminar_profesor).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar Todos",
                   command=self.eliminar_todos_profesores).pack(side='left', padx=5)

    def select_raw_folder(self):
        """Seleccionar carpeta RAW"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta RAW (FET Results)")
        if folder:
            self.ruta_raw.set(os.path.normpath(folder))
            self.guardar_configuracion()

    def select_save_folder(self):
        """Seleccionar carpeta de destino"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self.ruta_salvado.set(os.path.normpath(folder))
            self.guardar_configuracion()

    def select_fet_file(self):
        """Seleccionar archivo FET"""
        file = filedialog.askopenfilename(
            title="Seleccionar archivo FET",
            filetypes=[("FET files", "*.fet"), ("All files", "*.*")]
        )
        if file:
            self.ruta_fet.set(os.path.normpath(file))
            # Auto-completar ruta de salida HTML
            if not self.ruta_html_salida.get():
                directorio = os.path.dirname(file)
                self.ruta_html_salida.set(directorio)
                self.ruta_html_salida_entry.delete(0, tk.END)
                self.ruta_html_salida_entry.insert(0, directorio)
            self.guardar_configuracion()

    def select_html_output_folder(self):
        """Seleccionar carpeta de salida HTML"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida para HTML")
        if folder:
            self.ruta_html_salida.set(os.path.normpath(folder))
            self.guardar_configuracion()

    def guardar_configuracion(self):
        """Guardar configuración en la base de datos"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO config (id, nombre_centro, ruta_raw, ruta_salvado, ruta_fet, ruta_html_salida)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (self.nombre_centro.get(), self.ruta_raw.get(), self.ruta_salvado.get(), 
                  self.ruta_fet.get(), self.ruta_html_salida.get()))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")

    def guardar_centro(self):
        """Guardar solo el nombre del centro"""
        self.guardar_configuracion()
        messagebox.showinfo("Éxito", "Nombre del centro guardado correctamente")

    def agregar_profesor(self):
        """Agregar un profesor a la base de datos"""
        nombre = self.nuevo_profesor_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese un nombre de profesor")
            return

        try:
            self.cursor.execute("INSERT INTO profesores (nombre) VALUES (?)", (nombre,))
            self.conn.commit()
            self.nuevo_profesor_entry.delete(0, tk.END)
            self.load_data()
            messagebox.showinfo("Éxito", f"Profesor '{nombre}' agregado correctamente")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"El profesor '{nombre}' ya existe")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar profesor: {str(e)}")

    def eliminar_profesor(self):
        """Eliminar el profesor seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un profesor para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar el profesor seleccionado?"):
            nombre = self.tree.item(selected[0])['values'][0]
            try:
                self.cursor.execute("DELETE FROM profesores WHERE nombre = ?", (nombre,))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Éxito", f"Profesor '{nombre}' eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar profesor: {str(e)}")

    def eliminar_todos_profesores(self):
        """Eliminar todos los profesores"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar todos los profesores?"):
            try:
                self.cursor.execute("DELETE FROM profesores")
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Éxito", "Todos los profesores eliminados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar profesores: {str(e)}")

    def cargar_profesores_defecto(self):
        """Cargar la lista de profesores por defecto"""
        profesores_defecto = [
            "Eddy Wilson Díaz Sánchez", "Miguelina Díaz", "Franny Reyemic Ramirez De Fernández",
            "Johanna Altagracia Pujols de Feliz", "Leandro Díaz Díaz", "Navidad Del Jesús Sánchez Sánchez",
            "Romilia Féliz Morón", "Prof. Inglés", "Mario Moreno Pérez Paula", "Prof. Informática",
            "Darlenny Custodio", "Eridania Marte", "Rosa Naut", "César Méndez Beltré",
            "Geraldo Sánchez Cuevas", "Arnaldo Andrés Agramonte Carrasco", "Mirely Geraldo",
            "Prof. Francés Tercero", "Profe. Educación Física", "Elsa Jonmari Tejeda",
            "Luz Maria", "Emelin Stephany Santana Concepción", "Yadiela Féliz", "Rosa María Sención",
            "Smarlin Ramírez", "Miulca Janogui Peguero Barreiro", "Prof. Matemática",
            "Luchy Margarita De la Cruz", "Rosmerys Lebrón García", "Anny Sugeidy Rossó Hernández",
            "Jacinto Féliz", "DEISI MILAGROS PIMENTEL", "MIRELLA DE LEÓN", "MARY E. ESCALANTE",
            "MELANIA ESCALANTE", "JORGE ERADYS MINYETI", "MAESTRO EN PROYECTO", "LUISAS ZAYAS",
            "MERALIS ESCALANTE", "ANDREA MAÑÓN", "DOMINGA DE LEÓN", "DOMINGA FÉLIZ", "CAROLINA",
            "HUMBERTO CÉSPEDES", "ELADIO DE LEÓN", "CARMEN MEJÍA", "ROLANDO MÉNDEZ", "ANEUDY FÉLIZ",
            "GEORGINA RODRÍGUEZ", "MANUELA REYES MÉNDEZ", "BLADIMIL PEREZ", "MAESTRO MATEMÁTICA X",
            "YENIFER DANIELISA JIMENEZ QUEZADA", "YOKAIRA MARISOL AGRAMONTE PUJOLS",
            "EUNICE PÉREZ FIGUEREO", "CINTHIA ELIZABETH PINEDA AYBAR", "YISSETT ESMERALDA MARTINEZ TAPIA",
            "PROF. EDUCACIÓN FISICA", "PROF. FRANCÉS", "PROF. TALLERES 1", "PROF. TALLERES 2",
            "MARÍA NICAURIS MÉNDEZ"
        ]

        if messagebox.askyesno("Confirmar", "¿Desea cargar los profesores por defecto? (Se eliminarán los actuales)"):
            try:
                self.cursor.execute("DELETE FROM profesores")
                for profesor in profesores_defecto:
                    self.cursor.execute("INSERT INTO profesores (nombre) VALUES (?)", (profesor,))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Éxito", f"Se cargaron {len(profesores_defecto)} profesores correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar profesores: {str(e)}")

    def get_profesores_from_db(self):
        """Obtener la lista de profesores de la base de datos"""
        self.cursor.execute("SELECT nombre FROM profesores ORDER BY nombre")
        return [row[0] for row in self.cursor.fetchall()]

    def replace_brake(self, miarray, hora, texto):
        """Reemplazar los marcadores -X- con el texto correspondiente"""
        p = [i for i, item in enumerate(miarray) if hora in item]
        for m in p:
            for i in range(1, 6):
                if m + i < len(miarray):
                    miarray[m + i] = miarray[m + i].replace('-X-', texto)

    def log_message(self, message):
        """Agregar mensaje al log principal"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def xml_log_message(self, message):
        """Agregar mensaje al log XML"""
        self.xml_log_text.insert(tk.END, message + "\n")
        self.xml_log_text.see(tk.END)
        self.root.update()

    def obtener_nombre_inicial(self, ruta_raw):
        """Obtener el nombre inicial del archivo a partir de la ruta"""
        ruta_normalizada = os.path.normpath(ruta_raw)
        nombre_carpeta = os.path.basename(ruta_normalizada)

        if "-multi" in nombre_carpeta:
            inicial_nombre = nombre_carpeta.replace("-multi", "")
        else:
            inicial_nombre = nombre_carpeta.replace("-single", "")

        return inicial_nombre

    def procesar_horarios(self):
        """Procesar los horarios"""
        if not self.ruta_raw.get():
            messagebox.showerror("Error", "Seleccione la ruta RAW")
            return
        if not self.ruta_salvado.get():
            messagebox.showerror("Error", "Seleccione la ruta de destino")
            return

        nombres_profesores = self.get_profesores_from_db()
        if not nombres_profesores:
            messagebox.showerror("Error", "No hay profesores en la base de datos")
            return

        try:
            nombre_centro = self.nombre_centro.get()
            ruta_raw = os.path.normpath(self.ruta_raw.get())
            ruta_salvado = os.path.normpath(self.ruta_salvado.get())

            inicial_nombre = self.obtener_nombre_inicial(ruta_raw)

            self.log_message(f"Ruta RAW: {ruta_raw}")
            self.log_message(f"Ruta Destino: {ruta_salvado}")
            self.log_message(f"Nombre inicial:stylesh {inicial_nombre}")

            estilo = "styles.css"

            raw_estudiante = os.path.join(ruta_raw, f"{inicial_nombre}_subgroups_days_horizontal.html")
            raw_profesores = os.path.join(ruta_raw, f"{inicial_nombre}_teachers_days_horizontal.html")

            self.log_message(f"Buscando archivo estudiantes: {raw_estudiante}")
            self.log_message(f"Buscando archivo profesores: {raw_profesores}")

            if not os.path.exists(raw_estudiante):
                import glob
                patron_estudiantes = os.path.join(ruta_raw, "*_subgroups_days_horizontal.html")
                archivos_encontrados = glob.glob(patron_estudiantes)
                if archivos_encontrados:
                    raw_estudiante = archivos_encontrados[0]
                    self.log_message(f"Archivo de estudiantes encontrado: {raw_estudiante}")
                else:
                    messagebox.showerror("Error", f"No se encuentra el archivo: {raw_estudiante}")
                    return

            if not os.path.exists(raw_profesores):
                import glob
                patron_profesores = os.path.join(ruta_raw, "*_teachers_days_horizontal.html")
                archivos_encontrados = glob.glob(patron_profesores)
                if archivos_encontrados:
                    raw_profesores = archivos_encontrados[0]
                    self.log_message(f"Archivo de profesores encontrado: {raw_profesores}")
                else:
                    messagebox.showerror("Error", f"No se encuentra el archivo: {raw_profesores}")
                    return

            self.log_message("Procesando horario de estudiantes...")
            self.dividir2(raw_estudiante, "estudiantes.html", ruta_salvado, estilo, "e", nombres_profesores, nombre_centro)
            self.log_message("Horario de estudiantes procesado correctamente")

            self.log_message("Procesando horario de profesores...")
            self.dividir2(raw_profesores, "profesores.html", ruta_salvado, estilo, "p", nombres_profesores, nombre_centro)
            self.log_message("Horario de profesores procesado correctamente")

            messagebox.showinfo("Éxito", "Horarios procesados correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar horarios: {str(e)}")
            self.log_message(f"ERROR: {str(e)}")

    def dividir2(self, archivo, nombre, ruta_salvado, nombre_css, tipo, nombres_profesores, nombre_centro):
        """Función principal de procesamiento de archivos"""
        try:
            with io.open(archivo, encoding='utf-8') as f:
                lineas = f.readlines()

            if tipo == 'p':
                for i, linea in enumerate(lineas):
                    if 'teacher line0' in linea:
                        for profesor in nombres_profesores:
                            if profesor in linea:
                                lineas[i] = lineas[i].replace(profesor, '').replace(
                                    f'<div class="teacher line0"><span class="t_9" onmouseover="highlight(\'t_9\')"></span>, <span class="t_19" onmouseover="highlight(\'t_19\')"></span></div>',
                                    '')

            g = ''.join(lineas)

            index = [idx for idx, s in enumerate(lineas) if 'Horario generado con ' in s]
            texto_generacion = lineas[index[0]] if index else ""

            if tipo == 'e':
                for profesor in nombres_profesores:
                    g = g.replace(profesor, '')

            g = g.replace('NORMAL', '').replace('SALIDA', '<BR>SALIDA').replace('TALLER', '<BR>TALLER')
            # Reemplaza CUALQUIER href que termine en _stylesheet.css por styles.css
            g = re.sub(r'href="[^"]*_stylesheet\.css"', 'href="styles.css"', g, flags=re.IGNORECASE)
            # Fallback por si el nombre no coincide con el patrón
            g = g.replace(nombre_css, 'styles.css')
            g = g.replace(r'<p class="back"><a href="#top">Volver al principio</a></p>', '')
            g = g.replace('</table>', '</table> salto777')
            g = g.replace(texto_generacion, '')
            g = g.replace(f'<caption>{nombre_centro}</caption>', '')

            reemplazos_hora = [
                # ("03:05", "03:05<br>04:00"),
                # ("02:50", "02:50<br>03:05"),
                ("3:05", "03:05<br>04:00"),
                ("2:50", "02:50<br>03:05"),
                ("01:55", "01:55<br>02:50"),
                ("01:00", "01:00<br>01:55"),
                ("03:15", "03:15<br>04:00"),
                ("02:30", "02:30<br>03:15"),
                ("02:15", "02:15<br>02:30"),
                ("01:30", "01:30<br>02:15"),
                ("14:45", "14:45<br>01:30"),
                ("12:45", "12:45<br>01:30"),
                ("11:45", "11:45<br>12:45"),
                ("11:00", "11:00<br>11:45"),
                ("10:15", "10:15<br>11:00"),
                ("09:45", "09:45<br>10:15"),
                ("09:00", "09:00<br>09:45"),
                ("08:15", "08:15<br>09:00"),
            ]

            for old, new in reemplazos_hora:
                g = g.replace(old, new)

            a = np.array(g.split('\n'))

            self.replace_brake(a, '9:45', 'RECREO')
            self.replace_brake(a, '2:50', 'RECESO')
            self.replace_brake(a, '11:45', 'ALMUERZO')
            self.replace_brake(a, '2:15', 'RECESO')
            self.replace_brake(a, '3:15', 'TALLER')

            j = [i for i, item in enumerate(a) if 'rowspan="2"' in item]
            k = [i for i, item in enumerate(a) if '<!-- span -->' in item]
            n = 0
            for m in j:
                if m - 1 >= 0 and a[m - 1] != '      <thead>':
                    a[m] = a[m].replace('rowspan="2"', '')
                    if n < len(k):
                        a[k[n]] = a[m]
                n = n + 1

            z = '\n'.join(a)

            archivo_guardar = os.path.join(ruta_salvado, nombre)
            os.makedirs(ruta_salvado, exist_ok=True)
            with open(archivo_guardar, 'w', encoding='utf-8') as text_file:
                text_file.write(z)

        except Exception as e:
            raise Exception(f"Error procesando {archivo}: {str(e)}")

    # ==================== FUNCIONES DE GESTIÓN XML ====================

    def obtener_datos_fet(self):
        """Obtener y validar los datos del archivo FET"""
        ruta_fet = self.ruta_fet.get()
        if not ruta_fet:
            messagebox.showerror("Error", "Seleccione un archivo FET")
            return None, None
        
        if not os.path.exists(ruta_fet):
            messagebox.showerror("Error", f"No se encuentra el archivo: {ruta_fet}")
            return None, None

        ruta_html = self.ruta_html_salida.get()
        if not ruta_html:
            ruta_html = os.path.dirname(ruta_fet)
            self.ruta_html_salida.set(ruta_html)
            self.ruta_html_salida_entry.delete(0, tk.END)
            self.ruta_html_salida_entry.insert(0, ruta_html)

        return ruta_fet, ruta_html

    def generar_carga_maestros(self):
        """Generar el HTML de carga de maestros"""
        ruta_fet, ruta_html = self.obtener_datos_fet()
        if not ruta_fet:
            return

        try:
            self.xml_log_message("Generando carga de maestros...")
            
            tree = ET.parse(ruta_fet)
            root = tree.getroot()

            teachers = {}
            for teacher in root.find(".//Teachers_List").findall(".//Teacher"):
                teachers[teacher[0].text] = []

            used_group_id = [0]
            for activity in root.findall(".//Activity"):
                group_id = int(activity.find(".//Activity_Group_Id").text)
                if group_id == 0 or group_id not in used_group_id:
                    used_group_id.append(group_id)
                    teacher_name = activity.find(".//Teacher").text
                    subject = activity.find(".//Subject").text
                    activity_tag = activity.find(".//Activity_Tag").text
                    students = activity.find(".//Students").text
                    total_duration = int(activity.find(".//Total_Duration").text)
                    teachers[teacher_name].append({
                        'subject': subject, 
                        'activity_tag': activity_tag, 
                        'students': students,
                        'total_duration': total_duration
                    })

            html = "<html>\n<head>\n"
            html += '<title>Liceo Ana Elpidia Sánchez</title>\n'
            html += '<link rel="stylesheet" media="all" href="estilo_carga_maestros.css" type="text/css" />\n'
            html += "</head>\n<body>\n"
            html += "<table>\n"
            html += "\t<tr>\n\t\t<th>Maestros</th>\n\t\t<th>Asignaturas</th>\n\t\t<th>Horas Totales</th>\n\t</tr>\n"

            for teacher, subjects in teachers.items():
                html += "\t<tr>\n"
                html += f"\t\t<td>{teacher}</td>\n"
                html += "\t\t<td>\n\t\t\t<ul>\n"
                horas = 0
                for subject in subjects:
                    horas += subject['total_duration']
                    subject_info = f"{subject['subject']}, {subject['activity_tag']}, {subject['students']}, {subject['total_duration']} horas"
                    html += f"\t\t\t\t<li>{subject_info}</li>\n"
                html += "\t\t\t</ul>\n\t\t</td>\n"
                html += f"\t\t<td>{horas} Horas</td>\n"
                html += "\t</tr>\n"

            html += "</table>\n</body>\n</html>"

            archivo_html = os.path.join(ruta_html, "carga_maestros.html")
            with open(archivo_html, "w", encoding='utf-8') as f:
                f.write(html)

            self.xml_log_message(f"✅ Carga de maestros generada en: {archivo_html}")
            messagebox.showinfo("Éxito", f"Archivo generado: {archivo_html}")
            
            # Abrir el archivo en el navegador
            webbrowser.open(archivo_html)

        except Exception as e:
            self.xml_log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error al generar carga de maestros: {str(e)}")

    def generar_restricciones_estudiantes(self):
        """Generar restricciones por estudiantes"""
        ruta_fet, ruta_html = self.obtener_datos_fet()
        if not ruta_fet:
            return

        try:
            self.xml_log_message("Generando restricciones por estudiantes...")
            
            tree = ET.parse(ruta_fet)
            root = tree.getroot()

            # Obtener todos los estudiantes
            all_students = []
            for subgroup in root.find(".//Students_List").findall(".//Subgroup"):
                all_students.append(subgroup[0].text)

            # Obtener actividades
            activities = {}
            for activity in root.findall(".//Activity"):
                teachers_list = []
                for teacher in activity.findall(".//Teacher"):
                    teachers_list.append(teacher.text)
                cantidad = len(teachers_list)
                activities[int(activity[6 + cantidad - 1].text)] = {
                    'activity_group_id': int(activity[7 + cantidad - 1].text),
                    'teachers': teachers_list,
                    'subject': activity[1 + cantidad - 1].text,
                    'students': activity[3 + cantidad - 1].text,
                    'activity_tag': activity[2 + cantidad - 1].text,
                    'duration': int(activity[4 + cantidad - 1].text),
                    'active': activity[8 + cantidad - 1].text
                }

            # Procesar restricciones
            restricciones_dict = {student: [] for student in all_students}
            
            for constraint in root.findall(".//ConstraintActivityPreferredStartingTimes"):
                activity_id = int(constraint[1].text)
                active = constraint[-2]
                
                if active.text == 'true':
                    activity_data = activities.get(activity_id)
                    if activity_data:
                        times = []
                        for preferred_starting_time in constraint.findall(".//Preferred_Starting_Time"):
                            times.append([preferred_starting_time[0].text, preferred_starting_time[1].text])
                        
                        dias_unicos = []
                        for horario_item in times:
                            dia = horario_item[0]
                            if dia not in dias_unicos:
                                dias_unicos.append(dia)
                        
                        clave_dias = 'O'
                        if set(['Lunes', 'Martes', 'Miércoles', 'Jueves']).issubset(dias_unicos):
                            if 'Viernes' not in dias_unicos:
                                clave_dias = 'L-J'
                            else:
                                clave_dias = 'L-V'
                        
                        restricciones_dict[activity_data['students']].append({
                            'subject': activity_data['subject'],
                            'teachers': activity_data['teachers'],
                            'duration': activity_data['duration'],
                            'clave_dias': clave_dias
                        })

            # Ordenar
            for student in all_students:
                restricciones_dict[student] = sorted(restricciones_dict[student], 
                                                      key=lambda x: (x['clave_dias'], x['subject']))

            # Generar HTML
            html = ""
            for student, materias in restricciones_dict.items():
                html += f'<h1>{student}</h1>\n'
                html += '<table border="1">\n'
                html += '<tr><th>Materia</th><th>Profesor</th><th>Duración</th><th>Días</th><th>Sum L-J</th><th>Sum L-V</th></tr>\n'
                sum_l_j = 0
                sum_l_v = 0

                for materia in materias:
                    teacher = ', '.join(materia["teachers"])
                    if materia["clave_dias"] == 'L-J':
                        sum_l_j += materia["duration"]
                    if materia["clave_dias"] == 'L-V':
                        sum_l_v += materia["duration"]
                    html += f'<tr><td>{materia["subject"]}</td><td>{teacher}</td><td>{materia["duration"]} horas</td>'
                    html += f'<td>{materia["clave_dias"]}</td><td>{sum_l_j}</td><td>{sum_l_v}</td></tr>\n'
                html += '</table>\n'

            archivo_html = os.path.join(ruta_html, "restricciones-estudiantes.html")
            with open(archivo_html, "w", encoding='utf-8') as f:
                f.write(html)

            self.xml_log_message(f"✅ Restricciones por estudiantes generadas en: {archivo_html}")
            messagebox.showinfo("Éxito", f"Archivo generado: {archivo_html}")
            webbrowser.open(archivo_html)

        except Exception as e:
            self.xml_log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error al generar restricciones: {str(e)}")

    def generar_restricciones_profesores(self):
        """Generar restricciones por profesores"""
        ruta_fet, ruta_html = self.obtener_datos_fet()
        if not ruta_fet:
            return

        try:
            self.xml_log_message("Generando restricciones por profesores...")
            
            tree = ET.parse(ruta_fet)
            root = tree.getroot()

            # Obtener todos los profesores
            all_teachers = []
            for teacher in root.find(".//Teachers_List").findall(".//Teacher"):
                all_teachers.append(teacher[0].text)

            # Obtener actividades
            activities = {}
            for activity in root.findall(".//Activity"):
                teachers_list = []
                for teacher in activity.findall(".//Teacher"):
                    teachers_list.append(teacher.text)
                cantidad = len(teachers_list)
                activities[int(activity[6 + cantidad - 1].text)] = {
                    'activity_group_id': int(activity[7 + cantidad - 1].text),
                    'teachers': teachers_list,
                    'subject': activity[1 + cantidad - 1].text,
                    'students': activity[3 + cantidad - 1].text,
                    'activity_tag': activity[2 + cantidad - 1].text,
                    'duration': int(activity[4 + cantidad - 1].text),
                    'active': activity[8 + cantidad - 1].text
                }

            # Procesar restricciones
            restricciones_dict = {teacher: [] for teacher in all_teachers}
            
            for constraint in root.findall(".//ConstraintActivityPreferredStartingTimes"):
                activity_id = int(constraint[1].text)
                active = constraint[-2]
                
                if active.text == 'true':
                    activity_data = activities.get(activity_id)
                    if activity_data:
                        times = []
                        for preferred_starting_time in constraint.findall(".//Preferred_Starting_Time"):
                            times.append([preferred_starting_time[0].text, preferred_starting_time[1].text])
                        
                        dias_unicos = []
                        for horario_item in times:
                            dia = horario_item[0]
                            if dia not in dias_unicos:
                                dias_unicos.append(dia)
                        
                        clave_dias = 'O'
                        if set(['Lunes', 'Martes', 'Miércoles', 'Jueves']).issubset(dias_unicos):
                            if 'Viernes' not in dias_unicos:
                                clave_dias = 'L-J'
                            else:
                                clave_dias = 'L-V'
                        
                        for teacher in activity_data['teachers']:
                            restricciones_dict[teacher].append({
                                'subject': activity_data['subject'],
                                'students': activity_data['students'],
                                'duration': activity_data['duration'],
                                'clave_dias': clave_dias
                            })

            # Ordenar
            for teacher in all_teachers:
                restricciones_dict[teacher] = sorted(restricciones_dict[teacher], 
                                                      key=lambda x: (x['clave_dias'], x['students']))

            # Generar HTML
            html = ""
            for teacher, materias in restricciones_dict.items():
                html += f'<h1>{teacher}</h1>\n'
                html += '<table border="1">\n'
                html += '<tr><th>Materia</th><th>Curso</th><th>Duración</th><th>Días</th><th>Sum L-J</th><th>Sum L-V</th></tr>\n'
                sum_l_j = 0
                sum_l_v = 0

                for materia in materias:
                    if materia["clave_dias"] == 'L-J':
                        sum_l_j += materia["duration"]
                    if materia["clave_dias"] == 'L-V':
                        sum_l_v += materia["duration"]
                    html += f'<tr><td>{materia["subject"]}</td><td>{materia["students"]}</td><td>{materia["duration"]} horas</td>'
                    html += f'<td>{materia["clave_dias"]}</td><td>{sum_l_j}</td><td>{sum_l_v}</td></tr>\n'
                html += '</table>\n'

            archivo_html = os.path.join(ruta_html, "restricciones-profesores.html")
            with open(archivo_html, "w", encoding='utf-8') as f:
                f.write(html)

            self.xml_log_message(f"✅ Restricciones por profesores generadas en: {archivo_html}")
            messagebox.showinfo("Éxito", f"Archivo generado: {archivo_html}")
            webbrowser.open(archivo_html)

        except Exception as e:
            self.xml_log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error al generar restricciones: {str(e)}")

    def generar_todas_restricciones(self):
        """Generar todas las restricciones"""
        self.generar_carga_maestros()
        self.generar_restricciones_estudiantes()
        self.generar_restricciones_profesores()
        self.xml_log_message("✅ Todas las restricciones generadas correctamente")
        messagebox.showinfo("Éxito", "Todas las restricciones generadas correctamente")

    def __del__(self):
        """Cerrar conexión a la base de datos"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = HorarioApp(root)
    root.mainloop()