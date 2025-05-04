import tkinter as tk
from tkinter import font as tkfont
import json
import os
import time
import pygame
from datetime import datetime
from gtts import gTTS
import winsound
from PIL import Image, ImageTk
import threading  # Importar threading para el Lock

# Crear un objeto Lock global
file_lock = threading.Lock()

# Configuración de tamaños
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FONT_TITLE_SIZE = 28
FONT_LIST_SIZE = 26
LOGO_WIDTH = 800
LOGO_HEIGHT = 600

class SalaEspera:
    def __init__(self):
        # Inicializa audio
        pygame.mixer.quit()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Datos
        self.archivo =  'datos_hospital.json'
        self.datos = self._cargar_datos()
        self.ultimo_llamado = None
        self.logo = None

        # Ventana principal
        self.root = tk.Tk()
        self.root.title("Sala de Espera – Hospital de Apoyo Palpa")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(800, 600)
        self.root.configure(bg='#f0f0f0')

        # Proporción columnas: usando enteros para evitar TclError
        # Ratio aproximado 5.5:4.5 se convierte a 11:9
        self.root.grid_columnconfigure(0, weight=11)
        self.root.grid_columnconfigure(1, weight=9)
        self.root.grid_rowconfigure(0, weight=1)

        # Fuentes
        self.fuente_tit = tkfont.Font(family='Arial', size=FONT_TITLE_SIZE, weight='bold')
        self.fuente_lst = tkfont.Font(family='Arial', size=FONT_LIST_SIZE)

        self._setup_ui()
        self._cargar_listas()
        self._verificar_cambios()

    def _cargar_datos(self):
        with file_lock:  # Bloquear acceso al archivo
            base = {'especialidades': [], 'pacientes': [], 'ultimo_llamado': None}
            if os.path.exists(self.archivo):
                try:
                    with open(self.archivo, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return base
            else:
                with open(self.archivo, 'w', encoding='utf-8') as f:
                    json.dump(base, f, indent=4)
                return base

    def _setup_ui(self):
        # Columna Izquierda
        izq = tk.Frame(self.root, bg='black')
        izq.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        izq.grid_rowconfigure(0, weight=1)
        izq.grid_columnconfigure(0, weight=1)

        # Logo
        try:
            image = Image.open("logo_hospital.png")
            image = image.resize((LOGO_WIDTH, LOGO_HEIGHT), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(image)
            tk.Label(izq, image=self.logo, bg='black').grid(row=0, column=0, pady=(10,20))
        except:
            tk.Label(izq, text="HOSPITAL DE APOYO PALPA", font=('Arial', FONT_TITLE_SIZE, 'bold'), fg='white', bg='black').grid(row=0, column=0, pady=(10,20))

        # Reloj
        self.lbl_reloj = tk.Label(izq, font=('Arial', FONT_TITLE_SIZE), fg='white', bg='black')
        self.lbl_reloj.grid(row=1, column=0, pady=(0,5))
        self._update_clock()

        # Último atendido en pantalla Columna Izquierda
        self.lbl_last = tk.Label(izq, font=('Arial', FONT_LIST_SIZE + 5), fg='white', bg='black')
        self.lbl_last.grid(row=2, column=0, pady=(5,20))
        self.lbl_last.config(text="Último atendido: Ninguno")

        # Columna Derecha
        der = tk.Frame(self.root, bg='#f0f0f0')
        der.grid(row=0, column=1, sticky='nsew', padx=(0,5), pady=10)
        der.grid_rowconfigure(0, weight=7)
        der.grid_rowconfigure(1, weight=3)
        der.grid_columnconfigure(0, weight=1, minsize=400)

        # Panel EN ESPERA
        espera = tk.Frame(der, bg='#e6f3ff', bd=2, relief=tk.RAISED)
        espera.grid(row=0, column=0, sticky='nsew', pady=(0,3), padx=5)
        espera.grid_columnconfigure(0, weight=1)
        espera.grid_rowconfigure(1, weight=1)
        tk.Label(espera, text="EN ESPERA", font=self.fuente_tit, bg='#004a99', fg='white').grid(row=0, column=0, sticky='ew', pady=1)
        self.txt_espera = tk.Listbox(espera, font=self.fuente_lst, bg='#e6f3ff')
        self.txt_espera.grid(row=1, column=0, sticky='nsew')

        # Panel EN ATENCIÓN
        atencion = tk.Frame(der, bg='#ffe6e6', bd=2, relief=tk.RAISED)
        atencion.grid(row=1, column=0, sticky='nsew', pady=(3,0), padx=5)
        atencion.grid_columnconfigure(0, weight=1)
        atencion.grid_rowconfigure(1, weight=1)
        tk.Label(atencion, text="EN ATENCIÓN", font=self.fuente_tit, bg='#990000', fg='white').grid(row=0, column=0, sticky='ew', pady=1)
        self.txt_atencion = tk.Listbox(atencion, font=self.fuente_lst, bg='#ffe6e6')
        self.txt_atencion.grid(row=1, column=0, sticky='nsew')

    def _update_clock(self):
        self.lbl_reloj.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _cargar_listas(self):
        self.txt_espera.delete(0, tk.END)
        self.txt_atencion.delete(0, tk.END)

        espera = [p for p in self.datos['pacientes'] if not p.get('atendido')]
        espera.sort(key=lambda x: x['fecha_registro'])
        for p in espera:
            texto = f"{p['id']}. {p['nombre']} ({p['especialidad']})"
            self.txt_espera.insert(tk.END, texto)

        atend = [p for p in self.datos['pacientes'] if p.get('atendido')]
        atend.sort(key=lambda x: (x.get('fecha_atencion',''), x.get('id',0)), reverse=True)
        for p in atend:
            texto = f"{p['id']}. {p['nombre']} ({p['especialidad']})"
            self.txt_atencion.insert(tk.END, texto)

        # Actualizar último atendido
        if atend:
            ultimo = atend[0]
            self.lbl_last.config(text=f"En atención: {ultimo['id']}. {ultimo['nombre']} ({ultimo['especialidad']})")
        else:
            self.lbl_last.config(text="En atención: Ninguno")

        if not espera:
            self.txt_espera.insert(tk.END, "Sin pacientes en espera")
        if not atend:
            self.txt_atencion.insert(tk.END, "Sin pacientes en atención")

    def _verificar_cambios(self):
        nuevos_datos = self._cargar_datos()
        pygame.mixer.music.stop()

        if 'ultimo_llamado' in nuevos_datos and nuevos_datos['ultimo_llamado'] and nuevos_datos['ultimo_llamado'].startswith("RELLAMADO_"):
            mensaje = nuevos_datos['ultimo_llamado'].split('_',1)[1]
            nuevos_datos['ultimo_llamado']=None
            with open(self.archivo,'w',encoding='utf-8') as f:
                json.dump(nuevos_datos,f,indent=4)
            self._play_audio(mensaje)
            self.datos=nuevos_datos
            self._cargar_listas()
            self.root.after(3000,self._verificar_cambios)
            return

        atend = [p for p in nuevos_datos['pacientes'] if p.get('atendido')]
        if atend:
            ultimo = sorted(atend,key=lambda x:(x.get('fecha_atencion',''),x.get('id',0)),reverse=True)[0]
            if not self.ultimo_llamado or ultimo['id']!=self.ultimo_llamado['id']:
                self.ultimo_llamado=ultimo
                mensaje=f"Paciente {ultimo['nombre']}, favor dirigirse al {ultimo['consultorio']}"
                self._play_audio(mensaje)

        self.datos=nuevos_datos
        self._cargar_listas()
        self.root.after(3000,self._verificar_cambios)

    def _play_audio(self,texto):
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050,size=-16,channels=2,buffer=512)
            temp_file=f"temp_audio_{int(time.time())}.mp3"
            tts=gTTS(text=texto, lang='es', slow=False)
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            os.remove(temp_file)
        except:
            winsound.Beep(1000,500)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SalaEspera()
    app.run()





