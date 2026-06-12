import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from faseLexico import Token, TokenType, TokenResult
from faseSintaxis import Parser, NodoAST

class TopMenu:
    def __init__(self, root, text_widget, bottom_panel=None, right_panel=None):
        self.root = root
        self.texto = text_widget
        self.bottom_panel = bottom_panel
        self.right_panel = right_panel
        self.ruta_archivo = None
        self.scanner = Token(self.root, self.texto, self.bottom_panel)  # para poder llamar a getToken
        self.tokens = []
        self.parser = Parser(self.tokens)
        self.ruta_archivoTokens = None
        self.ruta_archivoErrores = None
        self.contenido_errores = ""
        self.contenido_tokens = ""
        self.crear_menu()
        self.crear_toolbar()

    def crear_menu(self):
        barraMenu = tk.Menu(self.root)
        self.root.config(menu=barraMenu)

        menu_archivo = tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_compilar = tk.Menu(barraMenu, tearoff=0)
        barraMenu.add_cascade(label="Acciones", menu=menu_compilar)

        # iconos de acceso rapido
        self.icono_new = tk.PhotoImage(file="iconos/new_icon.png").subsample(20, 20)
        self.icono_open = tk.PhotoImage(file="iconos/open_icon.png").subsample(20, 20)
        self.icono_save = tk.PhotoImage(file="iconos/save_icon.png").subsample(20, 20)
        self.icono_out = tk.PhotoImage(file="iconos/out_icon.png").subsample(20, 20)
        self.icono_compile = tk.PhotoImage(file="iconos/compile_icon.png").subsample(20, 20)

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

    # toolbar para el acceso rapido con iconos
    def crear_toolbar(self):
        toolbar = tk.Frame(self.root, bd=0, bg="#1e1e1e", relief=tk.RAISED)

        btn_new = tk.Button(toolbar, image=self.icono_new, command=self.nuevoArchivo)
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)

        btn_open = tk.Button(toolbar, image=self.icono_open, command=self.abrirArchivo)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        btn_save = tk.Button(toolbar, image=self.icono_save, command=self.guardarArchivo)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        btn_out = tk.Button(toolbar, image=self.icono_out, command=self.cerrarArchivo)
        btn_out.pack(side=tk.LEFT, padx=2, pady=2)

        btn_compile = tk.Button(toolbar, image=self.icono_compile, command=self.llamarCompilador)
        btn_compile.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X, before=self.root.winfo_children()[0], padx=5, pady=5)

    # funciones del gestor de archivos ----------------------------------------------------------------------------
    def nuevoArchivo(self):
        self.ruta_archivoTokens = None
        self.ruta_archivoErrores = None
        # esto elimmina todo el contenido del text area
        # 1.0 significa linea 1 caracter 0
        # tk.END significa hasta el final del texto
        self.texto.delete(1.0, tk.END)
        # la ruta debe estar vacia porque el archivo es nuevo y aun no se guarda en ningun lugar
        self.ruta_archivo = None
        # secciones vasias pues aun no se analiza nada
        self.limpiar_secciones()

    def abrirArchivo(self):
        # esto abre el explorador de archivos del sistema
        ruta = filedialog.askopenfilename(
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos Python", "*.py"),
                ("Todos los archivos", "*.*"),
            ]
            # filetypes limita los tipos de archivos
        )

        # si el usuario seleccionó un archivo
        if ruta:
            self.ruta_archivoTokens = None
            self.ruta_archivoErrores = None
            # se abre el archivo
            try:
                contenido = self.leerArchivo(ruta)  # contenido guarda todo lo que se leyó del archivo
                self.texto.delete(1.0, tk.END)  # se limpia el text area
                self.texto.insert("end-1c", contenido)  # se inserta el contenido leido en el text area
                self.texto.mark_set(tk.INSERT, "end-1c")  # colocamos el cursor al final del texto
                self.ruta_archivo = ruta  # se guarda la ruta
                
                # limpiar secciones
                self.limpiar_secciones()
                self.root.after(50, self.root._resaltar_sintaxis)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            except Exception as e:
                # para cualquier otro error con el archivo
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
                return

    def cerrarArchivo(self):
        # mensaje de si desea guardar
        resp = messagebox.askyesno("Cerrar", "¿Deseas guardar los cambios en el archivo antes de cerrarlo?")
        if resp:
            self.guardarArchivo()

        self.texto.delete(1.0, tk.END)
        self.ruta_archivo = None
        self.ruta_archivoTokens = None
        self.ruta_archivoErrores = None
        self.limpiar_secciones()

    def guardarArchivo(self):
        # si el archivo ya tiene una ruta
        if self.ruta_archivo:
            # se abre en modo escritura (w)
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto.get(1.0, "end-1c"))  # se escribe el archivo con el contenido del text area
        else:
            # si no tiene ruta, hay que guardar como
            self.guardarComo()

    def guardarComo(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos Python", "*.py"),
                ("Todos los archivos", "*.*"),
            ],
        )

        # si el usuario selecciona ubicacion
        if ruta:
            # se crea o sobreescribe el archivo
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto.get(1.0, "end-1c"))
            self.ruta_archivo = ruta  # se guarda la nueva ruta

    def leerArchivo(self, ruta):
        # intenta leer el archivo en base a varios encodings
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(ruta, "r", encoding=enc) as archivo:
                    contenido = archivo.read()
                    return contenido
            except UnicodeDecodeError:
                continue
        # raise "sube" el error hasta el try catch de la funcion abrirArchivo
        raise ValueError("No se pudo determinar la codificación del archivo.")
    
    def salirIDE(self):
        resp = messagebox.askyesnocancel("Salir", "¿Deseas guardar antes de salir?")
        if resp is True:
            self.guardarArchivo()
            self.root.quit()
        elif resp is False:
            self.root.quit()
        # si no elige ninguna es porque dio cancelar

    def limpiar_secciones(self):
        if self.bottom_panel:
            self.bottom_panel.clean_errores_lexicos()
            self.bottom_panel.clean_errores_sintacticos()
        if self.right_panel:
            self.right_panel.clean_analisis_lexico()
            self.right_panel.clean_analisis_sintactico()

    # funciones del menu de compilador ----------------------------------------------------------------------------
    def llamarCompilador(self):
        self.mostrarAnalisisLexico()
        self.mostrarAnalisisSintactico()

    def mostrarAnalisisLexico(self):
        # limpiar antes del analisis
        if self.bottom_panel:
            self.bottom_panel.clean_errores_lexicos()
        if self.right_panel:
            self.right_panel.clean_analisis_lexico()
        self.scanner.errores.clear()
        self.scanner.cargarCodigo()

        self.contenido_tokens = ""
        self.contenido_errores = ""

        # primero se trabaja en memoria
        while True:
            token = self.scanner.getToken()
            if token.tipo == TokenType.comentario:
                # si es un comentario, no se guarda
                pass
            elif token.tipo == TokenType.error:
                # si es un error, no se guarda
                pass
            elif token.tipo == TokenType.endfile:
                # enfile significa ya termino de ver el archivo, hay que salir del loop
                break
            else:
                # si llega aqui, es un token valido, entonces se guarda
                self.contenido_tokens += str(token) + "\n"

        self.contenido_errores += "******************* Errores léxicos *******************\n"
        # para el manejo de errores
        if self.scanner.errores:
            for error in self.scanner.errores:
                self.contenido_errores += str(error) + "\n"
        else:
            self.contenido_errores += "Sin errores léxicos.\n"

        # construimos ruta para los archivos que resultan del analisis
        # solo si el archivo tine ruta, es decir existe en el disco
        if self.ruta_archivo:
            carpeta = os.path.dirname(self.ruta_archivo)
            nombre = os.path.splitext(os.path.basename(self.ruta_archivo))[0]
            self.ruta_archivoTokens = os.path.join(carpeta, f"tokens_{nombre}.txt")
            self.ruta_archivoErrores = os.path.join(carpeta, f"errores_{nombre}.txt")

            # escanear y guardar en el archivo
            with open(self.ruta_archivoTokens, "w", encoding="utf-8") as archivo_tokens:
                archivo_tokens.write(self.contenido_tokens)

            # guardando los errores en el archivo correspondiente
            with open(self.ruta_archivoErrores, "w", encoding="utf-8") as archivo_errores:
                archivo_errores.write(self.contenido_errores)
        # si no hay ruta es porque el archivo no se ha guardado 
        # y entonces no es necesario guardar la información que arrojo el analisis

        # mostrar el análisis en la seccion correspondiente
        if self.right_panel:
            self.right_panel.mostrar_analisis_lexico(self.contenido_tokens)
            # cambiar al tab lexico automaticamente
            self.right_panel.tabs_notebook.select(self.right_panel.tab_lexico)

        # cambiar al tab de errores para que, si los hubo, mostrarlos
        if self.scanner.errores:
            for error in self.scanner.errores:
                if self.bottom_panel:
                    self.bottom_panel.add_error_lexico(error, 0)
            self.bottom_panel.tabs_notebook.select(
                self.bottom_panel.tab_errores_lexicos
            )
        else:
            if self.bottom_panel:
                self.bottom_panel.add_error_lexico("✔ Sin errores léxicos.", 1)
            self.bottom_panel.tabs_notebook.select(
                self.bottom_panel.tab_errores_lexicos
            )

    def mostrarAnalisisSintactico(self):
        # limpiar seccion antes del analisis
        if self.bottom_panel:
            self.bottom_panel.clean_errores_sintacticos()
        if self.right_panel:
            self.right_panel.clean_analisis_sintactico()
        
        # el analisis sintactico requiere de un archivo de tokens
        # esta informacion solo se genera si:
        # - el archivo ya existe en el disco
        # - ya se realizó el analisis lexico antes
        # entonces, existe el archivo de tokens
        # validamos de la siguiente manera:
        if not self.ruta_archivo:
            messagebox.showwarning(
                "Archivo sin guardar",
                "Debes guardar el archivo antes de ejecutar el análisis sintáctico."
            )
            self.guardarComo()
            return
        
        if not self.ruta_archivoTokens:
            messagebox.showwarning(
                "Análisis léxico requerido",
                "Primero debes ejecutar el análisis léxico."
            )
            return
        
        if not os.path.exists(self.ruta_archivoTokens):
            messagebox.showwarning(
                "Archivo de tokens no encontrado",
                "Ejecuta nuevamente el análisis léxico."
            )
            return
        
        # leer los tokens
        self.tokens = self.cargarTokens(self.ruta_archivoTokens)
        self.parser = Parser(self.tokens)
        self.parser.programa()

        self.contenido_errores += "\n******************* Errores sintácticos *******************\n"
        # para el manejo de errores
        if self.parser.errores:
            for error in self.parser.errores:
                self.contenido_errores += str(error) + "\n"
        else:
            self.contenido_errores += "Sin errores sintácticos.\n"

        # tras recuperar los errores, se guardan en el archivo de errores
        # que ya se habia creado con anterioridad y donde ya exisen los errores lexicos
        # solo si el archivo tine ruta, es decir existe en el disco
        if self.ruta_archivoErrores:
            # guardando los errores en el archivo correspondiente
            with open(self.ruta_archivoErrores, "w", encoding="utf-8") as archivo_errores:
                archivo_errores.write(self.contenido_errores)
        # si no hay ruta es porque el archivo no se ha guardado 
        # y entonces no es necesario guardar la información que arrojo el analisis

        # mostrar el análisis en la seccion correspondiente
        if self.right_panel:
            self.right_panel.mostrar_analisis_sintactico(self.parser.raiz)
            # cambiar al tab sintactico automaticamente
            self.right_panel.tabs_notebook.select(self.right_panel.frame_sintactico)

        # cambiar al tab de errores para que, si los hubo, mostrarlos
        if self.parser.errores:
            for error in self.parser.errores:
                if self.bottom_panel:
                    self.bottom_panel.add_error_sintactico(error, 0)
            self.bottom_panel.tabs_notebook.select(
                self.bottom_panel.tab_errores_sintacticos
            )
        else:
            if self.bottom_panel:
                self.bottom_panel.add_error_sintactico("✔ Sin errores sintácticos.", 1)
            self.bottom_panel.tabs_notebook.select(
                self.bottom_panel.tab_errores_sintacticos
            )

    def mostrarAnalisisSemantico(self):
        # por definir
        pass

    def mostrarCodigoIntermedio(self):
        # por definir
        pass

    def cargarTokens(self, ruta):
        contenido = self.leerArchivo(ruta)
        tokens = []
        patron = r"Token\((.*?), '(.*?)', L(\d+):C(\d+)\)"

        for linea in contenido.splitlines():
            linea = linea.strip()

            if not linea:
                continue

            match = re.match(patron, linea)

            if not match:
                continue

            tipo_str, lexema, linea_num, columna = match.groups()
            tipo = getattr(TokenType, tipo_str)
            token = TokenResult(
                tipo,
                lexema,
                int(linea_num),
                int(columna),
                0
            )
            tokens.append(token)
        # se agrega el EOF para algunos ciclos del analisis sintactico
        if tokens:
            ultimo=tokens[-1]
            tokens.append(
                TokenResult(
                    TokenType.endfile,
                    "",
                    ultimo.linea,
                    ultimo.columna,
                    0
                )
            )
        else:
            tokens.append(
                TokenResult(
                    TokenType.endfile,
                    "",
                    1,
                    1,
                    0
                )
            )
        return tokens