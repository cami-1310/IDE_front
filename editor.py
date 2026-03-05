import tkinter as tk
from topMenu import TopMenu
from bottom_panel import BottomPanel
from right_panel import RightPanel

# colores
TEMA_BG = '#1e1e1e'
TEMA_FG = '#d4d4d4'
TEMA_LINES_BG = '#2d2d2d'
TEMA_LINES_FG = '#858585'
TEMA_CURSOR = '#ffffff'

class IDEEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IDE Editor")
        self.state('zoomed')
        self.configure(bg=TEMA_BG)
        self._debounce_id = None
        self._iniciar_componentes()
        self.menu=TopMenu(self, self.editor)
        
    def _iniciar_componentes(self):
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Crear sección superior con editor y panel derecho
        editor_section = tk.Frame(self.main_container)
        editor_section.pack(fill=tk.BOTH, expand=True)

        editor_frame = tk.Frame(editor_section)
        editor_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        self.numero_lineas = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0,
                                    background=TEMA_LINES_BG, state='disabled', foreground=TEMA_LINES_FG)
        self.numero_lineas.pack(side=tk.LEFT, fill=tk.Y)
        
        text_area = tk.Frame(editor_frame, background=TEMA_BG)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para contener el editor y scrollbars
        editor_scrollbar_frame = tk.Frame(text_area, background=TEMA_BG)
        editor_scrollbar_frame.pack(fill=tk.BOTH, expand=True)

        vscrollbar = tk.Scrollbar(editor_scrollbar_frame, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        hscrollbar = tk.Scrollbar(editor_scrollbar_frame, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # sincronizar scrollbar vertical
        def _on_editor_scroll(first, last):
            vscrollbar.set(first, last)
            self.numero_lineas.yview_moveto(first)
            return None

        self.editor = tk.Text(editor_scrollbar_frame, wrap=tk.NONE, undo=True, yscrollcommand=_on_editor_scroll, xscrollcommand=hscrollbar.set, background=TEMA_BG, foreground=TEMA_FG, insertbackground=TEMA_CURSOR)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=lambda *args: (self.editor.yview(*args), self.numero_lineas.yview(*args)))
        hscrollbar.config(command=self.editor.xview)
        
        # actualizar números de línea
        self.editor.bind('<MouseWheel>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-4>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-5>', lambda e: self._actualizar_lineas())
        self.editor.bind('<KeyRelease>', lambda e: self._actualizar_lineas())
        
        # actualizar barra de estado
        self.editor.bind('<KeyRelease>', lambda e: self._actualizar_barra_estado(), add='+')
        self.editor.bind('<ButtonRelease-1>', lambda e: self._actualizar_barra_estado(), add='+')
        self.editor.bind('<Motion>', lambda e: self._actualizar_barra_estado(), add='+')
        
        # actualizar números de línea al escribir / cambiar tamaño / soltar botón
        self.editor.bind('<Configure>', lambda e: self._actualizar_lineas())
        self.editor.bind('<ButtonRelease-1>', lambda e: self._actualizar_lineas())
        
        # Panel lateral derecho
        self.right_panel = RightPanel(editor_section)
    
        # Panel de tabs en la parte inferior
        self.bottom_panel = BottomPanel(self.main_container)
        
        # Barra de estado
        self._crear_barra_estado()
        
        self._actualizar_lineas()
        self._actualizar_barra_estado()
        
    def _crear_barra_estado(self):
        self.status_bar = tk.Frame(self.main_container, bg=TEMA_LINES_BG, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        # Label para mostrar información del cursor
        self.status_label = tk.Label(self.status_bar, text="Línea: 1, Columna: 1", 
                                   bg=TEMA_LINES_BG, fg=TEMA_FG, anchor='w', padx=10)
        self.status_label.pack(fill=tk.BOTH, expand=True)
        
    def _actualizar_barra_estado(self, event=None):
        try:
            # Obtener la posición del cursor
            cursor_pos = self.editor.index(tk.INSERT)
            linea, columna = cursor_pos.split('.')
            linea = int(linea)
            columna = int(columna) + 1  # Las columnas empiezan en 0, pero mostramos desde 1
            
            # Actualizar el label
            self.status_label.config(text=f"Línea: {linea}, Columna: {columna}")
        except Exception:
            self.status_label.config(text="Línea: 1, Columna: 1")
            
    def _actualizar_lineas(self, event=None):
        try:
            contador_lineas = int(self.editor.index('end-1c').split('.')[0])
        except Exception:
            contador_lineas = 1
        lineas_texto = "\n".join(str(i) for i in range(1, contador_lineas + 1))
        self.numero_lineas.config(state='normal')
        self.numero_lineas.delete('1.0', tk.END)
        self.numero_lineas.insert('1.0', lineas_texto)
        self.numero_lineas.config(state='disabled')
            
if __name__ == "__main__":
    IDEEditor().mainloop()