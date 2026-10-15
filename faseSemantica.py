class Simbolo:
    def __init__(self, nombre, tipo, linea_decl, offset):
        self.nombre = nombre
        self.tipo = tipo                  
        self.linea_decl = linea_decl
        self.lineas = [linea_decl]        # declaracion + usos
        self.offset = offset              # desplazamiento de memoria
        self.inicializada = False

class TablaSimbolos:
    # bytes que ocupa cada tipo (para calcular el desplazamiento)
    TAMANOS = {"int": 1, "float": 1, "bool": 1}

    def __init__(self):
        self.simbolos = {}                # diccionario: nombre -> Simbolo
        self.siguiente_offset = 0

    def declarar(self, nombre, tipo, linea):
        # inserta una variable. Devuelve False si ya estaba declarada
        if nombre in self.simbolos:
            return False
        self.simbolos[nombre] = Simbolo(nombre, tipo, linea, self.siguiente_offset)
        self.siguiente_offset += self.TAMANOS[tipo]
        return True

    def buscar(self, nombre):
        # devuelve el Simbolo, o None si no está declarada.
        return self.simbolos.get(nombre)

    def existe(self, nombre):
        return nombre in self.simbolos

    def tipo_de(self, nombre):
        s = self.buscar(nombre)
        return s.tipo if s else None

    def registrar_uso(self, nombre, linea):
        s = self.buscar(nombre)
        if s and linea is not None:
            s.lineas.append(linea)

    def marcar_inicializada(self, nombre):
        s = self.buscar(nombre)
        if s:
            s.inicializada = True

    def esta_inicializada(self, nombre):
        s = self.buscar(nombre)
        return s.inicializada if s else False

    def items(self):
        # simbolos en orden de declaracion (para mostrarlos en el IDE)
        return list(self.simbolos.values())

    def a_texto(self):
        filas = [f"{'Nombre':<10}{'Tipo':<8}{'Dirección':<11}Líneas"]
        for s in self.items():
            filas.append(f"{s.nombre:<10}{s.tipo:<8}{s.offset:<11}{', '.join(map(str, s.lineas))}")
        return "\n".join(filas)

##tabla simbolos#########################################3
NUMERICOS = ("int", "float")

# (operador, tipo_izq, tipo_der) -> tipo_resultado
# Cualquier combinación que no aparezca aquí es error.
REGLAS_BINARIAS = {
    # Suma
    ("+", "int", "int"): "int",     ("+", "int", "float"): "float",
    ("+", "float", "int"): "float", ("+", "float", "float"): "float",
    # Resta
    ("-", "int", "int"): "int",     ("-", "int", "float"): "float",
    ("-", "float", "int"): "float", ("-", "float", "float"): "float",
    # Multiplicación
    ("*", "int", "int"): "int",     ("*", "int", "float"): "float",
    ("*", "float", "int"): "float", ("*", "float", "float"): "float",
    # División (int/int se trunca)
    ("/", "int", "int"): "int",     ("/", "int", "float"): "float",
    ("/", "float", "int"): "float", ("/", "float", "float"): "float",
    # Módulo (solo enteros)
    ("%", "int", "int"): "int",
    # Potencia
    ("^", "int", "int"): "int",     ("^", "int", "float"): "float",
    ("^", "float", "int"): "float", ("^", "float", "float"): "float",
    # Relacionales (solo numéricos) -> bool
    ("<", "int", "int"): "bool",    ("<", "int", "float"): "bool",
    ("<", "float", "int"): "bool",  ("<", "float", "float"): "bool",
    ("<=", "int", "int"): "bool",   ("<=", "int", "float"): "bool",
    ("<=", "float", "int"): "bool", ("<=", "float", "float"): "bool",
    (">", "int", "int"): "bool",    (">", "int", "float"): "bool",
    (">", "float", "int"): "bool",  (">", "float", "float"): "bool",
    (">=", "int", "int"): "bool",   (">=", "int", "float"): "bool",
    (">=", "float", "int"): "bool", (">=", "float", "float"): "bool",
    # Igualdad (numéricos entre sí, o bool con bool) -> bool
    ("==", "int", "int"): "bool",   ("==", "int", "float"): "bool",
    ("==", "float", "int"): "bool", ("==", "float", "float"): "bool",
    ("==", "bool", "bool"): "bool",
    ("!=", "int", "int"): "bool",   ("!=", "int", "float"): "bool",
    ("!=", "float", "int"): "bool", ("!=", "float", "float"): "bool",
    ("!=", "bool", "bool"): "bool",
    # Lógicos (solo bool) -> bool
    ("&&", "bool", "bool"): "bool",
    ("||", "bool", "bool"): "bool",
}

