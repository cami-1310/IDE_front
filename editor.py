import tkinter as tk
from topMenu import TopMenu
from bottom_panel import BottomPanel
from right_panel import RightPanel
from getToken import Token, TokenType
import threading
import time

TEMA_BG = '#1e1e1e'
TEMA_FG = '#d4d4d4'
TEMA_LINES_BG = '#2d2d2d'
TEMA_LINES_FG = '#858585'
TEMA_CURSOR = '#ffffff'

COLOR_1   = '#4ec9b0'  # numeros         → verde menta
COLOR_2   = '#dcdcdc'  # identificadores → blanco suave
COLOR_3   = '#6a9955'  # comentarios     → verde olivo
COLOR_4   = '#569cd6'  # palabras reservadas → azul cielo
COLOR_5   = '#ce9178'  # op. aritmeticos → naranja
COLOR_6   = '#c586c0'  # op. relacionales y logicos → lila
COLOR_SIM = '#d4d4d4'  # simbolos y asignacion
COLOR_ERR = '#f44747'  # errores
# Cerca de tus constantes de colores
FUENTE_GENERAL = ('Consolas', 11)

PALABRAS_RESERVADAS = (
    TokenType.if_word, TokenType.else_word, TokenType.end_word,
    TokenType.do_word, TokenType.while_word, TokenType.switch_word,
    TokenType.case_word, TokenType.int_word, TokenType.float_word,
    TokenType.main_word, TokenType.cin_word, TokenType.cout_word,
)

TOKEN_COLORS = {
    TokenType.numero_entero:   COLOR_1,
    TokenType.numero_flotante: COLOR_1,

    TokenType.identificador:   COLOR_2,

    TokenType.comentario:      COLOR_3,

    TokenType.if_word:         COLOR_4,
    TokenType.else_word:       COLOR_4,
    TokenType.end_word:        COLOR_4,
    TokenType.do_word:         COLOR_4,
    TokenType.while_word:      COLOR_4,
    TokenType.switch_word:     COLOR_4,
    TokenType.case_word:       COLOR_4,
    TokenType.int_word:        COLOR_4,
    TokenType.float_word:      COLOR_4,
    TokenType.main_word:       COLOR_4,
    TokenType.cin_word:        COLOR_4,
    TokenType.cout_word:       COLOR_4,

    TokenType.suma:            COLOR_5,
    TokenType.resta:           COLOR_5,
    TokenType.multiplicacion:  COLOR_5,
    TokenType.division:        COLOR_5,
    TokenType.modulo:          COLOR_5,
    TokenType.potencia:        COLOR_5,
    TokenType.incremento:      COLOR_5,
    TokenType.decremento:      COLOR_5,

    TokenType.menorQue:        COLOR_6,
    TokenType.menorIgual:      COLOR_6,
    TokenType.mayorQue:        COLOR_6,
    TokenType.mayorIgual:      COLOR_6,
    TokenType.diferente:       COLOR_6,
    TokenType.igual:           COLOR_6,
    TokenType.opAnd:           COLOR_6,
    TokenType.opOr:            COLOR_6,
    TokenType.opNot:           COLOR_6,

    TokenType.parentesisDer:   COLOR_SIM,
    TokenType.parentesisIzq:   COLOR_SIM,
    TokenType.llaveDer:        COLOR_SIM,
    TokenType.llaveIzq:        COLOR_SIM,
    TokenType.coma:            COLOR_SIM,
    TokenType.puntoComa:       COLOR_SIM,
    TokenType.cadena:          COLOR_SIM,
    TokenType.caracter:        COLOR_SIM,
    TokenType.asignacion:      COLOR_SIM,

    TokenType.error:           COLOR_ERR,
}


class IDEEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IDE Editor")
        self.state('zoomed')
        self.configure(bg=TEMA_BG)
        self._debounce_id = None
        self._highlight_debounce = None

        self._actualizar_activo = True
        self._lineas_anteriores = 0
        self._linea_anterior = 0
        self._columna_anterior = 0

        self._iniciar_componentes()
        self.menu = TopMenu(self, self.editor, self.bottom_panel, self.right_panel)

        self.tokenizador = Token(self, self.editor, self.bottom_panel)
        self._registrar_tags_color()

        self._hilo_actualizar = threading.Thread(target=self._hilo_actualizar_lineas, daemon=True)
        self._hilo_actualizar.start()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _registrar_tags_color(self):
        for tipo, color in TOKEN_COLORS.items():
            kwargs = {'foreground': color}
            if tipo == TokenType.comentario:
                kwargs['font'] = ('Consolas', 11, 'italic')
            elif tipo in PALABRAS_RESERVADAS:
                kwargs['font'] = ('Consolas', 11, 'bold')
            if tipo == TokenType.error:
                kwargs['underline'] = True
            self.editor.tag_config(f'tok_{tipo.name}', **kwargs)

    def _resaltar_sintaxis(self, event=None):
        for tipo in TokenType:
            self.editor.tag_remove(f'tok_{tipo.name}', '1.0', tk.END)

        try:
            tokens = self.tokenizador.tokenizar_todo()
        except Exception:
            return

        for tok in tokens:
            col_inicio = tok.columna - 1
            col_fin    = col_inicio + len(tok.lexema)
            inicio = f'{tok.linea}.{col_inicio}'
            fin    = f'{tok.linea}.{col_fin}'
            try:
                self.editor.tag_add(f'tok_{tok.tipo.name}', inicio, fin)
            except Exception:
                pass

    def _resaltar_con_debounce(self, event=None):
        if self._highlight_debounce is not None:
            self.after_cancel(self._highlight_debounce)
        self._highlight_debounce = self.after(200, self._resaltar_sintaxis)

    def _iniciar_componentes(self):
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        editor_section = tk.Frame(self.main_container)
        editor_section.pack(fill=tk.BOTH, expand=True)

        editor_frame = tk.Frame(editor_section)
        editor_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.numero_lineas = tk.Text(
            editor_frame, width=4, padx=4, takefocus=0, border=0,
            background=TEMA_LINES_BG, state='disabled', foreground=TEMA_LINES_FG, font=FUENTE_GENERAL # <--- Usa la misma fuente que el editor
        )
        self.numero_lineas.pack(side=tk.LEFT, fill=tk.Y)
        self.numero_lineas.tag_config('linea_actual', foreground='#ffffff', background='#404040')

        text_area = tk.Frame(editor_frame, background=TEMA_BG)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        editor_vscroll_frame = tk.Frame(text_area, background=TEMA_BG)
        editor_vscroll_frame.pack(fill=tk.BOTH, expand=True)

        vscrollbar = tk.Scrollbar(editor_vscroll_frame, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_editor_scroll(first, last):
            vscrollbar.set(first, last)
            self.numero_lineas.yview_moveto(first)
            return None

        self.editor = tk.Text(
            editor_vscroll_frame, wrap=tk.NONE, undo=True,
            yscrollcommand=_on_editor_scroll,
            xscrollcommand=self._on_hscroll,
            background=TEMA_BG, foreground=TEMA_FG,
            insertbackground=TEMA_CURSOR,
            font=('Consolas', 11)
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=lambda *args: (
            self.editor.yview(*args),
            self.numero_lineas.yview(*args)
        ))

        self.hscrollbar = None

        self.right_panel = RightPanel(editor_section)

        hscrollbar_container = tk.Frame(self.main_container, background=TEMA_BG, height=15)
        hscrollbar_container.pack(fill=tk.X, side=tk.TOP)
        hscrollbar_container.pack_propagate(False)

        self.hscrollbar = tk.Scrollbar(hscrollbar_container, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(fill=tk.X, expand=True)
        self.hscrollbar.config(command=self.editor.xview)

        for event in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
            self.editor.bind(event, lambda e: self._actualizar_lineas())

        for event in ('<KeyRelease>', '<Key>'):
            self.editor.bind(event, lambda e: (
                self._actualizar_lineas(),
                self._resaltar_con_debounce()
            ))

        self.bottom_panel = BottomPanel(self.main_container)

        self._crear_barra_estado()
        self._actualizar_lineas()
        self._actualizar_barra_estado()

    def _on_hscroll(self, first, last):
        if self.hscrollbar:
            self.hscrollbar.set(first, last)

    def _crear_barra_estado(self):
        self.status_bar = tk.Frame(self.main_container, bg=TEMA_LINES_BG, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_bar, text="Línea: 1, Columna: 1",
            bg=TEMA_LINES_BG, fg=TEMA_FG, anchor='w', padx=10
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)

    def _actualizar_barra_estado(self, event=None):
        try:
            cursor_pos = self.editor.index(tk.INSERT)
            linea, columna = cursor_pos.split('.')
            linea   = int(linea)
            columna = int(columna) + 1
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

        first, _ = self.editor.yview()
        self.numero_lineas.yview_moveto(first)
        self._resaltar_linea_actual()

    def _resaltar_linea_actual(self):
        try:
            cursor_linea = int(self.editor.index(tk.INSERT).split('.')[0])
            self.numero_lineas.tag_remove('linea_actual', '1.0', tk.END)
            self.numero_lineas.config(state='normal')
            self.numero_lineas.tag_add(
                'linea_actual',
                f'{cursor_linea}.0',
                f'{cursor_linea}.end'
            )
            self.numero_lineas.config(state='disabled')
        except Exception:
            pass

    def _hilo_actualizar_lineas(self):
        while self._actualizar_activo:
            try:
                contador_lineas = int(self.editor.index('end-1c').split('.')[0])
                cursor_pos = self.editor.index(tk.INSERT)
                cursor_linea, columna = cursor_pos.split('.')
                cursor_linea = int(cursor_linea)
                columna      = int(columna) + 1

                if self._lineas_anteriores != contador_lineas:
                    self._lineas_anteriores = contador_lineas
                    self.after(0, self._actualizar_lineas)

                if (self._linea_anterior != cursor_linea or
                        self._columna_anterior != columna):
                    self._linea_anterior   = cursor_linea
                    self._columna_anterior = columna
                    self.after(0, self._resaltar_linea_actual)
                    self.after(0, self._actualizar_barra_estado)

            except Exception:
                pass

            time.sleep(0.05)

    def _on_closing(self):
        self._actualizar_activo = False
        if hasattr(self, '_hilo_actualizar'):
            self._hilo_actualizar.join(timeout=1)
        self.destroy()


if __name__ == "__main__":
    IDEEditor().mainloop()