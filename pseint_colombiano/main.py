# pseint_colombiano/main.py
"""
Punto de entrada principal para la aplicación PseudoCol.
"""
import customtkinter as ctk
from gui.main_window import MainWindow # Asegúrate que la ruta sea correcta

# Configuración inicial de CustomTkinter (opcional, pero bueno tenerla)
ctk.set_appearance_mode("System")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # Opciones: "blue", "green", "dark-blue"

def main():
    """Función principal para iniciar la aplicación."""
    try:
        app = MainWindow()
        app.mainloop()
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas y que la estructura del proyecto sea correcta.")
        print("Intenta ejecutar 'pip install -r requirements.txt' desde la raíz del proyecto.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al iniciar la aplicación: {e}")
        # En una aplicación real, podrías registrar este error en un archivo.

if __name__ == "__main__":
    main()