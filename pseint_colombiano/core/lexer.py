# pseint_colombiano/core/lexer.py
"""
Analizador Léxico (Lexer) para el pseudocódigo colombiano.
Convierte el código fuente en una secuencia de tokens.
"""
import re
from .keywords_col import REGEX_TOKENS

class Token:
    """Representa un token con su tipo, valor y posición (línea, columna)."""
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Ln {self.line}, Col {self.column})"

class Lexer:
    """Analizador léxico que tokeniza el código fuente."""
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        self.errors = [] # Lista para almacenar errores léxicos

    def tokenize(self):
        """Realiza la tokenización del código."""
        remaining_code = self.code
        line_start_pos = 0 # Para calcular la columna correctamente

        while remaining_code:
            match = None
            # Ajustar la columna para la posición actual en la línea
            # La columna se basa en la posición desde el último '\n'
            # self.current_column = len(self.code) - len(remaining_code) - line_start_pos + 1
            
            # Calcular la posición actual absoluta y luego la columna en la línea actual
            current_pos_abs = len(self.code) - len(remaining_code)
            last_newline_pos = self.code.rfind('\n', 0, current_pos_abs)
            if last_newline_pos == -1: # Primera línea
                self.current_column = current_pos_abs + 1
            else:
                self.current_column = current_pos_abs - last_newline_pos

            for token_type, pattern in REGEX_TOKENS:
                regex = re.compile(pattern)
                m = regex.match(remaining_code)
                if m:
                    value = m.group(0)
                    if token_type == 'NUEVALINEA':
                        self.current_line += 1
                        line_start_pos = current_pos_abs + len(value) # Actualizar para el cálculo de columna
                    elif token_type == 'ESPACIO' or token_type == 'COMENTARIO':
                        # Ignorar espacios y comentarios para la lista de tokens,
                        # pero avanzar el puntero.
                        pass
                    elif token_type == 'ERROR':
                        self.errors.append(
                            f"Error Léxico: Caracter no reconocido '{value}' en línea {self.current_line}, columna {self.current_column}"
                        )
                    else:
                        self.tokens.append(Token(token_type, value, self.current_line, self.current_column))
                    
                    remaining_code = remaining_code[len(value):]
                    match = True
                    break
            
            if not match: # Debería ser manejado por el token 'ERROR'
                # Esto es una salvaguarda, en teoría el token 'ERROR' debería atraparlo.
                # Si se llega aquí, hay un problema con la definición de REGEX_TOKENS.
                error_char = remaining_code[0]
                self.errors.append(
                    f"Error Léxico Fatal: Caracter inesperado '{error_char}' en línea {self.current_line}, columna {self.current_column}."
                )
                remaining_code = remaining_code[1:] # Avanzar para evitar bucle infinito

        self.tokens.append(Token("EOF", "EOF", self.current_line, self.current_column)) # End of File token
        return self.tokens, self.errors

if __name__ == '__main__':
    # Ejemplo de uso
    codigo_ejemplo = """
    ALGORITMO SaludoAmigo
        DEFINA nombre COMO TEXTO; // Definición de variable
        MUESTRE "Hola! ¿Cómo te llamas?";
        LEA nombre;
        MUESTRE "Mucho gusto, ", nombre, "!";
        // Esto es un comentario
        Defina edad Como Entero
        edad = 10 + 5 * 2
        Si edad >= 18 Entonces
            Muestre "Eres mayor de edad"
        SiNo
            Muestre "Eres menor de edad"
        FinSi
    FINALGORITMO
    """
    lexer = Lexer(codigo_ejemplo)
    tokens, errors = lexer.tokenize()

    print("Tokens Generados:")
    for token in tokens:
        print(token)
    
    if errors:
        print("\nErrores Léxicos Encontrados:")
        for error in errors:
            print(error)

    print(f"\nTotal de tokens: {len(tokens)}")
    print(f"Total de errores: {len(errors)}")

    codigo_error = "ALGORITMO PruebaError\n @variableError = 10\nFINALGORITMO"
    lexer_error = Lexer(codigo_error)
    tokens_err, errors_err = lexer_error.tokenize()
    print("\nPrueba con error léxico:")
    for t in tokens_err: print(t)
    for e in errors_err: print(e)