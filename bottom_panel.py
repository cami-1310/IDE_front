import tkinter as tk
from tkinter import ttk

# colores
TEMA_BG = '#1e1e1e'
TEMA_FG = '#d4d4d4'

class BottomPanel:
    def __init__(self, parent):
        self.parent = parent
        self.crear_panel()
        
    def crear_panel(self):
        """Crea el panel de tabs en la parte inferior de la ventana"""
        # Separador visual
        separator = ttk.Separator(self.parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=0, pady=0)
        
        # Frame para el panel de tabs
        self.tabs_frame = tk.Frame(self.parent, bg=TEMA_BG, height=200)
        self.tabs_frame.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM)
        self.tabs_frame.pack_propagate(False)
        
        # Crear el notebook (panel de tabs)
        self.tabs_notebook = ttk.Notebook(self.tabs_frame)
        self.tabs_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Crear los tabs
        self.tab_errores_lexicos = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                   wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_errores_sintacticos = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                  wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_errores_semanticos = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                   wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        self.tab_resultados = tk.Text(self.tabs_notebook, bg=TEMA_BG, fg=TEMA_FG, 
                                    wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        
        # Agregar los tabs al notebook
        self.tabs_notebook.add(self.tab_errores_lexicos, text="Errores Léxicos")
        self.tabs_notebook.add(self.tab_errores_sintacticos, text="Errores Sintácticos")
        self.tabs_notebook.add(self.tab_errores_semanticos, text="Errores Semánticos")
        self.tabs_notebook.add(self.tab_resultados, text="Resultados")
