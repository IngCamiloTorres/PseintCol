# pseint_colombiano/gui/theme_manager.py
"""
Gestor de temas para la aplicación (claro/oscuro).
"""
import customtkinter as ctk

class ThemeManager:
    def __init__(self, app_instance):
        self.app = app_instance # Referencia a la ventana principal o app
        self.current_theme = ctk.get_appearance_mode().lower() # "light" or "dark"

    def set_theme(self, theme_name: str):
        """Establece el tema de la aplicación."""
        if theme_name.lower() == "light":
            ctk.set_appearance_mode("Light")
            self.current_theme = "light"
        elif theme_name.lower() == "dark":
            ctk.set_appearance_mode("Dark")
            self.current_theme = "dark"
        elif theme_name.lower() == "system":
            ctk.set_appearance_mode("System")
            # Necesitamos obtener el modo actual del sistema para saber si es claro u oscuro
            # CustomTkinter no expone esto directamente, así que asumimos uno o lo dejamos
            # que la UI se actualice sola. Para el resaltador, podríamos necesitar una lógica más explícita.
            # Por ahora, el resaltador se actualizará basado en get_appearance_mode() después de set.
            effective_mode = ctk.get_appearance_mode().lower()
            self.current_theme = "dark" if "dark" in effective_mode.lower() else "light" # Simplificación
        else:
            print(f"Advertencia: Tema '{theme_name}' no reconocido.")
            return

        # Notificar a los componentes que necesiten actualizarse (ej. resaltador)
        if hasattr(self.app, 'editor_frame') and hasattr(self.app.editor_frame, 'highlighter'):
            self.app.editor_frame.highlighter.update_highlighting_for_theme(self.current_theme)
        
        # TODO: Actualizar otros elementos de la GUI que no se actualizan automáticamente
        # con customtkinter (si los hubiera).

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        if self.current_theme == "light":
            self.set_theme("dark")
        else:
            self.set_theme("light")

    def get_current_theme_mode(self):
        """Devuelve 'light' o 'dark' basado en el tema actual."""
        # Si el tema es "system", necesitamos determinar si es claro u oscuro.
        # Esta es una simplificación, una detección más robusta podría ser necesaria.
        effective_mode = ctk.get_appearance_mode() # Esto devuelve 'Light' o 'Dark'
        return "dark" if "Dark" in effective_mode else "light"


if __name__ == '__main__':
    app_mock = ctk.CTk()
    app_mock.title("Theme Manager Test")
    
    # Mockear editor_frame y highlighter para la prueba de notificación
    class MockEditorFrame:
        def __init__(self):
            self.highlighter = MockHighlighter()
    class MockHighlighter:
        def update_highlighting_for_theme(self, theme_mode):
            print(f"Highlighter notificado: cambiar a tema {theme_mode}")

    app_mock.editor_frame = MockEditorFrame()

    manager = ThemeManager(app_mock)
    
    print(f"Tema inicial: {manager.current_theme}, Modo Efectivo: {manager.get_current_theme_mode()}")

    def switch_to_dark():
        manager.set_theme("dark")
        print(f"Tema cambiado a: {manager.current_theme}, Modo Efectivo: {manager.get_current_theme_mode()}")

    def switch_to_light():
        manager.set_theme("light")
        print(f"Tema cambiado a: {manager.current_theme}, Modo Efectivo: {manager.get_current_theme_mode()}")
    
    def switch_to_system():
        manager.set_theme("system") # El resultado dependerá de tu config de OS
        print(f"Tema cambiado a: 'system', Modo Efectivo: {manager.get_current_theme_mode()}")


    ctk.CTkButton(app_mock, text="Tema Oscuro", command=switch_to_dark).pack(pady=5)
    ctk.CTkButton(app_mock, text="Tema Claro", command=switch_to_light).pack(pady=5)
    ctk.CTkButton(app_mock, text="Tema Sistema", command=switch_to_system).pack(pady=5)

    app_mock.mainloop()