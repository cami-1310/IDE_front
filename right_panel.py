import tkinter as tk
from tkinter import ttk

# colores
TEMA_BG = '#1e1e1e'
TEMA_FG = '#d4d4d4'

class RightPanel:
    def __init__(self, parent):
        self.parent = parent
        self.crear_panel()
        
    def crear_panel(self):
        """Crea el panel lateral de tabs en el lado derecho"""
        # Separador visual
        separator = ttk.Separator(self.parent, orient='vertical')
        separator.pack(fill=tk.Y, padx=0, pady=0, side=tk.RIGHT)
        
        # Frame para el panel de tabs
        self.tabs_frame = tk.Frame(self.parent, bg=TEMA_BG, width=500)
        self.tabs_frame.pack(fill=tk.BOTH, expand=False, side=tk.RIGHT)
        self.tabs_frame.pack_propagate(False)
        
        # Crear el notebook (panel de tabs)
        self.tabs_notebook = ttk.Notebook(self.tabs_frame)
        self.tabs_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Crear los tabs
        # tab que mostrará el analisis lexico
        self.tab_lexico = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                     wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        
        # tab que mostrará el analisis sintactico
        self.frame_sintactico = tk.Frame(self.tabs_notebook, bg=TEMA_BG)
        # configuracion adicional para el TreeView que mostrará el AST
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Treeview",
            background=TEMA_BG,
            foreground=TEMA_FG,
            fieldbackground=TEMA_BG,
            borderwidth=0
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#264f78")],
            foreground=[("selected", "#ffffff")]
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=TEMA_BG,
            foreground=TEMA_FG
        )
        
        self.tab_sintactico = ttk.Treeview(self.frame_sintactico, style="Dark.Treeview", show="tree")
        self.tab_sintactico.column("#0", width=2000, stretch=False)
        scroll_sintactico = ttk.Scrollbar(
            self.frame_sintactico,
            orient="vertical",
            command=self.tab_sintactico.yview
        )
        scroll_sintactico_x = ttk.Scrollbar(
            self.frame_sintactico,
            orient="horizontal",
            command=self.tab_sintactico.xview
        )
        self.tab_sintactico.configure(yscrollcommand=scroll_sintactico.set, xscrollcommand=scroll_sintactico_x.set)
        scroll_sintactico_x.pack(side="bottom", fill="x")
        scroll_sintactico.pack(side="right", fill="y")
        self.tab_sintactico.pack(side="left", fill="both", expand=True)

        # tabs que aun no se implementan
        self.tab_semantico = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                 wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_hash_table = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                    wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_codigo_intermedio = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                    wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        
        # Agregar los tabs al notebook
        self.tabs_notebook.add(self.tab_lexico, text="Léxico")
        self.tabs_notebook.add(self.frame_sintactico, text="Sintáctico")
        self.tabs_notebook.add(self.tab_semantico, text="Semántico")
        self.tabs_notebook.add(self.tab_hash_table, text="Tabla de Hash")
        self.tabs_notebook.add(self.tab_codigo_intermedio, text="Código Intermedio")

    def mostrar_analisis_lexico(self, contenido):
        self.tab_lexico.config(state='normal')
        self.tab_lexico.delete('1.0', tk.END)
        self.tab_lexico.insert(tk.END, contenido)
        self.tab_lexico.config(state='disabled')
        self.tab_lexico.see('1.0')

    def clean_analisis_lexico(self):
        self.tab_lexico.config(state='normal')
        self.tab_lexico.delete('1.0', tk.END)
        self.tab_lexico.config(state='disabled')

    #funcion que mostrará el AST
    def mostrar_analisis_sintactico(self, raiz):
        self.tab_sintactico.delete(
            *self.tab_sintactico.get_children()
        )
        if raiz is not None:
            self.insertar_nodo_ast("", raiz)

    def clean_analisis_sintactico(self):
        self.tab_sintactico.delete(
            *self.tab_sintactico.get_children()
        )

    def insertar_nodo_ast(self, padre, nodo):
        texto = nodo.tipo
        if nodo.valor is not None:
            texto += f": {nodo.valor}"
        item = self.tab_sintactico.insert(
            padre,
            "end",
            text=texto,
            open=True
        )
        for hijo in nodo.hijos:
            self.insertar_nodo_ast(item, hijo)