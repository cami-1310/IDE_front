#Todo este archivo se encarga de tokenizar

from enum import Enum, auto

#Estados del automata
class Estado(Enum):
    inicio=auto()
    entradaID=auto()
    entradaNum=auto()
    entradaNumFlotante=auto()
    numFlotante=auto()
    posibleComentario=auto()
    cml=auto() #comentario de multiples lineas
    cul=auto() #comentario de una linea
    pfc=auto() #posible final de comentario
    posibleCadena=auto()
    posibleCaracter=auto()
    caracter=auto()
    posibleOR=auto()
    posibleAND=auto()
    posibleOpLogico=auto()
    posibleIncremento=auto()
    posibleDecremento=auto()
    hecho=auto() #estado final

#Todos los tokens posibles
class TokenType(Enum):
    #book-keeping
    endfile=auto()
    error=auto()
    #palabras reservadas
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
    #literales
    identificador=auto()
    numero_entero=auto()
    numero_flotante=auto()
    cadena=auto()
    caracter=auto()
    #operdores aritmeticos
    suma=auto()
    resta=auto()
    multiplicacion=auto()
    division=auto()
    modulo=auto()
    potencia=auto()
    incremento=auto()
    decremento=auto()
    #operadores relacionales y logicos
    menorQue=auto()
    menorIgual=auto()
    mayorQue=auto()
    mayorIgual=auto()
    diferente=auto()
    igual=auto()
    opAnd=auto()
    opOr=auto()
    opNot=auto()
    #simbolos especiales
    parentesisDer=auto()
    parentesisIzq=auto()
    llaveDer=auto()
    llaveIzq=auto()
    coma=auto()
    puntoComa=auto()
    #asignacion
    asignacion=auto()
    
