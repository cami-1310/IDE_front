from faseLexico import TokenType

class NodoAST:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def agregar(self, hijo):
        if hijo is not None:
            self.hijos.append(hijo)

TOKEN_NAMES = {
    TokenType.endfile: "end of file",
    TokenType.error: "error léxico",
    TokenType.if_word: "if",
    TokenType.else_word: "else",
    TokenType.end_word: "end",
    TokenType.do_word: "do",
    TokenType.while_word: "while",
    TokenType.then_word: "then",
    TokenType.int_word: "int",
    TokenType.float_word: "float",
    TokenType.bool_word: "bool",
    TokenType.bool_value: "valor booleano",
    TokenType.main_word: "main",
    TokenType.cin_word: "cin",
    TokenType.cout_word: "cout",
    TokenType.identificador: "identificador",
    TokenType.numero_entero: "número entero",
    TokenType.numero_flotante: "número flotante",
    TokenType.cadena: "cadena",
    TokenType.caracter: "carácter",
    TokenType.suma: "+",
    TokenType.resta: "-",
    TokenType.multiplicacion: "*",
    TokenType.division: "/",
    TokenType.modulo: "%",
    TokenType.potencia: "^",
    TokenType.incremento: "++",
    TokenType.decremento: "--",
    TokenType.menorQue: "<",
    TokenType.menorIgual: "<=",
    TokenType.mayorQue: ">",
    TokenType.mayorIgual: ">=",
    TokenType.diferente: "!=",
    TokenType.igual: "==",
    TokenType.opAnd: "&&",
    TokenType.opOr: "||",
    TokenType.opNot: "!",
    TokenType.opIn: ">>",
    TokenType.opOut: "<<",
    TokenType.parentesisDer: ")",
    TokenType.parentesisIzq: "(",
    TokenType.llaveDer: "}",
    TokenType.llaveIzq: "{",
    TokenType.coma: ",",
    TokenType.puntoComa: ";",
    TokenType.asignacion: "=",
    TokenType.comentario: "comentario"
}

