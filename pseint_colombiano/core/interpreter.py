# pseint_colombiano/core/interpreter.py
"""
Intérprete para el AST del pseudocódigo colombiano.
Ejecuta el árbol de sintaxis abstracta.
"""
from .ast_nodes import (
    ProgramaNode, DefinicionVariableNode, MuestreNode, LeaNode,
    AsignacionNode, SiNode, LiteralNode, VariableNode, OperacionBinariaNode
)
from .symbol_table import SymbolTable
from .pseudo_error import PseudoRuntimeError

class Interpreter:
    """
    Interpreta un AST y ejecuta el pseudocódigo.
    Utiliza un patrón Visitor para recorrer los nodos del AST.
    """
    def __init__(self, console_input_func=None, console_output_func=None):
        self.symbol_table = SymbolTable()
        self.console_input = console_input_func or input  # Para pruebas o integración GUI
        self.console_output = console_output_func or print # Para pruebas o integración GUI

    def interpret(self, ast_node):
        """Inicia la interpretación desde el nodo raíz del AST."""
        if ast_node is None:
            self.console_output("Error: No se pudo generar el AST para interpretar.")
            return
        try:
            return self._visit(ast_node)
        except PseudoRuntimeError as e:
            self.console_output(f"Error de Ejecución: {e}")
        except Exception as e:
            self.console_output(f"Error Inesperado en Intérprete: {e}")


    def _visit(self, node):
        """Método visitor genérico que llama al método específico para el tipo de nodo."""
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise PseudoRuntimeError(f"No hay método _visit_{type(node).__name__} definido y _generic_visit no lo maneja.")

    def _visit_ProgramaNode(self, node: ProgramaNode):
        # self.console_output(f"--- Ejecutando Algoritmo: {node.nombre_algoritmo.value} ---")
        for sentencia in node.cuerpo:
            self._visit(sentencia)
        # self.console_output(f"--- Fin Algoritmo: {node.nombre_algoritmo.value} ---")


    def _visit_DefinicionVariableNode(self, node: DefinicionVariableNode):
        tipo_dato_str = node.tipo.value.upper() # TEXTO, ENTERO, REAL, LOGICO
        # En PSeInt, la definición solo declara. La inicialización es implícita (0, "", Falso) o por asignación.
        for var_token in node.variables:
            var_nombre = var_token.value
            # PSeInt inicializa automáticamente: números a 0, lógicos a Falso, texto a ""
            default_value = None
            if tipo_dato_str == "ENTERO" or tipo_dato_str == "REAL":
                default_value = 0
            elif tipo_dato_str == "TEXTO":
                default_value = ""
            elif tipo_dato_str == "LOGICO":
                default_value = False
            else:
                raise PseudoRuntimeError(f"Tipo de dato desconocido '{tipo_dato_str}' para '{var_nombre}'")
            
            self.symbol_table.define(var_nombre, default_value, tipo_dato_str)


    def _visit_MuestreNode(self, node: MuestreNode):
        output_parts = []
        for expr_node in node.expresiones:
            value = self._visit(expr_node)
            output_parts.append(str(value))
        self.console_output("".join(output_parts)) # PSeInt concatena sin espacios por defecto

    def _visit_LeaNode(self, node: LeaNode):
        var_nombre = node.variable.value
        if not self.symbol_table.exists(var_nombre):
            raise PseudoRuntimeError(f"Variable '{var_nombre}' no ha sido definida antes de LEA.")
        
        # Prompt para la entrada. En PSeInt no hay prompt explícito en LEA,
        # la GUI debe manejar cómo se pide la entrada.
        # Para la consola, podemos hacer un input simple.
        # No incluimos un mensaje en el input() porque PSeInt no lo hace;
        # el MUESTRE previo es el que debe dar el contexto.
        raw_input = self.console_input()
        
        # Intentar convertir al tipo de la variable (PSeInt es flexible aquí)
        var_type = self.symbol_table.get_type(var_nombre)
        converted_value = None
        try:
            if var_type == "ENTERO":
                converted_value = int(raw_input)
            elif var_type == "REAL":
                converted_value = float(raw_input)
            elif var_type == "LOGICO":
                # PSeInt es flexible, "verdadero", "falso", 1, 0
                if raw_input.lower() in ["verdadero", "v", "true", "t", "1"]:
                    converted_value = True
                elif raw_input.lower() in ["falso", "f", "false", "0"]:
                    converted_value = False
                else:
                    raise ValueError("Entrada no es un valor lógico válido.")
            elif var_type == "TEXTO":
                converted_value = str(raw_input)
            else: # Seguridad
                converted_value = raw_input
        except ValueError:
            raise PseudoRuntimeError(f"Entrada '{raw_input}' no es válida para la variable '{var_nombre}' de tipo {var_type}.")

        self.symbol_table.assign(var_nombre, converted_value)

    def _visit_AsignacionNode(self, node: AsignacionNode):
        var_nombre = node.variable.value
        if not self.symbol_table.exists(var_nombre):
            # PSeInt permite asignación implícita en algunos contextos, pero es buena práctica definir.
            # Por ahora, seremos estrictos.
            raise PseudoRuntimeError(f"Variable '{var_nombre}' no ha sido definida antes de asignarle un valor.")

        valor_expresion = self._visit(node.expresion)
        
        # Validación de tipo (simplificada)
        var_type = self.symbol_table.get_type(var_nombre)
        val_py_type = type(valor_expresion)

        if var_type == "ENTERO" and not isinstance(valor_expresion, int):
             # PSeInt permite truncar reales a enteros, o convertir si es posible
            try:
                valor_expresion = int(valor_expresion)
            except (ValueError, TypeError):
                 raise PseudoRuntimeError(f"No se puede asignar valor '{valor_expresion}' (tipo {val_py_type.__name__}) a variable entera '{var_nombre}'.")
        elif var_type == "REAL" and not isinstance(valor_expresion, (int, float)):
            try:
                valor_expresion = float(valor_expresion)
            except (ValueError, TypeError):
                raise PseudoRuntimeError(f"No se puede asignar valor '{valor_expresion}' (tipo {val_py_type.__name__}) a variable real '{var_nombre}'.")
        elif var_type == "LOGICO" and not isinstance(valor_expresion, bool):
            raise PseudoRuntimeError(f"No se puede asignar valor '{valor_expresion}' (tipo {val_py_type.__name__}) a variable lógica '{var_nombre}'.")
        elif var_type == "TEXTO" and not isinstance(valor_expresion, str):
             # PSeInt convierte casi todo a texto para asignación a cadena
            valor_expresion = str(valor_expresion)


        self.symbol_table.assign(var_nombre, valor_expresion)

    def _visit_SiNode(self, node: SiNode):
        condicion_val = self._visit(node.condicion)
        if not isinstance(condicion_val, bool):
            raise PseudoRuntimeError(f"La condición del SI debe ser un valor lógico, se obtuvo {condicion_val} (tipo {type(condicion_val).__name__}).")

        if condicion_val: # Verdadero
            for sentencia in node.cuerpo_si:
                self._visit(sentencia)
        elif node.cuerpo_sino: # Falso y hay un SINO
            for sentencia in node.cuerpo_sino:
                self._visit(sentencia)

    # --- Visitantes para Nodos de Expresión ---
    def _visit_LiteralNode(self, node: LiteralNode):
        return node.value # El valor ya está convertido en el nodo

    def _visit_VariableNode(self, node: VariableNode):
        var_nombre = node.nombre
        if not self.symbol_table.exists(var_nombre):
            raise PseudoRuntimeError(f"Variable '{var_nombre}' no ha sido definida o usada antes de asignación.")
        return self.symbol_table.get(var_nombre)

    def _visit_OperacionBinariaNode(self, node: OperacionBinariaNode):
        val_izq = self._visit(node.izquierda)
        val_der = self._visit(node.derecha)
        op_tipo = node.operador.type

        # Aritméticos
        if op_tipo == 'OP_SUMA':
            # En PSeInt, la suma con cadenas es concatenación
            if isinstance(val_izq, str) or isinstance(val_der, str):
                return str(val_izq) + str(val_der)
            return val_izq + val_der
        elif op_tipo == 'OP_RESTA': return val_izq - val_der
        elif op_tipo == 'OP_MULT': return val_izq * val_der
        elif op_tipo == 'OP_DIV':
            if val_der == 0:
                raise PseudoRuntimeError("División por cero.")
            # PSeInt usualmente hace división real
            return float(val_izq) / float(val_der)
        elif op_tipo == 'OP_MOD':
            if val_der == 0:
                raise PseudoRuntimeError("Módulo por cero.")
            return val_izq % val_der
        elif op_tipo == 'OP_POT': return val_izq ** val_der
        
        # Comparación
        elif op_tipo == 'OP_IGUAL': return val_izq == val_der
        elif op_tipo == 'OP_DISTINTO': return val_izq != val_der
        elif op_tipo == 'OP_MENOR': return val_izq < val_der
        elif op_tipo == 'OP_MAYOR': return val_izq > val_der
        elif op_tipo == 'OP_MENOR_IGUAL': return val_izq <= val_der
        elif op_tipo == 'OP_MAYOR_IGUAL': return val_izq >= val_der

        # Lógicos
        elif op_tipo == 'OP_Y':
            if not (isinstance(val_izq, bool) and isinstance(val_der, bool)):
                 raise PseudoRuntimeError(f"Operador 'Y' requiere operandos lógicos. Se obtuvo {type(val_izq).__name__} y {type(val_der).__name__}")
            return val_izq and val_der
        elif op_tipo == 'OP_O':
            if not (isinstance(val_izq, bool) and isinstance(val_der, bool)):
                 raise PseudoRuntimeError(f"Operador 'O' requiere operandos lógicos. Se obtuvo {type(val_izq).__name__} y {type(val_der).__name__}")
            return val_izq or val_der
        
        # TODO: OP_NO es unario, necesitaría su propio nodo o manejo especial
        
        else:
            raise PseudoRuntimeError(f"Operador binario desconocido o no implementado: {node.operador.value} ({op_tipo})")

