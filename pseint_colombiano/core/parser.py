# pseint_colombiano/core/parser.py
"""
Analizador Sintáctico (Parser) para el pseudocódigo colombiano.
Construye un Árbol de Sintaxis Abstracta (AST) a partir de los tokens.
Este es un parser descendente recursivo muy simplificado.
"""
from .lexer import Token
from .ast_nodes import (
    ProgramaNode, DefinicionVariableNode, MuestreNode, LeaNode,
    AsignacionNode, SiNode, LiteralNode, VariableNode, OperacionBinariaNode
)
from .keywords_col import PALABRAS_CLAVE

class Parser:
    """
    Analizador sintáctico que convierte una lista de tokens en un AST.
    Implementa un parser descendente recursivo simple.
    """
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in ('ESPACIO', 'COMENTARIO', 'NUEVALINEA')]
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else Token("EOF", "EOF", 0, 0)
        self.errors = []

    def _error(self, message, token=None):
        token = token or self.current_token
        err_msg = f"Error Sintáctico: {message} en línea {token.line}, columna {token.column} (token: {token.type} '{token.value}')"
        self.errors.append(err_msg)
        # Podríamos lanzar una excepción aquí para detener el parsing,
        # o intentar sincronizar para encontrar más errores.
        # Por simplicidad, solo registramos y continuamos si es posible.

    def _avanzar(self):
        """Consume el token actual y avanza al siguiente."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            # Asegurar que current_token sea EOF si se acaban los tokens reales
            self.current_token = Token("EOF", "EOF", 
                                       self.tokens[-1].line if self.tokens else 0,
                                       self.tokens[-1].column if self.tokens else 0)


    def _consumir(self, tipo_esperado, valor_esperado=None):
        """Consume el token actual si es del tipo esperado, sino reporta error."""
        if self.current_token.type == tipo_esperado and \
           (valor_esperado is None or self.current_token.value.upper() == valor_esperado.upper()):
            token_consumido = self.current_token
            self._avanzar()
            return token_consumido
        else:
            msg_esperado = tipo_esperado
            if valor_esperado:
                msg_esperado += f" ('{valor_esperado}')"
            self._error(f"Se esperaba {msg_esperado} pero se encontró {self.current_token.type} ('{self.current_token.value}')")
            # Intentar avanzar para evitar bucles si el error no es fatal
            # self._avanzar() # Cuidado con esto, puede saltar tokens importantes
            return None # O lanzar una excepción

    def parse(self):
        """Método principal para iniciar el análisis."""
        # Un programa debe empezar con ALGORITMO y terminar con FINALGORITMO
        programa_node = self._parse_programa()
        if self.current_token.type != "EOF" and not self.errors:
             self._error(f"Tokens extra después del final del programa.")
        return programa_node, self.errors

    def _parse_programa(self):
        """ Parsea: ALGORITMO ID cuerpo FINALGORITMO """
        self._consumir(PALABRAS_CLAVE["ALGORITMO"])
        nombre_algoritmo = self._consumir("ID")
        if nombre_algoritmo is None: # Si el ID no se pudo consumir
            nombre_algoritmo = Token("ID", "_sin_nombre_", self.current_token.line, self.current_token.column)

        cuerpo = self._parse_cuerpo_sentencias(PALABRAS_CLAVE["FINALGORITMO"])
        
        self._consumir(PALABRAS_CLAVE["FINALGORITMO"])
        return ProgramaNode(nombre_algoritmo, cuerpo)

    def _parse_cuerpo_sentencias(self, token_fin_bloque):
        """ Parsea una secuencia de sentencias hasta encontrar token_fin_bloque """
        sentencias = []
        while self.current_token.type != token_fin_bloque and self.current_token.type != "EOF":
            sentencia = self._parse_sentencia()
            if sentencia:
                sentencias.append(sentencia)
            # Si _parse_sentencia devuelve None (por error y no avanzar), debemos avanzar aquí
            # para evitar un bucle infinito si _error no lanza excepción.
            # Esto es delicado. Lo ideal es que _error o _consumir manejen el avance o excepción.
            # Por ahora, asumimos que _parse_sentencia avanza o hay error fatal.
            if self.pos < len(self.tokens) and self.tokens[self.pos-1] == self.current_token and sentencia is None:
                # Si no avanzó y hubo un error, forzar avance para evitar bucle
                # Esto es un parche, la gestión de errores debería ser más robusta
                if self.current_token.type != "EOF": # No avanzar si ya estamos en EOF
                    self._error("Error no recuperado, saltando token.")
                    self._avanzar()


        return sentencias

    def _parse_sentencia(self):
        """Determina qué tipo de sentencia parsear."""
        if self.current_token.type == PALABRAS_CLAVE["DEFINA"]:
            return self._parse_definicion_variable()
        elif self.current_token.type == PALABRAS_CLAVE["MUESTRE"]:
            return self._parse_muestre()
        elif self.current_token.type == PALABRAS_CLAVE["LEA"]:
            return self._parse_lea()
        elif self.current_token.type == "ID": # Podría ser una asignación o llamada a función
            # Miramos el siguiente token para decidir
            if self.pos + 1 < len(self.tokens):
                siguiente_token = self.tokens[self.pos + 1]
                if siguiente_token.type == "ASIGNACION":
                    return self._parse_asignacion()
                # TODO: Aquí iría la lógica para llamadas a función
            # Si no, es un error o una expresión suelta (no permitido como sentencia)
            self._error(f"Sentencia no reconocida iniciada con ID '{self.current_token.value}'")
            self._avanzar() # Avanzar para evitar bucle
            return None
        elif self.current_token.type == PALABRAS_CLAVE["SI"]:
            return self._parse_si()
        # TODO: Añadir MIENTRAS, PARA, REPITA, FUNCION, etc.
        else:
            if self.current_token.type != "EOF": # No es error si solo es EOF
                self._error(f"Sentencia inesperada: token '{self.current_token.value}'")
                self._avanzar() # Avanzar para evitar bucle
            return None

    def _parse_definicion_variable(self):
        """ Parsea: DEFINA ID [, ID]* COMO TIPO_DATO [;] """
        self._consumir(PALABRAS_CLAVE["DEFINA"])
        variables = [self._consumir("ID")]
        while self.current_token.type == "COMA":
            self._avanzar() # Consumir COMA
            variables.append(self._consumir("ID"))
        
        self._consumir(PALABRAS_CLAVE["COMO"])
        
        # El tipo puede ser una de las palabras clave de tipo
        tipo_token_valor = self.current_token.value.upper()
        tipo_token_type = None
        for kw_key, kw_val in PALABRAS_CLAVE.items(): # Buscar el tipo correcto
            if tipo_token_valor == kw_key and kw_val.startswith("TIPO_"):
                tipo_token_type = kw_val
                break
        
        if tipo_token_type:
            tipo = self._consumir(tipo_token_type, valor_esperado=tipo_token_valor)
        else:
            self._error(f"Tipo de dato desconocido: {self.current_token.value}")
            tipo = Token("ERROR_TIPO", self.current_token.value, self.current_token.line, self.current_token.column)
            self._avanzar() # Consumir el token erróneo

        if self.current_token.type == "PUNTOYCOMA": # Opcional
            self._avanzar()
        
        # Filtrar None de variables si hubo errores en _consumir("ID")
        variables_validas = [v for v in variables if v is not None]
        if not variables_validas: # Si todas las variables fallaron
            return None
        return DefinicionVariableNode(variables_validas, tipo)

    def _parse_muestre(self):
        """ Parsea: MUESTRE expresion [, expresion]* [;] """
        self._consumir(PALABRAS_CLAVE["MUESTRE"])
        expresiones = [self._parse_expresion()]
        while self.current_token.type == "COMA":
            self._avanzar()
            expresiones.append(self._parse_expresion())
        
        if self.current_token.type == "PUNTOYCOMA": # Opcional
            self._avanzar()
        
        expresiones_validas = [e for e in expresiones if e is not None]
        if not expresiones_validas:
            return None
        return MuestreNode(expresiones_validas)

    def _parse_lea(self):
        """ Parsea: LEA ID [;] """
        self._consumir(PALABRAS_CLAVE["LEA"])
        variable = self._consumir("ID")
        if self.current_token.type == "PUNTOYCOMA": # Opcional
            self._avanzar()
        if variable is None:
            return None
        return LeaNode(variable)

    def _parse_asignacion(self):
        """ Parsea: ID ASIGNACION expresion [;] """
        variable = self._consumir("ID")
        self._consumir("ASIGNACION")
        expresion = self._parse_expresion()
        if self.current_token.type == "PUNTOYCOMA": # Opcional
            self._avanzar()
        if variable is None or expresion is None:
            return None
        return AsignacionNode(variable, expresion)

    def _parse_si(self):
        """ Parsea: SI expresion ENTONCES cuerpo_si [SINO cuerpo_sino] FINSI """
        self._consumir(PALABRAS_CLAVE["SI"])
        condicion = self._parse_expresion()
        self._consumir(PALABRAS_CLAVE["ENTONCES"])
        
        cuerpo_si = self._parse_cuerpo_sentencias_condicional(
            [PALABRAS_CLAVE["SINO"], PALABRAS_CLAVE["FINSI"]]
        )
        
        cuerpo_sino = None
        if self.current_token.type == PALABRAS_CLAVE["SINO"]:
            self._avanzar() # Consumir SINO
            cuerpo_sino = self._parse_cuerpo_sentencias_condicional([PALABRAS_CLAVE["FINSI"]])
            
        self._consumir(PALABRAS_CLAVE["FINSI"])
        
        if condicion is None or cuerpo_si is None: # cuerpo_sino es opcional
             # Ya se habrá reportado un error antes
            return None
        return SiNode(condicion, cuerpo_si, cuerpo_sino)

    def _parse_cuerpo_sentencias_condicional(self, tokens_fin_bloque):
        """ Parsea una secuencia de sentencias hasta encontrar uno de los tokens_fin_bloque """
        sentencias = []
        while self.current_token.type not in tokens_fin_bloque and self.current_token.type != "EOF":
            sentencia = self._parse_sentencia()
            if sentencia:
                sentencias.append(sentencia)
            # Similar al _parse_cuerpo_sentencias, manejar avance en caso de error no fatal
            if self.pos < len(self.tokens) and self.tokens[self.pos-1] == self.current_token and sentencia is None:
                 if self.current_token.type != "EOF":
                    self._error("Error no recuperado en bloque condicional, saltando token.")
                    self._avanzar()
        return sentencias

    # --- Parsing de Expresiones (muy simplificado, necesita precedencia de operadores) ---
    # Para un parser real, se usa el algoritmo Shunting-yard o precedencia de operadores.
    # Esto es una versión muy básica que solo maneja términos y sumas/restas.
    
    def _parse_expresion(self):
        """ Parsea una expresión. Llama a _parse_termino_logico_o para la precedencia. """
        return self._parse_termino_logico_o() # Empezar con el operador de menor precedencia

    def _parse_termino_logico_o(self):
        """ Parsea expresiones con 'O' """
        nodo = self._parse_termino_logico_y()
        while self.current_token.type == "OP_O":
            op_token = self.current_token
            self._avanzar()
            nodo_derecho = self._parse_termino_logico_y()
            if nodo is None or nodo_derecho is None: return None # Propagar error
            nodo = OperacionBinariaNode(nodo, op_token, nodo_derecho)
        return nodo

    def _parse_termino_logico_y(self):
        """ Parsea expresiones con 'Y' """
        nodo = self._parse_comparacion()
        while self.current_token.type == "OP_Y":
            op_token = self.current_token
            self._avanzar()
            nodo_derecho = self._parse_comparacion()
            if nodo is None or nodo_derecho is None: return None
            nodo = OperacionBinariaNode(nodo, op_token, nodo_derecho)
        return nodo

    def _parse_comparacion(self):
        """ Parsea comparaciones: ==, <>, <, >, <=, >= """
        nodo = self._parse_suma_resta() # Las comparaciones tienen menor precedencia que suma/resta
        ops_comparacion = ["OP_IGUAL", "OP_DISTINTO", "OP_MENOR", "OP_MAYOR", "OP_MENOR_IGUAL", "OP_MAYOR_IGUAL"]
        while self.current_token.type in ops_comparacion:
            op_token = self.current_token
            self._avanzar()
            nodo_derecho = self._parse_suma_resta()
            if nodo is None or nodo_derecho is None: return None
            nodo = OperacionBinariaNode(nodo, op_token, nodo_derecho)
        return nodo
        
    def _parse_suma_resta(self):
        """ Parsea sumas y restas. """
        nodo = self._parse_mult_div()
        while self.current_token.type in ("OP_SUMA", "OP_RESTA"):
            op_token = self.current_token
            self._avanzar()
            nodo_derecho = self._parse_mult_div()
            if nodo is None or nodo_derecho is None: return None
            nodo = OperacionBinariaNode(nodo, op_token, nodo_derecho)
        return nodo

    def _parse_mult_div(self):
        """ Parsea multiplicaciones y divisiones. """
        nodo = self._parse_factor()
        while self.current_token.type in ("OP_MULT", "OP_DIV", "OP_MOD"): # Añadido MOD
            op_token = self.current_token
            self._avanzar()
            nodo_derecho = self._parse_factor()
            if nodo is None or nodo_derecho is None: return None
            nodo = OperacionBinariaNode(nodo, op_token, nodo_derecho)
        return nodo

    def _parse_factor(self):
        """Parsea los elementos más básicos de una expresión: literales, variables, expresiones entre paréntesis."""
        token = self.current_token
        if token.type == 'NUMERO_ENTERO' or token.type == 'NUMERO_REAL' or \
           token.type == 'CADENA' or token.type == 'VALOR_VERDADERO' or token.type == 'VALOR_FALSO':
            self._avanzar()
            return LiteralNode(token)
        elif token.type == 'ID':
            self._avanzar()
            # TODO: Aquí se necesitaría diferenciar entre variable y llamada a función si las funciones toman args
            return VariableNode(token)
        elif token.type == 'PARENTESIS_IZQ':
            self._avanzar() # Consumir '('
            nodo_expresion = self._parse_expresion()
            self._consumir('PARENTESIS_DER') # Consumir ')'
            return nodo_expresion
        elif token.type == 'OP_RESTA' or token.type == 'OP_NO': # Operador unario (negación, NO lógico)
            # Esto es simplificado, un parser completo manejaría operadores unarios con más cuidado
            # Ejemplo: -5, NO verdadero
            # Por ahora, no lo implementamos completamente para mantenerlo simple.
            self._error(f"Operadores unarios ('{token.value}') aún no completamente soportados en esta posición.")
            self._avanzar()
            return None # O un UnaryOpNode si se implementa
        else:
            self._error(f"Factor inesperado en expresión: token '{token.value}'")
            self._avanzar() # Para evitar bucle infinito
            return None

if __name__ == '__main__':
    from .lexer import Lexer # Importación relativa para prueba
    codigo_ejemplo = """
    ALGORITMO CalculadoraSimple
        DEFINA a, b, resultado COMO ENTERO
        MUESTRE "Ingrese primer número:"
        LEA a
        MUESTRE "Ingrese segundo número:"
        LEA b
        resultado = a + b * 2
        MUESTRE "La suma es: ", resultado
        Si resultado > 10 Entonces
            Muestre "El resultado es mayor que 10"
        SiNo
            Muestre "El resultado es menor o igual a 10"
        FinSi
    FINALGORITMO
    """
    lexer = Lexer(codigo_ejemplo)
    tokens, errors_lex = lexer.tokenize()

    if errors_lex:
        print("Errores del Lexer:")
        for err in errors_lex: print(err)
    else:
        print("Tokens para el Parser:")
        for t in tokens: print(t)
        
        parser = Parser(tokens)
        ast, errors_par = parser.parse()

        print("\nAST Generado:")
        import sys
        from io import StringIO
        # Capturar la salida de repr para el AST si es muy grande
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        print(ast) # Usa __repr__ de los nodos
        sys.stdout = old_stdout
        print(captured_output.getvalue())


        if errors_par:
            print("\nErrores del Parser:")
            for err in errors_par:
                print(err)
        else:
            print("\nAnálisis sintáctico completado sin errores.")