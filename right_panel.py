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
        self.tab_lexico = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                     wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_sintactico = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                     wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_semantico = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                 wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_hash_table = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                    wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_codigo_intermedio = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                    wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        
        # Agregar los tabs al notebook
        self.tabs_notebook.add(self.tab_lexico, text="Léxico")
        self.tabs_notebook.add(self.tab_sintactico, text="Sintáctico")
        self.tabs_notebook.add(self.tab_semantico, text="Semántico")
        self.tabs_notebook.add(self.tab_hash_table, text="Tabla de Hash")
        self.tabs_notebook.add(self.tab_codigo_intermedio, text="Código Intermedio")
