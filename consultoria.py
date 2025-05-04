import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import time
import threading  # Importar threading para el Lock
from datetime import datetime
import keyboard
from PIL import Image, ImageTk
import sys

# Crear un objeto Lock global
file_lock = threading.Lock()

class ModuloConsultorio:
    def __init__(self, consultorio_id):
        try:
            if not consultorio_id.isdigit() or not 1 <= int(consultorio_id) <= 14:
                raise ValueError("Número de consultorio inválido (debe ser 1-14)")

            self.consultorio_id = consultorio_id
            self.archivo_datos = 'datos_hospital.json'
            self.paciente_actual = None
            self.logo = None
            
            self.datos = self.cargar_datos()
            self.setup_ui()
            self.setup_hotkeys()
            self.actualizar_listas()
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("Error de Inicialización", f"No se pudo iniciar el módulo: {e}")
            raise

    def refresh_data(self):
        try:
            self.datos = self.cargar_datos()
            self.actualizar_listas()
        except Exception as e:
            print(f"Error al refrescar datos: {e}")
        finally:
            self.root.after(3000, self.refresh_data)

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
                'pacientes': [],
                'ultimo_llamado': None
            }
        
            if os.path.exists(self.archivo_datos):
                try:
                    with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return datos_base
            else:
                with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                    json.dump(datos_base, f, indent=4)
                return datos_base

    def guardar_datos(self):
        with file_lock:  # Bloquear acceso al archivo
            try:
                with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                    json.dump(self.datos, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar los datos: {e}")
                return False

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title(f"Consultorio {self.consultorio_id} - Hospital de Apoyo Palpa")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        # Frame para el logo y título
        header_frame = tk.Frame(self.root, bg='#f0f0f0')
        header_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Llamamos a la función para cargar el logo
        self.cargar_logo(header_frame)

        # Estado actual
        sf = tk.Frame(self.root, bd=2, relief=tk.GROOVE, padx=10, pady=10, bg='#ffffff')
        sf.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(sf, text="Estado actual:", font=('Arial', 12), bg='#ffffff').pack(side=tk.LEFT)
        self.status_label = tk.Label(sf, text="LIBRE", font=('Arial', 14, 'bold'), fg='green', bg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.paciente_label = tk.Label(sf, text="", font=('Arial', 12), bg='#ffffff')
        self.paciente_label.pack(side=tk.LEFT, expand=True)

        # Botones
        bf = tk.Frame(self.root, bg='#f0f0f0')
        bf.pack(pady=15)
        
        btn_llamar = tk.Button(bf, text="Llamar Siguiente (F2)", font=('Arial',12),
                             command=self.llamar_siguiente, bg='#4CAF50', fg='white',
                             width=20, padx=10)
        btn_llamar.pack(side=tk.LEFT, padx=5)
        
        btn_relamar = tk.Button(bf, text="Re-llamar Actual (F4)", font=('Arial',12),
                              command=self.re_llamar_paciente, bg='#2196F3', fg='white',
                              width=20, padx=10)
        btn_relamar.pack(side=tk.LEFT, padx=5)

        # Listas
        lf = tk.Frame(self.root, bg='#f0f0f0')
        lf.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Lista de espera
        wf = tk.Frame(lf, bd=2, relief=tk.GROOVE, bg='#ffffff')
        wf.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(wf, text="Pacientes en Espera", font=('Arial',12,'bold'), bg='#ffffff').pack(pady=5)
        
        self.wait_listbox = tk.Listbox(wf, font=('Arial',12), selectbackground='#e0e0e0')
        self.wait_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        
        scroll_wait = tk.Scrollbar(wf, orient="vertical", command=self.wait_listbox.yview)
        scroll_wait.pack(side=tk.RIGHT, fill=tk.Y)
        self.wait_listbox.config(yscrollcommand=scroll_wait.set)

        # Historial
        hf = tk.Frame(lf, bd=2, relief=tk.GROOVE, bg='#ffffff')
        hf.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(hf, text="Historial de Hoy", font=('Arial',12,'bold'), bg='#ffffff').pack(pady=5)
        
        self.hist_listbox = tk.Listbox(hf, font=('Arial',12), selectbackground='#e0e0e0')
        self.hist_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        
        scroll_hist = tk.Scrollbar(hf, orient="vertical", command=self.hist_listbox.yview)
        scroll_hist.pack(side=tk.RIGHT, fill=tk.Y)
        self.hist_listbox.config(yscrollcommand=scroll_hist.set)

    def cargar_logo(self, logo_frame):
        try:
            # Usamos la ruta correcta dependiendo de si es un ejecutable o no
            if getattr(sys, 'frozen', False):
               logo_path = os.path.join(sys._MEIPASS, 'logo_hospital.png')
            else:
               logo_path = 'logo_hospital.png'
        
            image = Image.open(logo_path)
            image = image.resize((200, 200), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(logo_frame, image=self.logo, bg='#f0f0f0')
            logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            tk.Label(logo_frame, 
                 text="HOSPITAL DE APOYO PALPA",
                 font=('Arial', 14),
                 bg='#f0f0f0').pack(side=tk.LEFT, padx=10)

    def setup_hotkeys(self):
        keyboard.add_hotkey('F2', self.llamar_siguiente)
        keyboard.add_hotkey('F4', self.re_llamar_paciente)

    def obtener_especialidad_consultorio(self):
        for esp in self.datos['especialidades']:
            if esp['consultorio'] == f"Consultorio {self.consultorio_id}":
                return esp['nombre']
        return None

    def obtener_pacientes_espera(self):
        esp = self.obtener_especialidad_consultorio()
        if not esp:
            return []
            
        hoy = datetime.now().strftime("%Y-%m-%d")
        pacientes = self.datos['pacientes'].get(f"Consultorio {self.consultorio_id}", [])
        lst = [p for p in pacientes if not p.get('atendido', False) and p['fecha_registro'].startswith(hoy)]
        #lst = [p for p in self.datos['pacientes']
               #if not p.get('atendido', False) #pacientes no atendidos
               #and p['consultorio'] == f"Consultorio {self.consultorio_id}" #consultorio actual
               #and p['fecha_registro'].startswith(hoy)] #pacientes registrados hoy
        lst.sort(key=lambda x: x['fecha_registro']) #ordena los pacientes por la fecha de registro
        return lst

    def obtener_historial_atencion(self):
        esp = self.obtener_especialidad_consultorio()
        if not esp:
            return []
            
        hoy = datetime.now().strftime("%Y-%m-%d")
        pacientes = self.datos['pacientes'].get(f"Consultorio {self.consultorio_id}", [])
        # Filtra los pacientes que han sido atendidos y que están en la especialidad y consultorio correctos
        lst = [p for p in pacientes if p.get('atendido', False) and p['fecha_registro'].startswith(hoy)]
        #lst = [p for p in self.datos['pacientes']
              #if p.get('atendido', False) #pacientes atendidos
              #and p['especialidad'] == esp #filtra por especialidad
              #and p['consultorio'] == f"Consultorio {self.consultorio_id}"  # Consultorio actual
              #and p['fecha_registro'].startswith(hoy)] #pacientes registrados hoy
        # Ordena los pacientes por la fecha de registro (descendente para ver los más recientes)
        lst.sort(key=lambda x: x['fecha_registro'], reverse=True)
        return lst[:20]

    def actualizar_listas(self):
        self.wait_listbox.delete(0, tk.END)
        self.hist_listbox.delete(0, tk.END)
        # Actualiza la lista de pacientes en espera
        espera = self.obtener_pacientes_espera()
        if espera:
            for p in espera:
                h = p['fecha_registro'].split(' ')[1][:5]  #solo muestra la hora
                self.wait_listbox.insert(tk.END, f"{p['id']}. {p['nombre']} ({h})")
        else:
            self.wait_listbox.insert(tk.END, "Sin pacientes en espera")
        # Actualiza el historial de pacientes atendidos
        hist = self.obtener_historial_atencion()
        if hist:
            for p in hist:
                h_reg = p['fecha_registro'].split(' ')[1][:5]
                h_aten = p['fecha_atencion'].split(' ')[1][:5] if 'fecha_atencion' in p else ''
                self.hist_listbox.insert(tk.END, f"{p['id']}. {p['nombre']} (Reg: {h_reg}, At: {h_aten})")
        else:
            self.hist_listbox.insert(tk.END, "Sin atenciones hoy")

    def llamar_siguiente(self):
        espera = self.obtener_pacientes_espera()
        if not espera:
            messagebox.showinfo("Info", "No hay pacientes en espera")
            return
           
        p = espera[0]
        for d in self.datos['pacientes'].get(f"Consultorio {self.consultorio_id}", []):
            if d['id'] == p['id']:
                d['atendido'] = True
                d['fecha_atencion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
                
        if self.guardar_datos():
            self.paciente_actual = p
            self.status_label.config(text="OCUPADO", fg='red')
            self.paciente_label.config(text=f"Paciente: {p['nombre']} (Turno {p['id']})")
            self.actualizar_listas() # Actualiza las listas después de llamar al paciente
            messagebox.showinfo("Paciente Llamado", f"Paciente {p['nombre']} está siendo atendido")

    def re_llamar_paciente(self):
        hist = self.obtener_historial_atencion()
        if hist:
            ultimo_paciente = hist[0]
            mensaje = f"RELLAMADO_Paciente {ultimo_paciente['nombre']}, favor pasar al consultorio {self.consultorio_id}"
            
            # Limpiar cualquier llamado anterior
            self.datos['ultimo_llamado'] = None
            self.guardar_datos()
            
            # Registrar nuevo llamado
            self.datos['ultimo_llamado'] = mensaje
            
            if self.guardar_datos():
                messagebox.showinfo("Re-llamar Paciente", 
                                  f"Paciente: {ultimo_paciente['nombre']}\nConsultorio: {self.consultorio_id}")
        else:
            messagebox.showinfo("Info", "No hay pacientes en el historial para re-llamar")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        keyboard.unhook_all_hotkeys()
        self.root.destroy()

if __name__ == "__main__":
    consultorio_id = simpledialog.askstring("Consultorio", "Ingrese el número de consultorio (1-14):")
    if consultorio_id:
        app = ModuloConsultorio(consultorio_id)
        app.run()
