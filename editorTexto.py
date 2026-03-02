import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

class EditorTexto:
    def __init__(self, root):
        self.root=root
        self.root.title("Editor de texto")
        self.root.geometry("800x600")

        self.ruta_archivo=None
        self.crear_textArea()
        self.crear_menu()

    def crear_textArea(self):
        frame=tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        #scroll
        scroll_y=tk.Scrollbar(frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        scroll_x=tk.Scrollbar(self.root, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        #text area
        self.texto=tk.Text(frame, 
                           wrap="none",
                           yscrollcommand=scroll_y.set,
                           xscrollcommand=scroll_x.set)
        
        #text crea un widget de texto multilinea
        self.texto.pack(side="left", fill="both", expand=True)
        #esto coloca el widget en la ventana, sus argumentos son
        #para otorgarle propiedades de posicion

        #conectar el text con los scrollbars
        scroll_y.config(command=self.texto.yview)
        scroll_x.config(command=self.texto.xview)


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
        self.root.title("Nuevo archivo")

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
            self.root.title(f"Editando - {ruta} ")

    def cerrarArchivo(self):
        #mensaje de si desea guardar
        resp=messagebox.askyesno("Cerrar", "¿Deseas guardar antes de cerrar?")
        if resp:
            self.guardarArchivo()
        
        self.texto.delete(1.0, tk.END)
        self.ruta_archivo=None
        self.root.title("Editor de texto")

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
        self.root.title({ruta})

    def cerrarArchivo(self):
        resp=messagebox.askyesno("Cerrar", "¿Deseas guardar antes de cerrar?")

        if resp:
            self.guardarArchivo()
        
        self.texto.delete(1.0, tk.END)
        self.ruta_archivo=None
        self.root.title("Editor de texto")

if __name__=="__main__":
    root=tk.Tk()
    app=EditorTexto(root)
    root.mainloop()