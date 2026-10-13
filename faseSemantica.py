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
    
class AnalizadorSemantico:
    def __init__(self, raiz):
        self.original = raiz            # AST original (tab "Sintáctico")
        self.raiz = raiz.copiar()       # copia que se va a anotar (tab "Semántico")
        self.tabla = TablaSimbolos()
        self.errores = []

    def error(self, nodo, mensaje):
        if nodo is not None and nodo.lin is not None:
            pos = f"L{nodo.lin}:C{nodo.col}"
        else:
            pos = "L?:C?"
        self.errores.append(f"[Error semántico] {pos} -> {mensaje}")
 
    def analizar(self):
        if self.raiz is None:
            return
        for hijo in self.raiz.hijos:
            if hijo.tipo == "ListaDeclaracion":
                self.pasadaDeclaraciones(hijo)
        # 2do recorrido (sentencias): tipos de expresiones y sentencias (Kim y Rafa)

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