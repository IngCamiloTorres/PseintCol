# pseint_colombiano/core/keywords_col.py
"""
Módulo para definir las palabras clave y tokens del pseudocódigo colombiano.
"""

# Palabras clave del lenguaje
PALABRAS_CLAVE = {
    # Estructura principal
    "ALGORITMO": "ALGORITMO",
    "FINALGORITMO": "FINALGORITMO",
    "PROCESO": "ALGORITMO", # Alias
    "FINPROCESO": "FINALGORITMO", # Alias

    # Definición de variables
    "DEFINA": "DEFINA",
    "COMO": "COMO",
    "ENTERO": "TIPO_ENTERO",
    "REAL": "TIPO_REAL",
    "LOGICO": "TIPO_LOGICO",
    "TEXTO": "TIPO_TEXTO", # En PSeInt es Caracter, Texto es más común
    "CARACTER": "TIPO_TEXTO", # Alias

    # Entrada/Salida
    "MUESTRE": "MUESTRE", # En vez de Escribir
    "ESCRIBA": "MUESTRE", # Alias
    "LEA": "LEA", # En vez de Leer

    # Condicionales
    "SI": "SI",
    "ENTONCES": "ENTONCES",
    "SINO": "SINO",
    "FINSI": "FINSI",

    # Ciclos
    "MIENTRAS": "MIENTRAS",
    "HAGA": "HAGA",
    "FINMIENTRAS": "FINMIENTRAS",
    "REPITA": "REPITA",
    "HASTAQUE": "HASTAQUE",
    "PARA": "PARA",
    "HASTA": "HASTA",
    "CONPASO": "CONPASO",
    "FINPARA": "FINPARA",

    # Funciones (Subprocesos en PSeInt)
    "FUNCION": "FUNCION",
    "FINFUNCION": "FINFUNCION",
    "SUBPROCESO": "FUNCION", # Alias
    "FINSUBPROCESO": "FINFUNCION", # Alias

    # Operadores lógicos como palabras
    "Y": "OP_Y",
    "O": "OP_O",
    "NO": "OP_NO",

    # Valores lógicos
    "VERDADERO": "VALOR_VERDADERO",
    "FALSO": "VALOR_FALSO",
}

# Tipos de tokens adicionales (no son palabras clave directas)
TOKEN_TIPOS = [
    # -- Tokens que deben tener alta prioridad por su especificidad --
    ('COMENTARIO', r'//[^\n]*'),      # Comentarios de una línea (ANTES DE OP_DIV)
    
    # -- Operadores de dos o más caracteres (ANTES de los de un caracter que puedan ser subcadenas) --
    ('ASIGNACION', r'<-'),            # Asignación PSeInt original (ANTES DE < y - por si acaso)
                                      # Si también se usa '=', la regex original era r'<-|='
                                      # Si '=' es asignación y '==' es comparación:
                                      # ('ASIGNACION_IGUAL', r'='),
                                      # ('OP_IGUAL_COMP', r'=='),
                                      # La lógica actual usa 'ASIGNACION' para 'r'<-|=' y 'OP_IGUAL' para 'r'=='
                                      # Esto está bien si '<-' y '=' son asignación y '==' es comparación.
                                      # Por ahora, mantendremos ASIGNACION como r'<-|=' (ver más abajo)

    ('OP_MENOR_IGUAL', r'<='),
    ('OP_MAYOR_IGUAL', r'>='),
    ('OP_IGUAL', r'=='),              # Comparación explícita de igualdad
    ('OP_DISTINTO', r'<>|!='),

    # -- Identificadores y Literales --
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identificadores
    ('NUMERO_REAL', r'\d+\.\d*|\.\d+'), # Números reales (ANTES DE ENTEROS para capturar el punto)
    ('NUMERO_ENTERO', r'\d+'),         # Números enteros
    ('CADENA', r'"[^"]*"|\'[^\']*\''),  # Cadenas de texto

    # -- Operadores de un caracter y otros símbolos --
    # Aquí re-añadimos '=' a ASIGNACION si se decide que es un operador de asignación además de '<-'
    # Si ASIGNACION es solo '<-', entonces '=' podría ser para comparación (OP_IGUAL podría ser solo '=')
    # Para mantener la flexibilidad de PSeInt y la simplicidad actual del parser:
    # Hacemos que ASIGNACION maneje ambos, pero '<-' debe ir primero en su propia regex si lo separamos.
    # Mejor mantener la regex original ('ASIGNACION', r'<-|='), que el lexer prueba como un todo.
    # La redefinición de ASIGNACION arriba fue solo para pensar el orden. Volvamos a la original:
    # ('ASIGNACION', r'<-|='), # Ya definido en REGEX_TOKENS a través de PALABRAS_CLAVE no, está en TOKEN_TIPOS.
    # La clave es el orden GLOBAL de REGEX_TOKENS.
    # Re-escribo la lista de TOKEN_TIPOS para claridad de orden:

    # (COMENTARIO ya está arriba)
    # ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'), # (ya arriba)
    # ('NUMERO_REAL', r'\d+\.\d*|\.\d+'), # (ya arriba)
    # ('NUMERO_ENTERO', r'\d+'), # (ya arriba)
    # ('CADENA', r'"[^"]*"|\'[^\']*\''), # (ya arriba)

    # Re-declarando ASIGNACION aquí para asegurar que está en la lista.
    # Si '<-' y '=' son asignación, y '==' es comparación:
    ('ASIGNACION', r'<-|='),       # Este orden dentro de la OR (|) es importante también. '<-' antes que '=' si hay ambigüedad.

    ('OP_SUMA', r'\+'),
    ('OP_RESTA', r'-'),
    ('OP_MULT', r'\*'),
    ('OP_DIV', r'/'),               # Ahora '/' solo, después de '//' (COMENTARIO)
    ('OP_POT', r'\^'),
    ('OP_MOD', r'%|(?i:\bMOD\b)'),   # '%', o la palabra MOD (case-insensitive)

    # (Operadores de comparación de dos caracteres ya están arriba)
    ('OP_MENOR', r'<'),
    ('OP_MAYOR', r'>'),

    ('PARENTESIS_IZQ', r'\('),
    ('PARENTESIS_DER', r'\)'),
    ('CORCHETE_IZQ', r'\['),
    ('CORCHETE_DER', r'\]'),
    ('COMA', r','),
    ('PUNTOYCOMA', r';'),
    ('DOSPUNTOS', r':'),

    ('NUEVALINEA', r'\n'),
    ('ESPACIO', r'[ \t]+'),
    ('ERROR', r'.'), # Cualquier otro caracter es un error al final
]

