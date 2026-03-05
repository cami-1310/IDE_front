import tkinter as tk
from tkinter import filedialog, messagebox

class TopMenu:
    def __init__(self, root, text_widget):
        self.root=root
        self.texto=text_widget
        self.ruta_archivo=None
        self.crear_menu()
        self.crear_toolbar()

    def crear_menu(self):
        barraMenu=tk.Menu(self.root)
        self.root.config(menu=barraMenu)

        menu_archivo=tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_compilar=tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Compilar", menu=menu_compilar)

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

        btn_new=tk.Button(toolbar, text="📄", command=self.nuevoArchivo, font=("Arial", 12), bg='#1e1e1e', fg='#ffffff', activebackground='#2d2d2d', activeforeground='#ffffff', relief=tk.FLAT, padx=2, pady=2, highlightthickness=0, bd=0)
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)

        btn_open=tk.Button(toolbar, text="📂", command=self.abrirArchivo, font=("Arial", 12), bg='#1e1e1e', fg='#ffffff', activebackground='#2d2d2d', activeforeground='#ffffff', relief=tk.FLAT, padx=2, pady=2, highlightthickness=0, bd=0)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        btn_save=tk.Button(toolbar, text="💾", command=self.guardarArchivo, font=("Arial", 12), bg='#1e1e1e', fg='#ffffff', activebackground='#2d2d2d', activeforeground='#ffffff', relief=tk.FLAT, padx=2, pady=2, highlightthickness=0, bd=0)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        btn_out=tk.Button(toolbar, text="❌", command=self.cerrarArchivo, font=("Arial", 12), bg='#1e1e1e', fg='#ffffff', activebackground='#2d2d2d', activeforeground='#ffffff', relief=tk.FLAT, padx=2, pady=2, highlightthickness=0, bd=0)
        btn_out.pack(side=tk.LEFT, padx=2, pady=2)

        btn_compile=tk.Button(toolbar, text="▶️", command=self.llamarCompilador, font=("Arial", 12), bg='#1e1e1e', fg='#ffffff', activebackground='#2d2d2d', activeforeground='#ffffff', relief=tk.FLAT, padx=2, pady=2, highlightthickness=0, bd=0)
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
                self.texto.insert(tk.END, contenido) #se inserta el contenido leido en el text area
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
        resp=messagebox.askyesno("Cerrar", "¿Deseas guardar el archivo antes de cerrarlo?")
        if resp:
            self.guardarArchivo()
        
        self.texto.delete(1.0, tk.END)
        self.ruta_archivo=None

    def guardarArchivo(self):
        #si el archivo ya tiene una ruta
        if self.ruta_archivo:
            #se abre en modo escritura (w)
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto.get(1.0, tk.END)) #se escribe el archivo con el contenido del text area
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
                archivo.write(self.texto.get(1.0, tk.END))

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
        #por definir
        pass

    def mostrarAnalisisLexico(self):
        #por definir
        pass

    def mostrarAnalisisSintactico(self):
        #por definir
        pass

    def mostrarAnalisisSemantico(self):
        #por definir
        pass

    def mostrarCodigoIntermedio(self):
        #por definir
        pass