# (operador, tipo_operando) -> tipo de resultado
REGLAS_UNARIAS = {
    ("!", "bool"): "bool",
    ("++", "int"): "int",     ("++", "float"): "float",
    ("--", "int"): "int",     ("--", "float"): "float",
}
    
class AnalizadorSemantico:
    def __init__(self, raiz):
        self.original = raiz            # AST original (tab "Sintáctico")
        self.raiz = raiz.copiar() if raiz is not None else None   # copia que se va a anotar (tab "Semántico")
        self.tabla = TablaSimbolos()
        self.errores = []

    def error(self, nodo, mensaje):
        if nodo is not None:
            nodo.conError = True        # el nodo causó un error (aunque su tipo sea válido)
        if nodo is not None and nodo.lin is not None:
            pos = f"L{nodo.lin}:C{nodo.col}"
            orden = (nodo.lin, nodo.col)
        else:
            pos = "L?:C?"
            orden = (float("inf"), 0)
        # se guarda la posición para ordenar al final del análisis
        self.errores.append((orden, f"[Error semántico] {pos} -> {mensaje}"))
 
    def analizar(self):
        if self.raiz is None:
            return
        for hijo in self.raiz.hijos:
            if hijo.tipo == "ListaDeclaracion":
                self.pasadaDeclaraciones(hijo)
        # 2do recorrido (sentencias): tipos de expresiones y sentencias
        for hijo in self.raiz.hijos:
            if hijo.tipo == "ListaSentencias":
                self.visitar_sentencias(hijo)
        # errores en el orden en que aparecen en el código
        self.errores.sort(key=lambda e: e[0])
        self.errores = [msg for _, msg in self.errores]

    # ── 2do recorrido: sentencias ─────────────────────────────────────────────────
    def visitar_sentencias(self, lista):
        if lista is None:
            return
        for s in lista.hijos:
            t = s.tipo
            if t == "Asignacion":
                self._asignacion(s)
            elif t == "Seleccion":
                self._seleccion(s)
            elif t == "Iteracion":
                self._iteracion(s)
            elif t == "Repeticion":
                self._repeticion(s)
            elif t == "sent_in":
                self._sent_in(s)
            elif t == "sent_out":
                self._sent_out(s)

    def _asignacion(self, nodo):
        if len(nodo.hijos) < 2:
            return
        nodo_id, expr = nodo.hijos[0], nodo.hijos[1]
        # primero se analiza la derecha, después se inicializa la izquierda
        te = self.tipar_expresion(expr)
        nombre = nodo_id.valor
        s = self.tabla.buscar(nombre)
        if s is None:                                   # error 1
            self.error(nodo_id, f"Identificador no declarado: '{nombre}'")
            nodo_id.tipoDato = "error"
            nodo.tipoDato = "error"
            return
        self.tabla.registrar_uso(nombre, nodo_id.lin)
        nodo_id.tipoDato = s.tipo
        self.tabla.marcar_inicializada(nombre)
        if te == "error":                               # sin errores en cascada
            nodo.tipoDato = "error"
            return
        if s.tipo == te:
            nodo.tipoDato = s.tipo
            nodo.valorCalc = expr.valorCalc
        elif s.tipo == "float" and te == "int":         # float = int se acepta
            self.convertir_a(expr, "float")
            nodo.tipoDato = "float"
            if expr.valorCalc is not None:
                nodo.valorCalc = float(expr.valorCalc)
        elif s.tipo == "int" and te == "float":         # error 4
            self.error(nodo, f"Conversión no válida: no se puede asignar un valor float a la variable int '{nombre}'")
            nodo.tipoDato = "error"
        else:                                           # error 3/6
            self.error(nodo, f"Incompatibilidad de tipos en asignación: '{nombre}' es {s.tipo} y la expresión es {te}")
            nodo.tipoDato = "error"

    def _condicion(self, nodo, cond, estructura):
        tc = self.tipar_expresion(cond)
        if tc not in ("bool", "error"):                 # error 7
            self.error(cond, f"La condición del {estructura} debe ser bool, pero es {tc}")
            nodo.tipoDato = "error"

    def _seleccion(self, nodo):
        if not nodo.hijos:
            return
        self._condicion(nodo, nodo.hijos[0], "if")
        for rama in nodo.hijos[1:]:                     # then / else
            for lista in rama.hijos:
                self.visitar_sentencias(lista)

    def _iteracion(self, nodo):
        if not nodo.hijos:
            return
        self._condicion(nodo, nodo.hijos[0], "while")
        if len(nodo.hijos) > 1:
            self.visitar_sentencias(nodo.hijos[1])

    def _repeticion(self, nodo):
        if not nodo.hijos:
            return
        # el cuerpo aparece antes que la condición en el texto
        self.visitar_sentencias(nodo.hijos[0])
        if len(nodo.hijos) > 1:
            self._condicion(nodo, nodo.hijos[1], "do-while")

    def _sent_in(self, nodo):
        if not nodo.hijos:
            return
        nodo_id = nodo.hijos[0]
        nombre = nodo_id.valor
        s = self.tabla.buscar(nombre)
        if s is None:                                   # error 1
            self.error(nodo_id, f"Identificador no declarado: '{nombre}'")
            nodo_id.tipoDato = "error"
            return
        self.tabla.registrar_uso(nombre, nodo_id.lin)
        nodo_id.tipoDato = s.tipo
        self.tabla.marcar_inicializada(nombre)

    def _sent_out(self, nodo):
        if not nodo.hijos:
            return
        for h in nodo.hijos[0].hijos:                   # hijos de Salida
            if h.tipo == "cadena":
                h.tipoDato = "cadena"
                continue
            t = self.tipar_expresion(h)
            if t not in ("int", "float", "bool", "error"):
                self.error(h, f"No se puede imprimir una expresión de tipo {t}")

    # ── 1er recorrido: declaraciones ──────────────────────────────────────────────
    def pasadaDeclaraciones(self, lista):
        for decl in lista.hijos:
            # para cada nodo "Declaracion"
            if len(decl.hijos) < 2:
                continue
            nodo_tipo, nodo_ids = decl.hijos[0], decl.hijos[1]
            dtype = nodo_tipo.valor                    
            if dtype not in TablaSimbolos.TAMANOS:
                continue
            # anotar: el tipo se hereda hacia Identificador y hacia cada id
            nodo_tipo.tipoDato = dtype
            nodo_ids.tipoDato = dtype
            for nodo_id in nodo_ids.hijos:
                nodo_id.tipoDato = dtype
                nombre = nodo_id.valor
                if not self.tabla.declarar(nombre, dtype, nodo_id.lin):
                    previo = self.tabla.buscar(nombre)
                    self.error(nodo_id,
                        f"La variable '{nombre}' ya fue declarada en la línea {previo.linea_decl}")
                    self.tabla.registrar_uso(nombre, nodo_id.lin)


    def tipar_expresion(self, nodo):
        """Anota tipoDato / valorCalc / conv y devuelve el tipoDato del nodo."""
        if nodo is None:
            return "error"
        if nodo.tipo == "numero":
            es_float = "." in nodo.valor
            nodo.tipoDato = "float" if es_float else "int"
            nodo.valorCalc = float(nodo.valor) if es_float else int(nodo.valor)
        elif nodo.tipo == "bool":
            nodo.tipoDato = "bool"
            nodo.valorCalc = (nodo.valor == "true")
        elif nodo.tipo == "id":
            self._tipar_id(nodo)
        elif nodo.tipo == "op":
            self._tipar_op(nodo)
        else:                       # nodo "error" del parser
            nodo.tipoDato = "error"
        return nodo.tipoDato

    def _tipar_id(self, nodo):
        nombre = nodo.valor
        s = self.tabla.buscar(nombre)
        if s is None:                                   #error 1
            self.error(nodo, f"Identificador no declarado: '{nombre}'")
            nodo.tipoDato = "error"
            return
        self.tabla.registrar_uso(nombre, nodo.lin)
        nodo.tipoDato = s.tipo
        if not s.inicializada:
            self.error(nodo, f"La variable '{nombre}' se usa antes de inicializarla")

    def _tipar_op(self, nodo):
        op = nodo.valor
        if len(nodo.hijos) == 1:
            return self._tipar_unario(nodo, op)
        izq, der = nodo.hijos
        ti = self.tipar_expresion(izq)
        td = self.tipar_expresion(der)
        if "error" in (ti, td):                         # sin errores en cascada
            nodo.tipoDato = "error"
            return
        res = REGLAS_BINARIAS.get((op, ti, td))
        if res is None:
            if op in ("==", "!="):                      # error 3
                self.error(nodo, f"Incompatibilidad de tipos: no se puede comparar '{ti}' con '{td}' usando '{op}'")
            else:                                       # error 5
                self.error(nodo, self._msg_operador(op, ti, td))
            nodo.tipoDato = "error"
            return
        if ti != td and ti in NUMERICOS and td in NUMERICOS:   # int mezclado con float
            self.convertir_a(izq if ti == "int" else der, "float")
        nodo.tipoDato = res
        nodo.valorCalc = self._plegar(nodo, op, izq, der, res)

    def _tipar_unario(self, nodo, op):
        t = self.tipar_expresion(nodo.hijos[0])
        if t == "error":
            nodo.tipoDato = "error"
            return
        res = REGLAS_UNARIAS.get((op, t))
        if res is None:                                 # error 5
            self.error(nodo, f"Operador '{op}' no aplica a {t}")
            nodo.tipoDato = "error"
            return
        nodo.tipoDato = res
        v = nodo.hijos[0].valorCalc
        if op == "!" and v is not None:
            nodo.valorCalc = (not v)

    def _msg_operador(self, op, ti, td):
        if op == "%":
            malo = "float" if "float" in (ti, td) else "bool"
        elif op in ("&&", "||"):
            malo = ti if ti != "bool" else td
        else:
            malo = "bool"
        return f"Operador '{op}' no aplica a {malo}"

    def convertir_a(self, nodo, destino):
        if nodo is not None and nodo.tipoDato == "int" and destino == "float":
            nodo.conv = "int→float"

    def _plegar(self, nodo, op, izq, der, res):
        # solo si los dos son constantes
        a, b = izq.valorCalc, der.valorCalc
        if op in ("/", "%") and b is not None and b == 0:
            self.error(nodo, "División entre cero")
            return None
        if a is None or b is None:
            return None
        try:
            if op == "+": r = a + b
            elif op == "-": r = a - b
            elif op == "*": r = a * b
            elif op == "/":
                if res == "int":                        # división con enteros truncada
                    q = abs(a) // abs(b)
                    r = q if (a < 0) == (b < 0) else -q
                else:
                    r = a / b
            elif op == "%":
                q = abs(a) // abs(b)
                q = q if (a < 0) == (b < 0) else -q
                r = a - b * q
            elif op == "^": r = a ** b
            elif op == "<": return a < b
            elif op == "<=": return a <= b
            elif op == ">": return a > b
            elif op == ">=": return a >= b
            elif op == "==": return a == b
            elif op == "!=": return a != b
            elif op == "&&": return a and b
            elif op == "||": return a or b
            else: return None
            if isinstance(r, complex):
                return None
            return int(r) if res == "int" else float(r)
        except (ZeroDivisionError, OverflowError, ValueError):
            return None