# Construir la lista completa de tokens para el lexer, priorizando palabras clave
REGEX_TOKENS = []
# Palabras clave primero (case-insensitive)
for nombre_kw, tipo_kw in PALABRAS_CLAVE.items():
    # Manejar palabras clave que podrían ser prefijos de otras o contener operadores (ej. CONPASO)
    # Usar \b (word boundary) es crucial.
    REGEX_TOKENS.append((tipo_kw, r'(?i:\b' + nombre_kw + r'\b)'))

# Luego los otros tipos de token en el orden definido en TOKEN_TIPOS
REGEX_TOKENS.extend(TOKEN_TIPOS)

# Tooltips para comandos (simplificado)
COMMAND_TOOLTIPS = {
    "ALGORITMO": "Inicia la definición de un algoritmo. Ej: ALGORITMO MiPrograma",
    "FINALGORITMO": "Finaliza la definición de un algoritmo.",
    "DEFINA": "Define una o más variables. Ej: DEFINA variable COMO TIPO",
    "ENTERO": "Tipo de dato para números enteros.",
    "REAL": "Tipo de dato para números con decimales.",
    "LOGICO": "Tipo de dato para valores Verdadero o Falso.",
    "TEXTO": "Tipo de dato para cadenas de caracteres.",
    "MUESTRE": "Muestra un valor o mensaje en la salida. Ej: MUESTRE 'Hola'",
    "LEA": "Lee un valor ingresado por el usuario. Ej: LEA miVariable",
    "SI": "Inicia una estructura condicional. Ej: SI condicion ENTONCES ... SINO ... FINSI",
    "ENTONCES": "Palabra clave usada con SI.",
    "SINO": "Parte opcional de una estructura SI para la condición falsa.",
    "FINSI": "Finaliza una estructura SI.",
    "MIENTRAS": "Inicia un ciclo mientras una condición sea verdadera. Ej: MIENTRAS condicion HAGA ... FINMIENTRAS",
    "HAGA": "Palabra clave usada con MIENTRAS.",
    "FINMIENTRAS": "Finaliza un ciclo MIENTRAS.",
    "REPITA": "Inicia un ciclo que se ejecuta al menos una vez. Ej: REPITA ... HASTAQUE condicion",
    "HASTAQUE": "Condición de salida para un ciclo REPITA.",
    "PARA": "Inicia un ciclo con contador. Ej: PARA variable <- valor_inicial HASTA valor_final CONPASO paso HAGA ... FINPARA",
    "HASTA": "Límite superior en un ciclo PARA.",
    "CONPASO": "Incremento/decremento en un ciclo PARA.",
    "FINPARA": "Finaliza un ciclo PARA.",
    "FUNCION": "Define una función o subproceso. Ej: FUNCION miFuncion(arg1, arg2) ... FINFUNCION",
    "FINFUNCION": "Finaliza la definición de una función.",
}

# Sugerencias para autocompletado (simplificado, solo palabras clave)
AUTOCOMPLETE_SUGGESTIONS = list(PALABRAS_CLAVE.keys()) + [
    "VERDADERO", "FALSO" # Añadir valores lógicos también
]

if __name__ == '__main__':
    # Para pruebas rápidas del módulo
    print("Palabras Clave Colombianas:")
    for kw, token_name in PALABRAS_CLAVE.items():
        print(f"  {kw} -> {token_name}")
    print("\nSugerencias de autocompletado:")
    print(AUTOCOMPLETE_SUGGESTIONS)
    print(f"\nTooltip para 'MUESTRE': {COMMAND_TOOLTIPS.get('MUESTRE')}")