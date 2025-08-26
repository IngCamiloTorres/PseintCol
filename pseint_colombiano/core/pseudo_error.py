# pseint_colombiano/core/pseudo_error.py
"""
Clases de error personalizadas para el intérprete de pseudocódigo.
"""

class PseudoError(Exception):
    """Clase base para errores específicos del pseudocódigo."""
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"[Línea {self.line}, Col {self.column}] {self.message}"
        return self.message

class PseudoLexerError(PseudoError):
    """Errores durante el análisis léxico."""
    pass

class PseudoSyntaxError(PseudoError):
    """Errores durante el análisis sintáctico."""
    pass

class PseudoRuntimeError(PseudoError):
    """Errores durante la ejecución/interpretación del pseudocódigo."""
    pass

if __name__ == '__main__':
    try:
        raise PseudoLexerError("Caracter inválido '$'", line=5, column=10)
    except PseudoError as e:
        print(f"Error capturado: {e}")

    try:
        raise PseudoRuntimeError("División por cero")
    except PseudoError as e:
        print(f"Error capturado: {e}")