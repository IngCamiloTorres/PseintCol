# pseint_colombiano/core/ast_nodes.py
"""
Definición de los nodos para el Árbol de Sintaxis Abstracta (AST).
Cada nodo representa una construcción del lenguaje.
"""

class ASTNode:
    """Clase base para todos los nodos del AST."""
    pass

class ProgramaNode(ASTNode):
    """Nodo raíz que representa todo el algoritmo."""
    def __init__(self, nombre_algoritmo, cuerpo):
        self.nombre_algoritmo = nombre_algoritmo # Token ID
        self.cuerpo = cuerpo # Lista de sentencias

    def __repr__(self):
        return f"ProgramaNode(nombre='{self.nombre_algoritmo.value}', cuerpo=[...])"

class DefinicionVariableNode(ASTNode):
    """Nodo para 'DEFINA variable COMO TIPO'."""
    def __init__(self, variables, tipo):
        self.variables = variables # Lista de Tokens ID
        self.tipo = tipo # Token TIPO (TIPO_ENTERO, TIPO_TEXTO, etc.)

    def __repr__(self):
        var_names = [v.value for v in self.variables]
        return f"DefinicionVariableNode(variables={var_names}, tipo='{self.tipo.value}')"

class MuestreNode(ASTNode):
    """Nodo para 'MUESTRE expresion1, expresion2, ...'."""
    def __init__(self, expresiones):
        self.expresiones = expresiones # Lista de nodos de expresión

    def __repr__(self):
        return f"MuestreNode(expresiones=[...])"

class LeaNode(ASTNode):
    """Nodo para 'LEA variable'."""
    def __init__(self, variable):
        self.variable = variable # Token ID

    def __repr__(self):
        return f"LeaNode(variable='{self.variable.value}')"

class AsignacionNode(ASTNode):
    """Nodo para 'variable = expresion' o 'variable <- expresion'."""
    def __init__(self, variable, expresion):
        self.variable = variable # Token ID
        self.expresion = expresion # Nodo de expresión

    def __repr__(self):
        return f"AsignacionNode(variable='{self.variable.value}', expresion=...)"
        
class SiNode(ASTNode):
    """Nodo para 'SI condicion ENTONCES cuerpo_si [SINO cuerpo_sino] FINSI'."""
    def __init__(self, condicion, cuerpo_si, cuerpo_sino=None):
        self.condicion = condicion # Nodo de expresión
        self.cuerpo_si = cuerpo_si # Lista de sentencias
        self.cuerpo_sino = cuerpo_sino # Lista de sentencias o None

    def __repr__(self):
        return f"SiNode(condicion=..., cuerpo_si=[...], cuerpo_sino={'[...]' if self.cuerpo_sino else 'None'})"

# --- Nodos de Expresión ---
class LiteralNode(ASTNode):
    """Nodo para un valor literal (número, cadena, lógico)."""
    def __init__(self, token):
        self.token = token
        self.value = token.value
        # Convertir el valor al tipo Python apropiado
        if token.type == 'NUMERO_ENTERO':
            self.value = int(token.value)
        elif token.type == 'NUMERO_REAL':
            self.value = float(token.value)
        elif token.type == 'CADENA':
            self.value = token.value[1:-1] # Quitar comillas
        elif token.type == 'VALOR_VERDADERO':
            self.value = True
        elif token.type == 'VALOR_FALSO':
            self.value = False


    def __repr__(self):
        return f"LiteralNode(type='{self.token.type}', value={self.value})"

class VariableNode(ASTNode):
    """Nodo para una referencia a una variable."""
    def __init__(self, token_id):
        self.token_id = token_id # Token ID
        self.nombre = token_id.value

    def __repr__(self):
        return f"VariableNode(nombre='{self.nombre}')"

class OperacionBinariaNode(ASTNode):
    """Nodo para una operación binaria (ej. a + b)."""
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda # Nodo de expresión
        self.operador = operador # Token de operador
        self.derecha = derecha # Nodo de expresión

    def __repr__(self):
        return f"OperacionBinariaNode(izquierda=..., op='{self.operador.value}', derecha=...)"

# TODO: Añadir más nodos según sea necesario:
# MientrasNode, ParaNode, RepitaNode, FuncionDefNode, FuncionCallNode, ArregloAccesoNode, etc.