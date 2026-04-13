from enum import Enum, auto

class Estado(Enum):
    inicio=auto()
    entradaID=auto()
    entradaNum=auto()
    entradaNumFlotante=auto()
    numFlotante=auto()
    posibleComentario=auto()
    cml=auto()
    cul=auto()
    pfc=auto()
    posibleCadena=auto()
    posibleCaracter=auto()
    caracter=auto()
    posibleOR=auto()
    posibleAND=auto()
    posibleOpLogico=auto()
    posibleIncremento=auto()
    posibleDecremento=auto()
    hecho=auto()

class TokenType(Enum):
    endfile=auto()
    error=auto()
    if_word=auto()
    else_word=auto()
    end_word=auto()
    do_word=auto()
    while_word=auto()
    switch_word=auto()
    case_word=auto()
    int_word=auto()
    float_word=auto()
    main_word=auto()
    cin_word=auto()
    cout_word=auto()
    identificador=auto()
    numero_entero=auto()
    numero_flotante=auto()
    cadena=auto()
    caracter=auto()
    suma=auto()
    resta=auto()
    multiplicacion=auto()
    division=auto()
    modulo=auto()
    potencia=auto()
    incremento=auto()
    decremento=auto()
    menorQue=auto()
    menorIgual=auto()
    mayorQue=auto()
    mayorIgual=auto()
    diferente=auto()
    igual=auto()
    opAnd=auto()
    opOr=auto()
    opNot=auto()
    parentesisDer=auto()
    parentesisIzq=auto()
    llaveDer=auto()
    llaveIzq=auto()
    coma=auto()
    puntoComa=auto()
    asignacion=auto()
    comentario=auto()

reserved_words={
    "if":     TokenType.if_word,
    "else":   TokenType.else_word,
    "end":    TokenType.end_word,
    "do":     TokenType.do_word,
    "while":  TokenType.while_word,
    "switch": TokenType.switch_word,
    "case":   TokenType.case_word,
    "int":    TokenType.int_word,
    "float":  TokenType.float_word,
    "main":   TokenType.main_word,
    "cin":    TokenType.cin_word,
    "cout":   TokenType.cout_word,
}

class TokenResult:
    def __init__(self, tipo, lexema, linea, columna):
        self.tipo=tipo
        self.lexema=lexema
        self.linea=linea
        self.columna=columna

    def __repr__(self):
        return f"Token({self.tipo.name}, '{self.lexema}', L{self.linea}:C{self.columna})"

