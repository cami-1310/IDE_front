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
        # Avanzar hasta encontrar un punto seguro
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
        nodo.agregar(self.bloque({
            TokenType.llaveDer, 
            TokenType.endfile
        }))
        if not self.consumir(TokenType.llaveDer):
            return nodo
        if not self.es(TokenType.endfile):
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Se esperaba fin de archivo pero se encontró '{tok.lexema}'")
        return nodo

    def bloque(self, extras=None):
        nodo = NodoAST("Bloque")
        tokens_fin = {
            TokenType.llaveDer,
            TokenType.end_word,
            TokenType.else_word,
            TokenType.endfile
        }
        if(extras is not None):
            tokens_fin |= extras
        while (self.token_actual().tipo not in tokens_fin):
            nodo.agregar(self.elemento())
        return nodo

    def elemento(self):
        if (self.es(TokenType.int_word) or 
             self.es(TokenType.float_word) or 
             self.es(TokenType.bool_word)):
            return self.declaracionVariable()
        elif(self.es(TokenType.if_word) or 
             self.es(TokenType.while_word) or 
             self.es(TokenType.do_word) or 
             self.es(TokenType.cin_word) or 
             self.es(TokenType.cout_word) or
             self.es(TokenType.identificador)):
            return self.sentencia()
        else:
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Token inesperado: '{tok.lexema}'")
            self.pos += 1
            return None

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
            siguiente = self.tokens[self.pos + 1].tipo
            if siguiente in (TokenType.incremento, TokenType.decremento):
                return self.sentPostfijo()
            else:
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
        then_nodo.agregar(self.bloque())
        if(self.es(TokenType.else_word)):
            self.consumir(TokenType.else_word)
            else_nodo = NodoAST("else")
            else_nodo.agregar(self.bloque())
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
        nodo.agregar(self.bloque())
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
        nodo.agregar(self.bloqueDo())
        if not self.consumir(TokenType.while_word):
            self.sincronizar()
            return nodo
        nodo.agregar(self.expresionLogica())
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo

    def bloqueDo(self):
        nodo = NodoAST("Bloque")
        tokens_fin = {
            TokenType.llaveDer,
            TokenType.end_word,
            TokenType.else_word,
            TokenType.endfile
        }
        while self.token_actual().tipo not in tokens_fin:
            if self.es(TokenType.while_word):
                if self.esCierreDelDo():
                    break           # es el while de cierre, salir
                else:
                    nodo.agregar(self.iteracion())  # es un while interno
            else:
                nodo.agregar(self.elemento())
        return nodo

    def esCierreDelDo(self):
        pos_guardada = self.pos
        self.pos += 1  # saltar el while

        profundidad = 0
        while self.pos < len(self.tokens):
            tipo = self.tokens[self.pos].tipo
            if tipo == TokenType.parentesisIzq:
                profundidad += 1
            elif tipo == TokenType.parentesisDer:
                profundidad -= 1
            elif tipo == TokenType.puntoComa and profundidad == 0:
                self.pos = pos_guardada
                return True   # encontró ; → es cierre del do
            elif tipo == TokenType.end_word and profundidad == 0:
                self.pos = pos_guardada
                return False  # encontró end → es iteracion interna
            elif tipo == TokenType.endfile:
                break
            self.pos += 1

        self.pos = pos_guardada
        return False

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

    def sentPostfijo(self):
        nodo = NodoAST("sent_postfijo")
        tok = self.token_actual()
        if self.consumir(TokenType.identificador):
            nodo.agregar(NodoAST("id", tok.lexema))
        if self.es(TokenType.incremento):
            self.consumir(TokenType.incremento)
            nodo.agregar(NodoAST("postfijo", "++"))
        elif self.es(TokenType.decremento):
            self.consumir(TokenType.decremento)
            nodo.agregar(NodoAST("postfijo", "--"))
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
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
        nodo.agregar(self.sentExpresion())
        return nodo

    def sentExpresion(self):
        self.errorExp = False
        nodo = NodoAST("sent_expresion")
        if self.es(TokenType.puntoComa):
            self.consumir(TokenType.puntoComa)
            return nodo
        hijo = self.expresionLogica()
        nodo.agregar(hijo)
        if self.errorExp:
            self.sincronizar()
            return nodo
        if not self.consumir(TokenType.puntoComa):
            self.sincronizar()
        return nodo
        
    def expresionLogica(self):
        nodo = NodoAST("expresion_logica")
        nodo.agregar(self.expresionOr())
        return nodo 

    def expresionOr(self):
        nodo = NodoAST("expresion_or")
        nodo.agregar(self.expresionAnd())
        while self.es(TokenType.opOr):
            self.consumir(TokenType.opOr)
            op = NodoAST("op", "||")
            op.agregar(nodo.hijos[-1] if nodo.hijos else None)
            nodo.agregar(NodoAST("op", "||"))
            nodo.agregar(self.expresionAnd())
        return nodo

    def expresionAnd(self):
        nodo = NodoAST("expresion_and")
        nodo.agregar(self.expresion())
        while self.es(TokenType.opAnd):
            self.consumir(TokenType.opAnd)
            nodo.agregar(NodoAST("op", "&&"))
            nodo.agregar(self.expresion())
        return nodo

    def expresion(self):
        nodo = NodoAST("expresion")
        nodo.agregar(self.expresionSimple())
        if (self.es(TokenType.menorQue) or self.es(TokenType.mayorQue) or
                self.es(TokenType.menorIgual) or self.es(TokenType.mayorIgual) or
                self.es(TokenType.igual) or self.es(TokenType.diferente)):
            nodo.agregar(self.relOp())
            nodo.agregar(self.expresionSimple())
        return nodo

    def relOp(self):
        tok = self.token_actual()
        if self.es(TokenType.menorQue):
            self.consumir(TokenType.menorQue)
            return NodoAST("rel_op", "<")
        elif self.es(TokenType.mayorQue):
            self.consumir(TokenType.mayorQue)
            return NodoAST("rel_op", ">")
        elif self.es(TokenType.menorIgual):
            self.consumir(TokenType.menorIgual)
            return NodoAST("rel_op", "<=")
        elif self.es(TokenType.mayorIgual):
            self.consumir(TokenType.mayorIgual)
            return NodoAST("rel_op", ">=")
        elif self.es(TokenType.igual):
            self.consumir(TokenType.igual)
            return NodoAST("rel_op", "==")
        elif self.es(TokenType.diferente):
            self.consumir(TokenType.diferente)
            return NodoAST("rel_op", "!=")
        else:
            self.errorSintactico(tok, None, "Se esperaba operador relacional")
            return NodoAST("rel_op", "?")

    def expresionSimple(self):
        nodo = NodoAST("expresion_simple")
        nodo.agregar(self.termino())
        while self.es(TokenType.suma) or self.es(TokenType.resta):
            if self.es(TokenType.suma):
                self.consumir(TokenType.suma)
                nodo.agregar(NodoAST("op", "+"))
            elif self.es(TokenType.resta):
                self.consumir(TokenType.resta)
                nodo.agregar(NodoAST("op", "-"))
            nodo.agregar(self.termino())
        return nodo

    def termino(self):
        nodo = NodoAST("termino")
        nodo.agregar(self.factor())
        while (self.es(TokenType.multiplicacion) or
               self.es(TokenType.division) or
               self.es(TokenType.modulo)):
            nodo.agregar(self.multOp())
            nodo.agregar(self.factor())
        return nodo
    
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
        nodo = NodoAST("factor")
        nodo.agregar(self.componente())
        if self.es(TokenType.potencia):
            self.consumir(TokenType.potencia)
            nodo.agregar(NodoAST("op", "^"))
            nodo.agregar(self.factor())
        return nodo
    
    def componente(self):
        nodo = NodoAST("componente")
        if self.es(TokenType.parentesisIzq):
            self.consumir(TokenType.parentesisIzq)
            nodo.agregar(self.expresionLogica())
            self.consumir(TokenType.parentesisDer)
        elif self.es(TokenType.numero_entero):
            tok = self.token_actual()
            self.consumir(TokenType.numero_entero)
            nodo.agregar(NodoAST("numero", tok.lexema))
        elif self.es(TokenType.numero_flotante):
            tok = self.token_actual()
            self.consumir(TokenType.numero_flotante)
            nodo.agregar(NodoAST("numero", tok.lexema))
        elif self.es(TokenType.identificador):
            tok = self.token_actual()
            self.consumir(TokenType.identificador)
            nodo.agregar(NodoAST("id", tok.lexema))
            if self.es(TokenType.incremento):
                self.consumir(TokenType.incremento)
                nodo.agregar(NodoAST("postfijo", "++"))
            elif self.es(TokenType.decremento):
                self.consumir(TokenType.decremento)
                nodo.agregar(NodoAST("postfijo", "--"))
        elif self.es(TokenType.bool_value):
            tok = self.token_actual()
            self.consumir(TokenType.bool_value)
            nodo.agregar(NodoAST("bool", tok.lexema))
        elif self.es(TokenType.opNot):
            self.consumir(TokenType.opNot)
            nodo.agregar(NodoAST("op", "!"))
            nodo.agregar(self.componente())
        else:
            tok = self.token_actual()
            self.errorSintactico(tok, None, f"Se esperaba un valor pero se encontró '{tok.lexema}'")
            self.errorExp = True
        return nodo