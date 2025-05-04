import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime
import csv
from PIL import Image, ImageTk
import sys
import threading  # Importar threading para el Lock

# Crear un objeto Lock global
file_lock = threading.Lock()

class ModuloAdmision:
    def __init__(self):
        self.archivo_datos = 'datos_hospital.json'
        self.datos = self.cargar_datos()
        self.logo = None
        self.setup_ui()

    def cargar_datos(self):
        with file_lock:  # Bloquear acceso al archivo
            datos_base = {
                'especialidades': [
                    {'nombre': 'Traumatología', 'consultorio': 'Consultorio 1'},
                    {'nombre': 'Internista', 'consultorio': 'Consultorio 2'},
                    {'nombre': 'Cirugía', 'consultorio': 'Consultorio 3'},
                    {'nombre': 'Pediatría', 'consultorio': 'Consultorio 4'},
                    {'nombre': 'Ginecología', 'consultorio': 'Consultorio 5'},
                    {'nombre': 'Neurología', 'consultorio': 'Consultorio 6'},
                    {'nombre': 'Urólogo', 'consultorio': 'Consultorio 7'},
                    {'nombre': 'Cardiología', 'consultorio': 'Consultorio 8'},
                    {'nombre': 'Radiología', 'consultorio': 'Consultorio 9'},
                    {'nombre': 'Medicina', 'consultorio': 'Consultorio 10'},
                    {'nombre': 'Obstetricia 1', 'consultorio': 'Consultorio 11'},
                    {'nombre': 'Obstetricia 2', 'consultorio': 'Consultorio 12'},
                    {'nombre': 'Psicología', 'consultorio': 'Consultorio 13'},
                    {'nombre': 'Dental', 'consultorio': 'Consultorio 14'}
                ],
                'pacientes': {
                    "Consultorio 1" : [],
                    "Consultorio 2" : [],
                    "Consultorio 3" : [],
                    "Consultorio 4" : [],
                    "Consultorio 5" : [],
                    "Consultorio 6" : [],
                    "Consultorio 7" : [],
                    "Consultorio 8" : [],
                    "Consultorio 9" : [],
                    "Consultorio 10" : [],
                    "Consultorio 11" : [],
                    "Consultorio 12" : [],
                    "Consultorio 13" : [],
                    "Consultorio 14" : [],
                    
                    },
                'ultimo_llamado': None
            }

            try:
                if os.path.exists(self.archivo_datos):
                    with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                        self.validar_estructura_datos(datos, datos_base)
                        return datos
                else:
                    self.guardar_datos(datos_base)
                    return datos_base
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar los datos: {str(e)}")
                return datos_base

    def validar_estructura_datos(self, datos, datos_base):
        """Valida que la estructura de los datos esté completa, de lo contrario, la ajusta."""
        for key in datos_base:
            if key not in datos:
                datos[key] = datos_base[key]
        return datos

    def guardar_datos(self, datos=None):
        with file_lock:  # Bloquear acceso al archivo
            """Guarda los datos en un archivo JSON de manera segura."""
            if not datos:
                datos = self.datos
            try:
                with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar los datos: {str(e)}")
                return False

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Admisión - Hospital de Apoyo Palpa")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f8ff')

        # Frame para el logo centrado en la parte superior
        logo_frame = tk.Frame(self.root, bg='#f0f8ff')
        logo_frame.pack(pady=20)  # Añadir un poco de espacio arriba

        self.cargar_logo(logo_frame)

        # Frame principal
        main_frame = tk.Frame(self.root, padx=40, pady=40, bg='#f0f8ff')
        main_frame.pack(expand=True)  # Centra el frame en la ventana
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Título
        tk.Label(main_frame,
                 text="REGISTRO DE PACIENTES",
                 font=('Arial', 16, 'bold'),
                 bg='#f0f8ff',
                 fg='#0066cc').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Campos de registro
        self.dibujar_campos_registro(main_frame)

        # Crear el label para mostrar información
        self.info_label = tk.Label(main_frame, text="", font=('Arial', 12), fg='#009688', bg='#f0f8ff')
        self.info_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Frame para botones
        self.dibujar_botones(main_frame)

        # Configurar atajo de teclado
        self.root.bind('<Return>', lambda event: self.registrar_paciente())

    def cargar_logo(self, logo_frame):
        """Carga el logo del hospital de manera segura y lo coloca en la parte superior centrado."""
        try:
             # Usamos la ruta correcta dependiendo de si es un ejecutable o no
            if getattr(sys, 'frozen', False):
               # Si el archivo es un ejecutable, la ruta será relativa al ejecutable
               logo_path = os.path.join(sys._MEIPASS, 'logo_hospital.png')
            else:
               # Si estamos en desarrollo, usamos la ruta relativa al script
               logo_path = 'logo_hospital.png'
               
            image = Image.open(logo_path)
            image = image.resize((200, 200), Image.LANCZOS)  # Tamaño ajustado del logo
            self.logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(logo_frame, image=self.logo, bg='#f0f8ff')
            logo_label.pack()  # Alineado al centro
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            tk.Label(logo_frame,
                     text="HOSPITAL DE APOYO PALPA",
                     font=('Arial', 18, 'bold'),
                     bg='#f0f8ff',
                     fg='#0066cc').pack(pady=20)

    def dibujar_campos_registro(self, main_frame):
        """Dibuja los campos de registro de pacientes con estilo mejorado."""
        estilo_label = {'font': ('Arial', 12), 'padx': 5, 'pady': 5, 'bg': '#f0f8ff'}
        estilo_entry = {'font': ('Arial', 12), 'width': 40, 'bd': 2, 'relief': tk.SOLID, 'highlightthickness': 2}

        tk.Label(main_frame, text="Nombre del Paciente:", **estilo_label).grid(row=1, column=0, sticky='w')
        self.nombre_entry = tk.Entry(main_frame, **estilo_entry)
        self.nombre_entry.grid(row=1, column=1, pady=5, sticky='ew')
        self.nombre_entry.focus_set()

        tk.Label(main_frame, text="Especialidad Médica:", **estilo_label).grid(row=2, column=0, sticky='w')
        self.especialidad_var = tk.StringVar(self.root)
        self.especialidades = [esp['nombre'] for esp in self.datos['especialidades']]
        self.especialidad_menu = ttk.Combobox(main_frame, textvariable=self.especialidad_var,
                                               values=self.especialidades, state='readonly')
        self.especialidad_menu.config(font=('Arial', 12), width=38)
        self.especialidad_menu.grid(row=2, column=1, pady=5, sticky='ew')

        tk.Label(main_frame, text="Consultorio:", **estilo_label).grid(row=3, column=0, sticky='w')
        self.consultorio_var = tk.StringVar(self.root)
        self.todos_consultorios = [f'Consultorio {i}' for i in range(1, 15)]
        self.consultorio_menu = ttk.Combobox(main_frame,
                                              textvariable=self.consultorio_var,
                                              values=self.todos_consultorios,
                                              state='readonly')
        self.consultorio_menu.config(font=('Arial', 12), width=38)
        self.consultorio_menu.grid(row=3, column=1, pady=5, sticky='ew')

    def dibujar_botones(self, main_frame):
        """Dibuja los botones con un estilo atractivo."""
        btn_frame = tk.Frame(main_frame, bg='#f0f8ff')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        estilo_boton = {'font': ('Arial', 12), 'bd': 2, 'relief': tk.RAISED, 'padx': 10, 'pady': 5, 'width': 20}
        tk.Button(btn_frame, text="Registrar Paciente", command=self.registrar_paciente,
                  bg='#4CAF50', fg='white', **estilo_boton).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Ver Reporte", command=self.mostrar_reporte,
                  bg='#607D8B', fg='white', **estilo_boton).pack(side=tk.LEFT, padx=10)

    def registrar_paciente(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Debe ingresar el nombre del paciente", parent=self.root)
            return

        especialidad = self.especialidad_var.get()
        if not especialidad:
            messagebox.showerror("Error", "Debe seleccionar una especialidad", parent=self.root)
            return

        consultorio = self.consultorio_var.get()
        if not consultorio:
            messagebox.showerror("Error", "Debe seleccionar un consultorio", parent=self.root)
            return

        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            existe_paciente = any(
                p['nombre'].lower() == nombre.lower() and
                p['fecha_registro'].startswith(hoy) and
                not p['atendido']
                for p in self.datos['pacientes']
            )

            if existe_paciente:
                messagebox.showwarning("Advertencia", "Este paciente ya tiene un turno pendiente para hoy", parent=self.root)
                return

            nuevo_id = max([p['id'] for p in self.datos['pacientes']], default=0) + 1
            nuevo_paciente = {
                'id': nuevo_id,
                'nombre': nombre,
                'especialidad': especialidad,
                'consultorio': consultorio,
                'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'atendido': False
            }

            self.datos['pacientes'].append(nuevo_paciente)

            if self.guardar_datos():
                self.info_label.config(text=f"Paciente registrado con éxito. Turno: {nuevo_paciente['id']}")
                self.nombre_entry.delete(0, tk.END)
                self.mostrar_dialogo_ticket(nuevo_paciente)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}", parent=self.root)

    def mostrar_dialogo_ticket(self, paciente):
        """Muestra un diálogo con la información del paciente y un botón para imprimir el ticket."""
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Ticket de Registro")
        dialogo.geometry("500x400")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.grab_set()

        # Frame principal
        frame = tk.Frame(dialogo, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)

        # Logo en ticket
        try:
            image = Image.open("logo_hospital.png")
            image = image.resize((90, 90), Image.LANCZOS)
            logo_ticket = ImageTk.PhotoImage(image)
            tk.Label(frame, image=logo_ticket).pack(pady=10)
            dialogo.logo = logo_ticket  # Mantener referencia
        except:
            tk.Label(frame, text="HOSPITAL DE APOYO PALPA", font=('Arial', 14, 'italic')).pack()

        # Información del ticket
        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(info_frame, text=f"Turno: {paciente['id']}", font=('Arial', 12, 'bold')).pack(anchor='w')
        tk.Label(info_frame, text=f"Paciente: {paciente['nombre']}", font=('Arial', 12)).pack(anchor='w', pady=5)
        tk.Label(info_frame, text=f"Especialidad: {paciente['especialidad']}", font=('Arial', 12)).pack(anchor='w')
        tk.Label(info_frame, text=f"Consultorio: {paciente['consultorio']}", font=('Arial', 12)).pack(anchor='w', pady=5)
        tk.Label(info_frame, text=f"Fecha: {paciente['fecha_registro']}", font=('Arial', 10)).pack(anchor='w')

        # Botones
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Imprimir Ticket", command=lambda: self.imprimir_ticket(paciente, dialogo),
                 bg='#2196F3', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cerrar", command=dialogo.destroy,
                 bg='#f44336', fg='white', font=('Arial', 12)).pack(side=tk.RIGHT, padx=10)

    def imprimir_ticket(self, paciente, ventana):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar ticket como",
                parent=ventana
            )

            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=== HOSPITAL DE APOYO PALPA ===\n")
                    f.write("       TICKET DE REGISTRO\n\n")
                    f.write(f"Turno: {paciente['id']}\n")
                    f.write(f"Paciente: {paciente['nombre']}\n")
                    f.write(f"Especialidad: {paciente['especialidad']}\n")
                    f.write(f"Consultorio: {paciente['consultorio']}\n")
                    f.write(f"Fecha: {paciente['fecha_registro']}\n\n")
                    f.write("Presente este ticket en recepción\n")
                    f.write("=== Gracias por su visita ===\n")

                messagebox.showinfo("Éxito", f"Ticket guardado en:\n{filepath}", parent=ventana)
                ventana.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el ticket: {str(e)}", parent=ventana)

    def mostrar_reporte(self):
        # Ventana emergente para el reporte
        reporte = tk.Toplevel(self.root)
        reporte.title("Reporte de Pacientes")
        reporte.geometry("800x600")
        reporte.configure(bg='#f0f8ff')

        # Botón para exportar CSV
        btn_export = tk.Button(
           reporte,
           text="Exportar CSV",
           command=lambda: self.exportar_csv(self.datos.get('pacientes', [])),
           font=('Arial', 12),
           bg='#4CAF50',
           fg='white',
           padx=10,
           pady=5
        )
        btn_export.pack(pady=(10, 0))

        # Treeview con encabezados
        columnas = ("ID", "Nombre", "Especialidad", "Consultorio", "Fecha Registro", "Atendido", "Fecha Atención")
        tree = ttk.Treeview(reporte, columns=columnas, show="headings")
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor='w', width=120)
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(reporte, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

        # Carga de datos
        for p in self.datos.get('pacientes', []):
            tree.insert(
                "",
                tk.END,
                values=(
                    p.get("id", ""),
                    p.get("nombre", ""),
                    p.get("especialidad", ""),
                    p.get("consultorio", ""),
                    p.get("fecha_registro", ""),
                    "Sí" if p.get("atendido") else "No",
                    p.get("fecha_atencion", "")
                )
            )

        # Botón para cerrar la ventana
        tk.Button(
            reporte,
            text="Cerrar",
            command=reporte.destroy,
            font=('Arial', 12),
            bg='#f44336',
            fg='white',
            padx=10,
            pady=5
       ).pack(pady=(0,10))
        
    def exportar_csv(self, pacientes):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV","*.csv")],
            title="Guardar Reporte como CSV"
        )
        if not filepath:
           return

        try:
           with open(filepath, 'w', newline='', encoding='utf-8') as f:
               writer = csv.writer(f)
               # Cabecera
               writer.writerow([
                  "ID", "Nombre", "Especialidad",
                  "Consultorio", "Fecha Registro",
                  "Atendido", "Fecha Atención"
               ])
               # Filas
               for p in pacientes:
                   writer.writerow([
                       p.get("id", ""),
                       p.get("nombre", ""),
                       p.get("especialidad", ""),
                       p.get("consultorio", ""),
                       p.get("fecha_registro", ""),
                       "Sí" if p.get("atendido") else "No",
                       p.get("fecha_atencion", "")
                   ])
           messagebox.showinfo("Éxito", f"Reporte exportado a:\n{filepath}", parent=self.root)
        except Exception as e:
           messagebox.showerror("Error", f"No se pudo exportar CSV:\n{e}", parent=self.root)
           
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModuloAdmision()
    app.run()






