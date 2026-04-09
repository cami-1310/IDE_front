import tkinter as tk
from topMenu import TopMenu
from bottom_panel import BottomPanel
from right_panel import RightPanel
import threading
import time

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
        
        # Variables para el hilo de actualización
        self._actualizar_activo = True
        self._lineas_anteriores = 0
        self._linea_anterior = 0
        self._columna_anterior = 0
        
        self._iniciar_componentes()
        self.menu=TopMenu(self, self.editor, self.bottom_panel, self.right_panel)
        
        # Iniciar hilo de actualización continua
        self._hilo_actualizar = threading.Thread(target=self._hilo_actualizar_lineas, daemon=True)
        self._hilo_actualizar.start()
        
        # Cerrar el hilo cuando se cierre la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
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
        
        # Configurar etiqueta para resaltar la línea actual
        self.numero_lineas.tag_config('linea_actual', foreground='#ffffff', background='#404040')
        
        text_area = tk.Frame(editor_frame, background=TEMA_BG)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para el editor con scroll vertical
        editor_vscroll_frame = tk.Frame(text_area, background=TEMA_BG)
        editor_vscroll_frame.pack(fill=tk.BOTH, expand=True)

        vscrollbar = tk.Scrollbar(editor_vscroll_frame, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # sincronizar scrollbar vertical
        def _on_editor_scroll(first, last):
            vscrollbar.set(first, last)
            self.numero_lineas.yview_moveto(first)
            return None

        self.editor = tk.Text(editor_vscroll_frame, wrap=tk.NONE, undo=True, yscrollcommand=_on_editor_scroll, xscrollcommand=self._on_hscroll, background=TEMA_BG, foreground=TEMA_FG, insertbackground=TEMA_CURSOR)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=lambda *args: (self.editor.yview(*args), self.numero_lineas.yview(*args)))
        
        # Placeholder para scrollbar horizontal
        self.hscrollbar = None
        
        # Panel lateral derecho
        self.right_panel = RightPanel(editor_section)
        
        # Frame SEPARADO para el scrollbar horizontal (fuera del editor)
        hscrollbar_container = tk.Frame(self.main_container, background=TEMA_BG, height=15)
        hscrollbar_container.pack(fill=tk.X, side=tk.TOP)
        hscrollbar_container.pack_propagate(False)
        
        self.hscrollbar = tk.Scrollbar(hscrollbar_container, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(fill=tk.X, expand=True)
        self.hscrollbar.config(command=self.editor.xview)
        
        # actualizar números de línea
        self.editor.bind('<MouseWheel>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-4>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Button-5>', lambda e: self._actualizar_lineas())
        self.editor.bind('<KeyRelease>', lambda e: self._actualizar_lineas())
        self.editor.bind('<Key>', lambda e: self._actualizar_lineas())
    
        # Panel de tabs en la parte inferior
        self.bottom_panel = BottomPanel(self.main_container)
        
        # Barra de estado
        self._crear_barra_estado()
        
        self._actualizar_lineas()
        self._actualizar_barra_estado()
    
    def _on_hscroll(self, first, last):
        """Callback para el scrollbar horizontal"""
        if self.hscrollbar:
            self.hscrollbar.set(first, last)
        
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

        # Restaurar la posición de scroll para que coincida con el editor
        first, _ = self.editor.yview()
        self.numero_lineas.yview_moveto(first)

        # Resaltar la línea actual después de actualizar
        self._resaltar_linea_actual()
    
    def _resaltar_linea_actual(self):
        """Resalta solo la línea actual sin regenerar los números"""
        try:
            cursor_linea = int(self.editor.index(tk.INSERT).split('.')[0])
            
            # Remover resaltado anterior
            self.numero_lineas.tag_remove('linea_actual', '1.0', tk.END)
            
            # Aplicar resaltado a la línea actual
            linea_inicio = f'{cursor_linea}.0'
            linea_fin = f'{cursor_linea}.end'
            
            self.numero_lineas.config(state='normal')
            self.numero_lineas.tag_add('linea_actual', linea_inicio, linea_fin)
            self.numero_lineas.config(state='disabled')
        except Exception:
            pass
    
    def _hilo_actualizar_lineas(self):
        """Hilo que actualiza las líneas y la barra de estado continuamente"""
        while self._actualizar_activo:
            try:
                # Obtener información actual del editor
                contador_lineas = int(self.editor.index('end-1c').split('.')[0])
                cursor_pos = self.editor.index(tk.INSERT)
                cursor_linea, columna = cursor_pos.split('.')
                cursor_linea = int(cursor_linea)
                columna = int(columna) + 1
                
                # Si cambió el número de líneas, actualizar todo
                if self._lineas_anteriores != contador_lineas:
                    self._lineas_anteriores = contador_lineas
                    self.after(0, self._actualizar_lineas)
                
                # Si cambió la línea o columna del cursor
                if (self._linea_anterior != cursor_linea or 
                    self._columna_anterior != columna):
                    
                    self._linea_anterior = cursor_linea
                    self._columna_anterior = columna
                    
                    # Solo resaltar la línea y actualizar barra de estado
                    self.after(0, self._resaltar_linea_actual)
                    self.after(0, self._actualizar_barra_estado)
                    
            except Exception:
                pass
            
            # Pequeña pausa para no consumir CPU
            time.sleep(0.05)
    
    def _on_closing(self):
        """Detener el hilo y cerrar la aplicación"""
        self._actualizar_activo = False
        # Esperar a que el hilo termine
        if hasattr(self, '_hilo_actualizar'):
            self._hilo_actualizar.join(timeout=1)
        self.destroy()
            
if __name__ == "__main__":
    IDEEditor().mainloop()