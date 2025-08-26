# pseint_colombiano/core/symbol_table.py
"""
Tabla de Símbolos para el intérprete.
Almacena información sobre variables (y futuras funciones).
"""
from .pseudo_error import PseudoRuntimeError

class SymbolTable:
    """Gestiona los símbolos (variables, funciones) y sus valores/tipos."""
    def __init__(self, parent=None): # parent para anidamiento de ámbitos (scopes)
        self.symbols = {}
        self.parent = parent

    def define(self, name, value, var_type=None):
        """Define una nueva variable en el ámbito actual."""
        if name in self.symbols:
            # PSeInt permite redefinir, pero puede ser una advertencia.
            # print(f"Advertencia: Variable '{name}' ya definida. Redefiniendo.")
            pass # Permitir redefinición por ahora, como PSeInt flexible
        self.symbols[name] = {'value': value, 'type': var_type}

    def assign(self, name, value):
        """Asigna un valor a una variable existente."""
        if name in self.symbols:
            # Aquí se podría añadir verificación de tipos si el lenguaje es estrictamente tipado
            # o conversión de tipos si es flexible.
            # Por ahora, PSeInt es bastante flexible con los tipos después de la definición.
            current_type = self.symbols[name]['type']
            # Realizar conversiones si es necesario y posible, o lanzar error
            # Ejemplo: si current_type es 'ENTERO' y value es float, intentar convertir a int.
            # Esto se maneja mejor en el _visit_AsignacionNode del intérprete.
            self.symbols[name]['value'] = value
        elif self.parent:
            return self.parent.assign(name, value) # Buscar en ámbito padre
        else:
            raise PseudoRuntimeError(f"Error de asignación: Variable '{name}' no ha sido definida.")

    def get(self, name):
        """Obtiene el valor de una variable."""
        if name in self.symbols:
            return self.symbols[name]['value']
        elif self.parent:
            return self.parent.get(name)
        else:
            raise PseudoRuntimeError(f"Error de acceso: Variable '{name}' no ha sido definida o usada antes de asignación.")

    def get_type(self, name):
        """Obtiene el tipo de una variable."""
        if name in self.symbols:
            return self.symbols[name]['type']
        elif self.parent:
            return self.parent.get_type(name)
        else:
            raise PseudoRuntimeError(f"Error de tipo: Variable '{name}' no ha sido definida.")

    def exists(self, name, check_parent=True):
        """Verifica si una variable está definida en este ámbito o (opcionalmente) en padres."""
        if name in self.symbols:
            return True
        elif self.parent and check_parent:
            return self.parent.exists(name)
        return False

    def __repr__(self):
        return f"SymbolTable({self.symbols})"

if __name__ == '__main__':
    st = SymbolTable()
    st.define("x", 0, "ENTERO")
    st.define("nombre", "", "TEXTO")
    print(f"Tabla inicial: {st}")

    st.assign("x", 10)
    st.assign("nombre", "Ana")
    print(f"x: {st.get('x')}, tipo: {st.get_type('x')}")
    print(f"nombre: {st.get('nombre')}, tipo: {st.get_type('nombre')}")

    try:
        st.assign("y", 5) # Error, no definida
    except PseudoRuntimeError as e:
        print(f"Error esperado: {e}")

    try:
        print(st.get("z")) # Error, no definida
    except PseudoRuntimeError as e:
        print(f"Error esperado: {e}")

    # Prueba de ámbitos anidados (básico)
    global_st = SymbolTable()
    global_st.define("g_var", 100, "ENTERO")

    local_st = SymbolTable(parent=global_st)
    local_st.define("l_var", 20, "ENTERO")
    local_st.assign("g_var", 150) # Modifica g_var en el ámbito padre

    print(f"Local l_var: {local_st.get('l_var')}")
    print(f"Global g_var desde local: {local_st.get('g_var')}") # Accede a g_var del padre
    print(f"Global g_var original: {global_st.get('g_var')}")
    print(f"Existe 'g_var' en local (sin chequear padre)?: {local_st.exists('g_var', False)}")
    print(f"Existe 'g_var' en local (chequeando padre)?: {local_st.exists('g_var', True)}")