class Token:
    def __init__(self, root, text_widget, bottom_panel=None):
        self.root=root
        self.texto=text_widget
        self.bottom_panel=bottom_panel
        self.codigo=""
        self.index=0
        self.linea=1
        self.columna=1

    def cargarCodigo(self):
        self.codigo=self.texto.get("1.0", "end-1c")
        self.index=0
        self.linea=1
        self.columna=1

    def getToken(self):
        while True:
            resultado=self.escanear()
            if resultado is not None:
                return resultado

    def escanear(self):
        lexema=""
        estado=Estado.inicio
        tokenActual=TokenType.error
        token_linea=self.linea
        token_columna=self.columna

        while(estado != Estado.hecho):
            c=self.sigienteC()
            guardar=True

            if(estado==Estado.inicio):
                token_linea=self.linea
                token_columna=self.columna-(1 if c and c != '\n' else 0)

                if(c is None):
                    guardar=False
                    tokenActual=TokenType.endfile
                    estado=Estado.hecho
                elif(c in (' ', '\t', '\n')):
                    guardar=False
                elif(c.isdigit()):
                    estado=Estado.entradaNum
                elif(c.isalpha()):
                    estado=Estado.entradaID
                elif(c=='/'):
                    guardar=False
                    estado=Estado.posibleComentario
                elif(c=='&'):
                    guardar=False
                    estado=Estado.posibleAND
                elif(c=='|'):
                    guardar=False
                    estado=Estado.posibleOR
                elif(c=='-'):
                    estado=Estado.posibleDecremento
                elif(c=='+'):
                    estado=Estado.posibleIncremento
                elif(c=='"'):
                    guardar=False
                    estado=Estado.posibleCadena
                elif(c=="'"):
                    guardar=False
                    estado=Estado.posibleCaracter
                elif(c in ('!', '<', '>', '=')):
                    estado=Estado.posibleOpLogico
                else:
                    estado=Estado.hecho
                    if(c=='('): tokenActual=TokenType.parentesisIzq
                    elif(c==')'): tokenActual=TokenType.parentesisDer
                    elif(c=='{'): tokenActual=TokenType.llaveIzq
                    elif(c=='}'): tokenActual=TokenType.llaveDer
                    elif(c==','): tokenActual=TokenType.coma
                    elif(c==';'): tokenActual=TokenType.puntoComa
                    elif(c=='*'): tokenActual=TokenType.multiplicacion
                    elif(c=='^'): tokenActual=TokenType.potencia
                    elif(c=='%'): tokenActual=TokenType.modulo
                    else:
                        tokenActual=TokenType.error
                        self.reportarError(f"Caracter no reconocido: '{c}'", token_linea, token_columna)

            elif(estado==Estado.entradaID):
                if(c is not None and (c.isalpha() or c.isdigit())):
                    pass
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=reserved_words.get(lexema, TokenType.identificador)

            elif(estado==Estado.entradaNum):
                if(c is not None and c.isdigit()):
                    pass
                elif(c=='.'):
                    estado=Estado.entradaNumFlotante
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=TokenType.numero_entero

            elif(estado==Estado.entradaNumFlotante):
                if(c is not None and c.isdigit()):
                    estado=Estado.numFlotante
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=TokenType.error
                    self.reportarError(f"Número mal formado: '{lexema}' (punto sin decimales)", token_linea, token_columna)

            elif(estado==Estado.numFlotante):
                if(c is not None and c.isdigit()):
                    pass
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=TokenType.numero_flotante

            elif(estado==Estado.posibleComentario):
                guardar=False
                if(c=='/'):
                    estado=Estado.cul
                    lexema='//'
                elif(c=='*'):
                    estado=Estado.cml
                    lexema='/*'
                else:
                    if(c is not None):
                        self.regresarC()
                    lexema='/'
                    tokenActual=TokenType.division
                    estado=Estado.hecho

            elif(estado==Estado.cul):
                if(c=='\n' or c is None):
                    guardar=False
                    tokenActual=TokenType.comentario
                    estado=Estado.hecho
                else:
                    pass

            elif(estado==Estado.cml):
                if(c is None):
                    self.reportarError("Comentario multilínea sin cerrar", token_linea, token_columna)
                    guardar=False
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                elif(c=='*'):
                    estado=Estado.pfc
                else:
                    pass

            elif(estado==Estado.pfc):
                if(c=='/'):
                    lexema+=c
                    guardar=False
                    tokenActual=TokenType.comentario
                    estado=Estado.hecho
                elif(c is None):
                    self.reportarError("Comentario multilínea sin cerrar", token_linea, token_columna)
                    guardar=False
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                elif(c!='*'):
                    estado=Estado.cml

            elif(estado==Estado.posibleCadena):
                if(c=='"'):
                    guardar=False
                    tokenActual=TokenType.cadena
                    estado=Estado.hecho
                elif(c is None or c=='\n'):
                    guardar=False
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Cadena sin cerrar", token_linea, token_columna)

            elif(estado==Estado.posibleCaracter):
                if(c=="'"):
                    guardar=False
                    tokenActual=TokenType.caracter
                    estado=Estado.hecho
                elif(c is None or c=='\n'):
                    guardar=False
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Caracter mal declarado", token_linea, token_columna)
                else:
                    estado=Estado.caracter

            elif(estado==Estado.caracter):
                if(c=="'"):
                    guardar=False
                    tokenActual=TokenType.caracter
                    estado=Estado.hecho
                else:
                    guardar=False
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Caracter mal declarado", token_linea, token_columna)

            elif(estado==Estado.posibleAND):
                guardar=False
                estado=Estado.hecho
                if(c=='&'):
                    lexema='&&'
                    tokenActual=TokenType.opAnd
                else:
                    if(c is not None):
                        self.regresarC()
                    tokenActual=TokenType.error
                    self.reportarError("'&' solo no es válido, use '&&'", token_linea, token_columna)

            elif(estado==Estado.posibleOR):
                guardar=False
                estado=Estado.hecho
                if(c=='|'):
                    lexema='||'
                    tokenActual=TokenType.opOr
                else:
                    if(c is not None):
                        self.regresarC()
                    tokenActual=TokenType.error
                    self.reportarError("'|' solo no es válido, use '||'", token_linea, token_columna)

            elif(estado==Estado.posibleIncremento):
                estado=Estado.hecho
                if(c=='+'):
                    tokenActual=TokenType.incremento
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    tokenActual=TokenType.suma

            elif(estado==Estado.posibleDecremento):
                estado=Estado.hecho
                if(c=='-'):
                    tokenActual=TokenType.decremento
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    tokenActual=TokenType.resta

            elif(estado==Estado.posibleOpLogico):
                estado=Estado.hecho
                if(c=='='):
                    if(lexema=='!'): tokenActual=TokenType.diferente
                    elif(lexema=='<'): tokenActual=TokenType.menorIgual
                    elif(lexema=='>'): tokenActual=TokenType.mayorIgual
                    elif(lexema=='='): tokenActual=TokenType.igual
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    if(lexema=='<'): tokenActual=TokenType.menorQue
                    elif(lexema=='>'): tokenActual=TokenType.mayorQue
                    elif(lexema=='='): tokenActual=TokenType.asignacion
                    elif(lexema=='!'): tokenActual=TokenType.opNot

            if(guardar and c is not None):
                lexema+=c

        return TokenResult(tokenActual, lexema, token_linea, token_columna)

    def limpiarErrores(self):
        if self.bottom_panel:
            try:
                self.bottom_panel.limpiar_errores_lexicos() 
            except Exception:
                pass

    def tokenizar_todo(self):
        self.cargarCodigo()
        if self.bottom_panel:          # ← agrega estas dos líneas
            self.bottom_panel.clean_errores_lexicos()
        tokens = []
        while True:
            tok = self.getToken()
            if tok.tipo == TokenType.endfile:
                break
            tokens.append(tok)
        return tokens

    def sigienteC(self):
        if self.index >= len(self.codigo):
            return None
        c=self.codigo[self.index]
        self.index+=1
        if(c=='\n'):
            self.linea+=1
            self.columna=1
        else:
            self.columna+=1
        return c

    def regresarC(self):
        if self.index > 0:
            self.index-=1
            c=self.codigo[self.index]
            if(c=='\n'):
                self.linea-=1
                prev=self.codigo.rfind('\n', 0, self.index)
                self.columna=self.index-prev
            else:
                self.columna-=1

    def reportarError(self, mensaje, linea, columna):
        texto_error=f"[Error léxico] L{linea}:C{columna} → {mensaje}"
        if self.bottom_panel:
            try:
                self.bottom_panel.add_error_lexico(texto_error)
            except Exception:
                pass