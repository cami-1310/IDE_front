import tkinter as tk
from tkinter import filedialog, messagebox
import os
from getToken import Token, TokenType
from bottom_panel import BottomPanel

class TopMenu:
    def __init__(self, root, text_widget, bottom_panel=None, right_panel=None):
        self.root=root
        self.texto=text_widget
        self.bottom_panel=bottom_panel
        self.right_panel=right_panel
        self.ruta_archivo=None
        self.scanner=Token(self.root, self.texto, self.bottom_panel) #para poder llamar a getToken
        self.crear_menu()
        self.crear_toolbar()

    def crear_menu(self):
        barraMenu=tk.Menu(self.root)
        self.root.config(menu=barraMenu)

        menu_archivo=tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_compilar=tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Compilar", menu=menu_compilar)

        #iconos de acceso rapido
        self.icono_new=tk.PhotoImage(file="iconos/new_icon.png").subsample(20, 20)
        self.icono_open=tk.PhotoImage(file="iconos/open_icon.png").subsample(20, 20)
        self.icono_save=tk.PhotoImage(file="iconos/save_icon.png").subsample(20, 20)
        self.icono_out=tk.PhotoImage(file="iconos/out_icon.png").subsample(20, 20)
        self.icono_compile=tk.PhotoImage(file="iconos/compile_icon.png").subsample(20, 20)

        menu_archivo.add_command(label="Nuevo", command=self.nuevoArchivo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Abrir", command=self.abrirArchivo)
        menu_archivo.add_command(label="Cerrar", command=self.cerrarArchivo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Guardar", command=self.guardarArchivo)
        menu_archivo.add_command(label="Guardar como", command=self.guardarComo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salirIDE)

        menu_compilar.add_command(label="Compilar", command=self.llamarCompilador)
        menu_compilar.add_separator()
        menu_compilar.add_command(label="Análisis léxico", command=self.mostrarAnalisisLexico)
        menu_compilar.add_command(label="Análisis sintáctico", command=self.mostrarAnalisisSintactico)
        menu_compilar.add_command(label="Análisis semántico", command=self.mostrarAnalisisSemantico)
        menu_compilar.add_separator()
        menu_compilar.add_command(label="Generación de código intermedio", command=self.mostrarCodigoIntermedio)
     
    #toolbar para el acceso rapido con iconos
    def crear_toolbar(self):
        toolbar=tk.Frame(self.root, bd=0, bg='#1e1e1e', relief=tk.RAISED)

        btn_new=tk.Button(toolbar, image=self.icono_new, command=self.nuevoArchivo)
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)

        btn_open=tk.Button(toolbar, image=self.icono_open, command=self.abrirArchivo)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        btn_save=tk.Button(toolbar, image=self.icono_save, command=self.guardarArchivo)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        btn_out=tk.Button(toolbar, image=self.icono_out, command=self.cerrarArchivo)
        btn_out.pack(side=tk.LEFT, padx=2, pady=2)

        btn_compile=tk.Button(toolbar, image=self.icono_compile, command=self.llamarCompilador)
        btn_compile.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X, before=self.root.winfo_children()[0], padx=5, pady=5)

    #funciones del gestor de archivo
    def nuevoArchivo(self):
        #esto elimmina todo el contenido del text area
        #1.0 significa linea 1 caracter 0
        #tk.END significa hasta el final del texto
        self.texto.delete(1.0, tk.END)
        #la ruta debe estar vacia porque el archivo es nuevo y aun no se guarda en ningun lugar
        self.ruta_archivo=None

    def abrirArchivo(self):
        #esto abre el explorador de archivos del sistema
        ruta=filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Archivos Python", "*.py"),
                       ("Todos los archivos", "*.*")] 
            #filetypes limita los tipos de archivos
        )

        #si el usuario selecciono un archivo
        if ruta:
            #se abre el archivo en modo lectura
            try:
                contenido=self.leerArchivo(ruta) #contenido guarda todo lo que se leyó del archivo
                self.texto.delete(1.0, tk.END) #se limpia el text area
                self.texto.insert("end-1c", contenido) #se inserta el contenido leido en el text area
                self.texto.mark_set(tk.INSERT, "end-1c") #colocamos el cursor al final del texto
                self.ruta_archivo=ruta #se guarda la ruta 
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            except Exception as e:
                #para cualquier otro error con el archivo
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
                return

    def cerrarArchivo(self):
        #mensaje de si desea guardar
        resp=messagebox.askyesno("Cerrar", "¿Deseas guardar los cambios en el archivo antes de cerrarlo?")
        if resp:
            self.guardarArchivo()
        
        self.texto.delete(1.0, tk.END)
        self.ruta_archivo=None

    def guardarArchivo(self):
        #si el archivo ya tiene una ruta
        if self.ruta_archivo:
            #se abre en modo escritura (w)
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto.get(1.0, "end-1c")) #se escribe el archivo con el contenido del text area
        else: 
            #si no tiene ruta, hay que guardar como
            self.guardarComo()

    def guardarComo(self):
        ruta=filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Archivos Python", "*.py"),
                       ("Todos los archivos", "*.*")]
        )

        #si el usuario selecciona ubicacion
        if ruta:
            #se crea o sobreescribe el archivo
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto.get(1.0, "end-1c"))
            self.ruta_archivo=ruta #se guarda la nueva ruta

    def salirIDE(self):
        resp=messagebox.askyesnocancel("Salir", "¿Deseas guardar antes de salir?")
        if resp is True:
            self.guardarArchivo()
            self.root.quit()
        elif resp is False:
            self.root.quit()
        #si no elige ninguna es porque dio cancelar

    def leerArchivo(self, ruta):
        #intenta leer el archivo en base a varios encodings 
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(ruta, "r", encoding=enc) as archivo:
                    contenido=archivo.read()
                    return contenido
            except UnicodeDecodeError:
                continue
        #raise "sube" el error hasta el try catch de la funcion abrirArchivo
        raise ValueError("No se pudo determinar la codificación del archivo.")
    
    #funciones del menu de compilador
    def llamarCompilador(self):
        self.analizadorLexico()

    def mostrarAnalisisLexico(self):
        self.analizadorLexico()

    def mostrarAnalisisSintactico(self):
        #por definir
        pass

    def mostrarAnalisisSemantico(self):
        #por definir
        pass

    def mostrarCodigoIntermedio(self):
        #por definir
        pass

    #funcion para llamar al scanner (analizador lexico)
    #cuando se compile y en el analisis lexico
    def analizadorLexico(self):
        #limpiar seccion antes del analisis
        if(self.bottom_panel):
            self.bottom_panel.clean_errores_lexicos()
        if(self.right_panel):
            self.right_panel.clean_analisis_lexico()

        self.scanner.cargarCodigo()

        #construimos ruta para el archivo para guardar los tokens
        if(self.ruta_archivo):
            carpeta=os.path.dirname(self.ruta_archivo)
            nombre=os.path.splitext(os.path.basename(self.ruta_archivo))[0]
            ruta_tokens=os.path.join(carpeta, f"tokens_{nombre}.txt")
        else:
            #es porque no hay ruta, porque el archivo es nuevo, no se ha guardado nunca
            ruta_tokens="tokens_nuevo.txt"

        #escanear y guardar en el archivo
        with open(ruta_tokens, "w", encoding="utf-8") as archivo_tokens:
            while True:
                token=self.scanner.getToken()
                #print(token) #ver en consola
                archivo_tokens.write(str(token)+'\n') #mandando al archivo
                #enfile significa ya termino de ver el archivo, hay que salir del loop
                if(token.tipo==TokenType.endfile):
                    break
        
        #leer el archivo y mostrar en la seccion correspondiente
        if(self.right_panel):
            with open(ruta_tokens, "r", encoding="utf-8") as archivo_tokens:
                contenido=archivo_tokens.read()
            self.right_panel.mostrar_analisis_lexico(contenido)
            #cambiar al tab lexico automaticamente
            self.right_panel.tabs_notebook.select(self.right_panel.tab_lexico)