class Parser:
    def __init__(self, tokens):
        self.errores=[]
        self.tokens = tokens
        self.pos = 0
        self.errorExp = False
        self.raiz = None

    def token_actual(self):
        #hay que leer el archivo de tokens y conservar el actual
        if(self.pos < len(self.tokens)):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def errorSintactico(self, tok, tipo, msj):
        mensaje = f"[Error sintáctico] L{tok.linea}:C{tok.columna} -> "
        if(msj!="1"):
            mensaje+=f"{msj}"
        else:
            esperado=TOKEN_NAMES.get(tipo, tipo.name)
            encontrado=TOKEN_NAMES.get(tok.tipo, tok.lexema)
            mensaje+=f"Se esperaba '{esperado}' pero se encontró '{encontrado}'"
        self.errores.append(mensaje)

    def es(self, tipo):
        return self.token_actual().tipo == tipo

    def esTipo(self):
        return (self.es(TokenType.int_word) or
                self.es(TokenType.float_word) or
                self.es(TokenType.bool_word))
    
    def consumir(self, tipo):
        tok = self.token_actual()
        if(tok.tipo == tipo):
            self.pos += 1
            return True
        
        #se encontró algo que no se esperaba
        self.errorSintactico(tok, tipo, "1")
        return False #si hubo fallo
    
    def sincronizar(self):
        # Tokens que indican un punto seguro de recuperación
        seguros = {
            TokenType.puntoComa,
            TokenType.end_word,
            TokenType.else_word,
            TokenType.llaveDer,
            TokenType.endfile
        }
        #avanzar hasta encontrar un punto seguro
        while not self.es(TokenType.endfile):
            if self.token_actual().tipo in seguros:
                if self.token_actual().tipo == TokenType.puntoComa:
                    self.pos += 1
                return
            self.pos += 1

    # ── Reglas ────────────────────────────────────────────────────────────────
    def programa(self):
        nodo = NodoAST("Programa")
        self.raiz = nodo
        if not self.consumir(TokenType.main_word):
            return nodo
        if not self.consumir(TokenType.llaveIzq):
            return nodo
        nodo.agregar(self.listaDeclaracion())
        nodo.agregar(self.listaSentencias())
        if not self.consumir(TokenType.llaveDer):
            return nodo
        if not self.es(TokenType.endfile):
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Se esperaba fin de archivo pero se encontró '{tok.lexema}'")
        return nodo

    def listaDeclaracion(self):
        nodo = NodoAST("ListaDeclaracion")
        while self.esTipo():
            nodo.agregar(self.declaracionVariable())
        return nodo
    
    def listaSentencias(self, en_do=False):
        nodo = NodoAST("ListaSentencias")
        tokens_fin = {
            TokenType.llaveDer,
            TokenType.end_word,
            TokenType.else_word,
            TokenType.endfile
        }
        while self.token_actual().tipo not in tokens_fin:
            if en_do and self.es(TokenType.while_word) and self.esCierreDelDo():
                break
            if self.esTipo():
                # declaración fuera de lugar: se reporta y se analiza para recuperarse
                tok = self.token_actual()
                self.errorSintactico(tok, None,
                    "Las declaraciones solo pueden aparecer al inicio del programa, antes de las sentencias")
                self.declaracionVariable()
                continue
            nodo.agregar(self.sentencia())
        return nodo

    def declaracionVariable(self):
        nodo = NodoAST("Declaracion")
        nodo.agregar(self.tipo())
        if not self.es(TokenType.identificador):
            tok = self.token_actual()
            self.errorSintactico(tok, TokenType.identificador, "1")
            self.sincronizar()
            return nodo
        nodo.agregar(self.identificador())
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def sentencia(self):
        if self.es(TokenType.if_word):
            return self.seleccion()
        elif self.es(TokenType.while_word):
            return self.iteracion()
        elif self.es(TokenType.do_word):
            return self.repeticion()
        elif self.es(TokenType.cin_word):
            return self.sentIn()
        elif self.es(TokenType.cout_word):
            return self.sentOut()
        elif self.es(TokenType.identificador):
            return self.asignacion()
        else: 
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Sentencia inesperada: '{tok.lexema}'")
            self.pos += 1
            return None

    def tipo(self):
        if(self.es(TokenType.int_word)):
            self.consumir(TokenType.int_word)
            return NodoAST("Tipo", "int")
        elif(self.es(TokenType.float_word)):
            self.consumir(TokenType.float_word)
            return NodoAST("Tipo", "float")
        elif(self.es(TokenType.bool_word)):
            self.consumir(TokenType.bool_word)
            return NodoAST("Tipo", "bool")
        else:
            tok = self.token_actual()
            self.errorSintactico(tok, None, "Se esperaba un tipo (int, float, bool)")
            self.pos += 1
            return NodoAST("tipo", "?")

    def identificador(self):
        nodo = NodoAST("Identificador")
        tok = self.token_actual()
        if self.consumir(TokenType.identificador):
            nodo.agregar(NodoAST("id", tok.lexema))
        while(self.es(TokenType.coma)):
            self.consumir(TokenType.coma)
            tok = self.token_actual()
            if self.consumir(TokenType.identificador):
                nodo.agregar(NodoAST("id", tok.lexema))
        return nodo

    def seleccion(self):
        nodo = NodoAST("Seleccion")
        if not self.consumir(TokenType.if_word):
            self.sincronizar()
            return nodo
        nodo.agregar(self.expresionLogica())
        if not self.consumir(TokenType.then_word):
            self.sincronizar()
            if self.es(TokenType.else_word):
                self.consumir(TokenType.else_word)
                self.sincronizar()
            if self.es(TokenType.end_word):
                self.consumir(TokenType.end_word)
                if self.es(TokenType.puntoComa):
                    self.consumir(TokenType.puntoComa)
            return nodo
        #rama then
        then_nodo = NodoAST("then")
        then_nodo.agregar(self.listaSentencias())
        nodo.agregar(then_nodo)
        if(self.es(TokenType.else_word)):
            self.consumir(TokenType.else_word)
            else_nodo = NodoAST("else")
            else_nodo.agregar(self.listaSentencias())
            nodo.agregar(else_nodo)
        if not self.consumir(TokenType.end_word):
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def iteracion(self):
        nodo = NodoAST("Iteracion")
        if not self.consumir(TokenType.while_word):
            self.sincronizar()
            return nodo
        nodo.agregar(self.expresionLogica())
        nodo.agregar(self.listaSentencias())
        if not self.consumir(TokenType.end_word):
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def repeticion(self):
        nodo = NodoAST("Repeticion")
        if not self.consumir(TokenType.do_word):
            self.sincronizar()
            return nodo
        nodo.agregar(self.listaSentencias(en_do=True))
        if not self.consumir(TokenType.while_word):
            self.sincronizar()
            return nodo
        nodo.agregar(self.expresionLogica())
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo
    
    def esCierreDelDo(self):
        # debe comenzar con while
        if not self.es(TokenType.while_word):
            return False
        pos_original = self.pos
        errores_original = len(self.errores)
        errorExp_original = self.errorExp
        self.pos += 1
        self.expresionLogica()
        cierra = self.es(TokenType.puntoComa)
        #restaurar el estado
        self.pos = pos_original
        del self.errores[errores_original:]
        self.errorExp = errorExp_original
        return cierra
    
    def sentIn(self):
        nodo = NodoAST("sent_in")
        if not self.consumir(TokenType.cin_word):
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.opIn):
            self.sincronizar()
            return nodo
        tok = self.token_actual()
        if self.consumir(TokenType.identificador):
            nodo.agregar(NodoAST("id", tok.lexema))
        else:
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def sentOut(self):
        nodo = NodoAST("sent_out")
        if not self.consumir(TokenType.cout_word):
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.opOut):
            self.sincronizar()
            return nodo
        nodo.agregar(self.salida())
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def salida(self):
        nodo = NodoAST("Salida")
        if self.es(TokenType.cadena):
            tok = self.token_actual()
            self.consumir(TokenType.cadena)
            nodo.agregar(NodoAST("cadena", tok.lexema))
            if self.es(TokenType.opOut):
                self.consumir(TokenType.opOut)
                nodo.agregar(self.expresionLogica())
        else:
            nodo.agregar(self.expresionLogica())
            if self.es(TokenType.opOut):
                self.consumir(TokenType.opOut)
                tok = self.token_actual()
                self.consumir(TokenType.cadena)
                nodo.agregar(NodoAST("cadena", tok.lexema))
        return nodo
    
    def asignacion(self):
        nodo = NodoAST("Asignacion")
        tok = self.token_actual()
        if self.consumir(TokenType.identificador):
            nodo.agregar(NodoAST("id", tok.lexema))
        else:
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.asignacion):
            self.sincronizar()
            return nodo
        self.errorExp = False
        nodo.agregar(self.expresionLogica())
        if self.errorExp:
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def expresionLogica(self):
        izq = self.expresionAnd()
        while self.es(TokenType.opOr):
            self.consumir(TokenType.opOr)
            nodo = NodoAST("op", "||")
            nodo.agregar(izq)
            nodo.agregar(self.expresionAnd())
            izq = nodo 
        return izq

    def expresionAnd(self):
        izq = self.expresion()
        while self.es(TokenType.opAnd):
            self.consumir(TokenType.opAnd)
            nodo = NodoAST("op", "&&")
            nodo.agregar(izq)
            nodo.agregar(self.expresion())
            izq = nodo
        return izq

    def expresion(self):
        izq = self.expresionSimple()
        if (self.es(TokenType.menorQue) or self.es(TokenType.mayorQue) or
                self.es(TokenType.menorIgual) or self.es(TokenType.mayorIgual) or
                self.es(TokenType.igual) or self.es(TokenType.diferente)):
            op = self.relOp()
            op.agregar(izq)
            op.agregar(self.expresionSimple())
            return op  # rel_op es la raíz, operandos son hijos
        return izq

    def relOp(self):
        tok = self.token_actual()
        if self.es(TokenType.menorQue):
            self.consumir(TokenType.menorQue)
            return NodoAST("op", "<")
        elif self.es(TokenType.mayorQue):
            self.consumir(TokenType.mayorQue)
            return NodoAST("op", ">")
        elif self.es(TokenType.menorIgual):
            self.consumir(TokenType.menorIgual)
            return NodoAST("op", "<=")
        elif self.es(TokenType.mayorIgual):
            self.consumir(TokenType.mayorIgual)
            return NodoAST("op", ">=")
        elif self.es(TokenType.igual):
            self.consumir(TokenType.igual)
            return NodoAST("op", "==")
        elif self.es(TokenType.diferente):
            self.consumir(TokenType.diferente)
            return NodoAST("op", "!=")
        else:
            self.errorSintactico(tok, None, "Se esperaba operador relacional")
            return NodoAST("op", "?")

    def expresionSimple(self):
        izq = self.termino()
        while self.es(TokenType.suma) or self.es(TokenType.resta):
            if self.es(TokenType.suma):
                self.consumir(TokenType.suma)
                nodo = NodoAST("op", "+")
            else:
                self.consumir(TokenType.resta)
                nodo = NodoAST("op", "-")
            nodo.agregar(izq)
            nodo.agregar(self.termino())
            izq = nodo
        return izq

    def termino(self):
        izq = self.factor()
        while (self.es(TokenType.multiplicacion) or
            self.es(TokenType.division) or
            self.es(TokenType.modulo)):
            nodo = self.multOp()
            nodo.agregar(izq)
            nodo.agregar(self.factor())
            izq = nodo
        return izq

    
    def multOp(self):
        if self.es(TokenType.multiplicacion):
            self.consumir(TokenType.multiplicacion)
            return NodoAST("op", "*")
        elif self.es(TokenType.division):
            self.consumir(TokenType.division)
            return NodoAST("op", "/")
        elif self.es(TokenType.modulo):
            self.consumir(TokenType.modulo)
            return NodoAST("op", "%")

    def factor(self):
        izq = self.componente()
        if self.es(TokenType.potencia):
            self.consumir(TokenType.potencia)
            nodo = NodoAST("op", "^")
            nodo.agregar(izq)
            nodo.agregar(self.factor())
            return nodo
        return izq
    
    def componente(self):
        if self.es(TokenType.parentesisIzq):
            self.consumir(TokenType.parentesisIzq)
            nodo = self.expresionLogica()  # los paréntesis desaparecen
            self.consumir(TokenType.parentesisDer)
            return nodo
        elif self.es(TokenType.numero_entero):
            tok = self.token_actual()
            self.consumir(TokenType.numero_entero)
            return NodoAST("numero", tok.lexema)
        elif self.es(TokenType.numero_flotante):
            tok = self.token_actual()
            self.consumir(TokenType.numero_flotante)
            return NodoAST("numero", tok.lexema)
        elif self.es(TokenType.identificador):
            tok = self.token_actual()
            self.consumir(TokenType.identificador)
            nodo = NodoAST("id", tok.lexema)
            if self.es(TokenType.incremento):
                self.consumir(TokenType.incremento)
                wrapper = NodoAST("op", "++")
                wrapper.agregar(nodo)
                return wrapper
            elif self.es(TokenType.decremento):
                self.consumir(TokenType.decremento)
                wrapper = NodoAST("op", "--")
                wrapper.agregar(nodo)
                return wrapper
            return nodo
        elif self.es(TokenType.bool_value):
            tok = self.token_actual()
            self.consumir(TokenType.bool_value)
            return NodoAST("bool", tok.lexema)
        elif self.es(TokenType.opNot):
            self.consumir(TokenType.opNot)
            nodo = NodoAST("op", "!")
            nodo.agregar(self.componente())
            return nodo
        else:
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Se esperaba un valor pero se encontró '{tok.lexema}'")
            self.errorExp = True
            return NodoAST("error", tok.lexema)