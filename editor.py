import tkinter as tk

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
        self.geometry("900x700")
        self.configure(bg=TEMA_BG)
        self._debounce_id = None
        self._iniciar_componentes()
        
    def _iniciar_componentes(self):
        editor_frame = tk.Frame(self)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.numero_lineas = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0,
                                    background=TEMA_LINES_BG, state='disabled', foreground=TEMA_LINES_FG)
        self.numero_lineas.pack(side=tk.LEFT, fill=tk.Y)
        
        text_area = tk.Frame(editor_frame, background=TEMA_BG)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vscrollbar = tk.Scrollbar(text_area)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # sincronizar scrollbar
        def _on_editor_scroll(first, last):
            vscrollbar.set(first, last)
            self.numero_lineas.yview_moveto(first)
            return None

        self.editor = tk.Text(text_area, wrap=tk.NONE, undo=True, yscrollcommand=_on_editor_scroll, background=TEMA_BG, foreground=TEMA_FG, insertbackground=TEMA_CURSOR)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=lambda *args: (self.editor.yview(*args), self.numero_lineas.yview(*args)))
        
        # actualizar números de línea
        self.editor.bind('<MouseWheel>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-4>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-5>', lambda e: self._actualizar_lineas())
        self.editor.bind('<KeyRelease>', lambda e: self._actualizar_lineas())
        
        bar = tk.Frame(self, bg=TEMA_BG)
        bar.pack(fill=tk.X)
        
        # actualizar números de línea al escribir / cambiar tamaño / soltar botón
        self.editor.bind('<Configure>', lambda e: self._actualizar_lineas())
        self.editor.bind('<ButtonRelease-1>', lambda e: self._actualizar_lineas())
        self._actualizar_lineas()
        
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