if __name__ == '__main__':
    from .lexer import Lexer
    from .parser import Parser
    
    codigo_ejemplo = """
    ALGORITMO PruebaCompleta
        DEFINA nombre COMO TEXTO
        DEFINA edad, anioActual, anioNacimiento COMO ENTERO
        DEFINA esMayor COMO LOGICO

        anioActual = 2025 // Asumimos año actual

        MUESTRE "¡Bienvenido al sistema!"
        MUESTRE "Por favor, ingrese su nombre:"
        LEA nombre
        MUESTRE "Ingrese su año de nacimiento:"
        LEA anioNacimiento

        edad = anioActual - anioNacimiento
        
        MUESTRE "Hola ", nombre, ", tienes ", edad, " años."

        Si edad >= 18 Entonces
            MUESTRE "Eres mayor de edad."
            esMayor = VERDADERO
        SiNo
            MUESTRE "Eres menor de edad."
            esMayor = FALSO
        FinSi

        Si esMayor Y (edad < 65) Entonces
            MUESTRE "Y estás en edad productiva."
        FinSi
        
        MUESTRE "Gracias por usar el sistema."
    FINALGORITMO
    """
    lexer = Lexer(codigo_ejemplo)
    tokens, errors_lex = lexer.tokenize()

    if errors_lex:
        print("Errores del Lexer:")
        for err in errors_lex: print(err)
    else:
        parser = Parser(tokens)
        ast, errors_par = parser.parse()

        if errors_par:
            print("\nErrores del Parser:")
            for err in errors_par: print(err)
        else:
            print("\n--- Iniciando Interpretación ---")
            # Para probar el LEA, necesitamos mockear input
            mock_inputs = ["Juan Perez", "1990"] # Nombre, Año Nacimiento
            
            # Buffer para la salida de MUESTRE
            output_buffer = []

            def mock_console_input():
                if mock_inputs:
                    val = mock_inputs.pop(0)
                    print(f"(Entrada simulada: {val})") # Para ver qué se está "ingresando"
                    return val
                return "" # Evitar error si se piden más inputs

            def mock_console_output(message):
                output_buffer.append(str(message))
                # print(f"(Salida: {message})") # Descomentar para depurar la salida en tiempo real

            interpreter = Interpreter(console_input_func=mock_console_input, 
                                      console_output_func=mock_console_output)
            interpreter.interpret(ast)
            
            print("\n--- Salida del Programa ---")
            for line in output_buffer:
                print(line)
            
            print("\n--- Estado Final de la Tabla de Símbolos ---")
            for name, data in interpreter.symbol_table.symbols.items():
                print(f"{name} ({data['type']}): {data['value']}")