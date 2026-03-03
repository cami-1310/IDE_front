import tkinter as tk
from tkinter import filedialog, messagebox

class TopMenu:
    def __init__(self, root, text_widget):
        self.root=root
        self.texto=text_widget
        self.ruta_archivo=None
        self.crear_menu()

    def crear_menu(self):
        barraMenu=tk.Menu(self.root)
        self.root.config(menu=barraMenu)

        menu_archivo=tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_archivo.add_command(label="Nuevo", command=self.nuevoArchivo)
        menu_archivo.add_command(label="Abrir", command=self.abrirArchivo)
        menu_archivo.add_command(label="Cerrar", command=self.cerrarArchivo)
        menu_archivo.add_command(label="Guardar", command=self.guardarArchivo)
        menu_archivo.add_command(label="Guardar como", command=self.guardarComo)
        menu_archivo.add_command(label="Salir", command=self.root.quit)

    #funciones del editor
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
            #se abre el archivo en modo lectura (r)
            #encoding utf-8 evita problemas con acentos
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido=archivo.read() #contenido guarda todo lo que se leyó del archivo
                self.texto.delete(1.0, tk.END) #se limpia el text area
                self.texto.insert(tk.END, contenido) #se inserta el contenido leido en el text area

            self.ruta_archivo=ruta #se guarda la ruta 

    def cerrarArchivo(self):
        #mensaje de si desea guardar
        resp=messagebox.askyesno("Cerrar", "¿Deseas guardar antes de cerrar?")
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