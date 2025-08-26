# pseint_colombiano/utils/syntax_highlighter.py
"""
Módulo para el resaltado de sintaxis básico en un CTkTextbox.
"""
import re
from core.keywords_col import PALABRAS_CLAVE # Ajusta la importación según tu estructura

class SyntaxHighlighter:
    def __init__(self, textbox):
        self.textbox = textbox
        self.configure_tags()
        self.patterns = self._build_patterns()

    def configure_tags(self):
        """Configura los tags de color para el resaltado."""
        # Colores para tema claro (puedes ajustarlos)
        self.textbox.tag_config("keyword", foreground="#0000FF") # Azul para palabras clave
        self.textbox.tag_config("comment", foreground="#008000") # Verde para comentarios
        self.textbox.tag_config("string", foreground="#A31515")  # Rojo oscuro para cadenas
        self.textbox.tag_config("number", foreground="#098658")  # Verde azulado para números
        self.textbox.tag_config("type", foreground="#2B91AF")    # Cian para tipos de dato
        self.textbox.tag_config("function_def", foreground="#795E26") # Marrón para def de función/algoritmo
        
        # TODO: Añadir colores específicos para tema oscuro y cambiar dinámicamente

    def _build_patterns(self):
        """Construye los patrones regex para el resaltado."""
        # Construir regex para palabras clave, asegurando que sean palabras completas (word boundaries \b)
        # Hacerlo insensible a mayúsculas y minúsculas con (?i)
        keywords_plain = [kw for kw in PALABRAS_CLAVE.keys() if not PALABRAS_CLAVE[kw].startswith("TIPO_") and kw not in ["ALGORITMO", "PROCESO", "FUNCION", "SUBPROCESO"]]
        keyword_pattern = r"(?i)\b(" + "|".join(keywords_plain) + r")\b"
        
        types_plain = [kw for kw, token_name in PALABRAS_CLAVE.items() if token_name.startswith("TIPO_")]
        type_pattern = r"(?i)\b(" + "|".join(types_plain) + r")\b"

        # Patrón para ALGORITMO, PROCESO, FUNCION, SUBPROCESO
        func_def_keywords = ["ALGORITMO", "PROCESO", "FUNCION", "SUBPROCESO"]
        func_def_pattern = r"(?i)\b(" + "|".join(func_def_keywords) + r")\b"

        comment_pattern = r"//[^\n]*"
        string_pattern = r'"[^"]*"|\'[^\']*\''
        number_pattern = r"\b\d+\.?\d*\b|\b\.\d+\b" # Números enteros y reales

        return {
            "keyword": re.compile(keyword_pattern),
            "type": re.compile(type_pattern),
            "function_def": re.compile(func_def_pattern),
            "comment": re.compile(comment_pattern),
            "string": re.compile(string_pattern),
            "number": re.compile(number_pattern),
        }

    def highlight(self, event=None):
        """Aplica el resaltado de sintaxis al contenido del textbox."""
        content = self.textbox.get("1.0", "end-1c")
        
        # Limpiar tags existentes para evitar solapamientos incorrectos
        for tag in self.patterns.keys():
            self.textbox.tag_remove(tag, "1.0", "end")

        # Aplicar tags según los patrones, de más específico a más general
        # o manejar el orden para que no se pisen mal.
        # Los comentarios deben ir primero para que no se resalten keywords dentro de ellos.
        self._apply_tag_for_pattern(content, "comment", self.patterns["comment"])
        self._apply_tag_for_pattern(content, "string", self.patterns["string"])
        self._apply_tag_for_pattern(content, "keyword", self.patterns["keyword"])
        self._apply_tag_for_pattern(content, "type", self.patterns["type"])
        self._apply_tag_for_pattern(content, "function_def", self.patterns["function_def"])
        self._apply_tag_for_pattern(content, "number", self.patterns["number"])

    def _apply_tag_for_pattern(self, content, tag_name, pattern):
        for match in pattern.finditer(content):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            self.textbox.tag_add(tag_name, start_index, end_index)

    def update_highlighting_for_theme(self, theme_mode):
        """Actualiza los colores de los tags según el tema."""
        if theme_mode == "dark":
            self.textbox.tag_config("keyword", foreground="#569CD6")
            self.textbox.tag_config("comment", foreground="#6A9955")
            self.textbox.tag_config("string", foreground="#CE9178")
            self.textbox.tag_config("number", foreground="#B5CEA8")
            self.textbox.tag_config("type", foreground="#4EC9B0")
            self.textbox.tag_config("function_def", foreground="#DCDCAA")
        else: # light
            self.textbox.tag_config("keyword", foreground="#0000FF")
            self.textbox.tag_config("comment", foreground="#008000")
            self.textbox.tag_config("string", foreground="#A31515")
            self.textbox.tag_config("number", foreground="#098658")
            self.textbox.tag_config("type", foreground="#2B91AF")
            self.textbox.tag_config("function_def", foreground="#795E26")
        
        # Reaplicar el resaltado para que los nuevos colores tomen efecto en el texto existente
        self.highlight()

if __name__ == '__main__':
    # Ejemplo de uso (requiere un root de CTk y un CTkTextbox)
    import customtkinter as ctk

    app = ctk.CTk()
    app.geometry("600x400")
    app.title("Syntax Highlighter Test")

    ctk.set_appearance_mode("light") # o "dark"

    textbox = ctk.CTkTextbox(app, font=("Consolas", 12), wrap="none")
    textbox.pack(expand=True, fill="both", padx=10, pady=10)
    
    highlighter = SyntaxHighlighter(textbox)
    textbox.bind("<KeyRelease>", highlighter.highlight) # Resaltar al soltar tecla

    sample_code = """ALGORITMO MiPrueba
    // Este es un comentario
    DEFINA saludo COMO TEXTO
    DEFINA numero COMO ENTERO
    
    saludo = "Hola, mundo!"
    numero = 123 + 45.67
    
    MUESTRE saludo
    MUESTRE numero
    
    SI numero > 100 ENTONCES
        MUESTRE "Es grande"
    SINO
        MUESTRE "Es pequeño"
    FINSI
FINALGORITMO
"""
    textbox.insert("1.0", sample_code)
    highlighter.highlight() # Resaltado inicial

    def toggle_theme():
        current_mode = ctk.get_appearance_mode()
        new_mode = "dark" if current_mode == "Light" else "light"
        ctk.set_appearance_mode(new_mode)
        highlighter.update_highlighting_for_theme(new_mode.lower())


    theme_button = ctk.CTkButton(app, text="Cambiar Tema", command=toggle_theme)
    theme_button.pack(pady=5)

    app.mainloop()