#array de las palabras reservadas
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
        #obteniendo codigo actual del editor
        self.codigo=self.texto.get("1.0", "end-1c") #obtener todo el codigo del textarea
        self.index=0
        self.linea=1
        self.columna=1

    def getToken(self):
        #esta funcion nos va a retornar el siguiente token
        #ignora comentarios, espacios en blanco y tabuladores

        while True:
            #loop para ignorar los comentarios (regresa al inicio)
            resultado=self.escanear()
            if resultado is not None:
                return resultado
            
    def escanear(self):
        #esta funcion es lo equivalente a ejecutar el automata
        #retorna TokenResult o None si es un comentario
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
                    #si el caracter es un espacio en blanco, un tabulador, o un salto de linea
                    #no se guarda
                    guardar=False
                elif(c.isdigit()):
                    estado=Estado.entradaNum
                elif (c.isalpha()):
                    estado=Estado.entradaID
                elif(c=='/'):
                    guardar=False #el caracter no forma parte del lexema todavía
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
                    #{|}|(|)|,|;|*|^|%
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

            #entrada de un ID
            elif(estado==Estado.entradaID):
                if(c is not None and (c.isalpha() or c.isdigit())):
                    #el primer caracter debe ser una letra, de ahi, el id si puede contener numeros
                    pass
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    #si encuentra el lexema entre las palabras reservadas lo tokeniza como tal
                    #si no, se trata de un identificador
                    tokenActual=reserved_words.get(lexema, TokenType.identificador)
            
            #entrada de un numero
            elif(estado==Estado.entradaNum):
                if(c is not None and c.isdigit()):
                    pass
                elif(c=='.'):
                    estado=Estado.entradaNumFlotante
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False #el char que rompió el numero no se guarda
                    estado=Estado.hecho
                    tokenActual=TokenType.numero_entero
            
            #posible entrada de un flotante
            elif(estado==Estado.entradaNumFlotante):
                if(c is not None and c.isdigit()):
                    estado=Estado.numFlotante
                else:
                    #tiene punto pero no digito despues, es error
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=TokenType.error
                    self.reportarError(f"Número mal formado: '{lexema}' (punto sin decimales)", token_linea, token_columna)
            
            #entrada de un flotante
            elif(estado==Estado.numFlotante):
                if(c is not None and c.isdigit()):
                    pass
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    estado=Estado.hecho
                    tokenActual=TokenType.numero_flotante
            
            #entrada de un posible comentario
            elif(estado==Estado.posibleComentario):
                guardar=False
                if(c=='/'):
                    #comenario de una linea
                    estado=Estado.cul
                elif(c=='*'):
                    #comenario de multiples lineas
                    estado=Estado.cml
                else:
                    if(c is not None):
                        self.regresarC()
                    #si despues de la / viene otro caracter debería ser division
                    lexema='/'
                    tokenActual=TokenType.division
                    estado=Estado.hecho
            
            #comentario de una sola linea
            elif(estado==Estado.cul):
                guardar=False
                if(c=='\n' or c is None):
                    return None #ignorar el comentario completo
            
            #comentario multiples lineas
            elif(estado==Estado.cml):
                guardar=False
                if(c is None):
                    self.reportarError("Comentario multilínea sin cerrar", token_linea, token_columna)
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                elif(c=='*'):
                    estado=Estado.pfc
            
            #posible final de comentario
            elif(estado==Estado.pfc):
                guardar=False
                if(c=='/'):
                    return None #ignorar el comentario completo
                elif(c is None):
                    self.reportarError("Comentario multilínea sin cerrar", token_linea, token_columna)
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                elif(c!='*'):
                    estado=Estado.cml #sigue dentro del comentario
            
            #posible cadena
            elif(estado==Estado.posibleCadena):
                if(c=='"'):
                    guardar=False #la comilla de cierre no se guarda en el lexema
                    tokenActual=TokenType.cadena
                    estado=Estado.hecho
                elif(c is None or c=='\n'):
                    guardar=False #EOF o salto de linea no van en el lexema
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Cadena sin cerrar", token_linea, token_columna)
                #else solo acumula los caracteres de la cadena
                    
            #posible caracter
            elif(estado==Estado.posibleCaracter):
                if(c is None or c=='\n'):
                    guardar=False #EOF o salto de linea no van en el lexema
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Caracter mal declarado", token_linea, token_columna)
                else:
                    estado=Estado.caracter

            #entrada de un caracter
            elif(estado==Estado.caracter):
                if(c=="'"):
                    guardar=False #la comilla no se guarda en el lexema
                    tokenActual=TokenType.caracter
                    estado=Estado.hecho
                else:
                    guardar=False #lo que venga despues ya no va al lexema
                    tokenActual=TokenType.error
                    estado=Estado.hecho
                    self.reportarError("Caracter mal declarado", token_linea, token_columna)
            
            #posible &&
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

            #posible ||
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
            
            #posible ++
            elif(estado==Estado.posibleIncremento):
                estado=Estado.hecho
                if(c=='+'):
                    tokenActual=TokenType.incremento
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    tokenActual=TokenType.suma

            #posible --
            elif(estado==Estado.posibleDecremento):
                estado=Estado.hecho
                if(c=='-'):
                    tokenActual=TokenType.decremento
                else:
                    if(c is not None):
                        self.regresarC()
                    guardar=False
                    tokenActual=TokenType.resta

            #posible operador logico
            elif(estado==Estado.posibleOpLogico):
                estado=Estado.hecho
                if(c=='='):
                    if(lexema=='!'): tokenActual=TokenType.diferente
                    elif(lexema=='<'): tokenActual=TokenType.menorIgual
                    elif(lexema=='>'): tokenActual=TokenType.mayorIgual
                    elif(lexema=='='): tokenActual=TokenType.igual
                else:
                    #operador simple, devolver el leido
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

    def sigienteC(self):
        if self.index >= len(self.codigo):
            return None #EOF
        
        #else
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
        #print(texto_error)
        if self.bottom_panel:
            try:
                self.bottom_panel.add_error_lexico(texto_error)
            except Exception:
                pass
