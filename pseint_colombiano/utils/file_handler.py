# pseint_colombiano/utils/file_handler.py
"""
Utilidades para manejar la carga y guardado de archivos de pseudocódigo.
"""
import tkinter as tk
from tkinter import filedialog

FILE_EXTENSION = ".pseudocol"
FILE_TYPES = [("Archivos PseudoCol", f"*{FILE_EXTENSION}"), ("Todos los archivos", "*.*")]

def abrir_archivo():
    """Abre un diálogo para seleccionar un archivo y devuelve su contenido y ruta."""
    filepath = filedialog.askopenfilename(
        defaultextension=FILE_EXTENSION,
        filetypes=FILE_TYPES
    )
    if not filepath:
        return None, None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
        return contenido, filepath
    except Exception as e:
        # Podrías usar un messagebox aquí si la GUI ya está activa
        print(f"Error al abrir archivo: {e}")
        return None, None

def guardar_archivo_como(contenido_actual, ventana_padre=None):
    """Abre un diálogo para guardar el contenido en un nuevo archivo."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=FILE_EXTENSION,
        filetypes=FILE_TYPES,
        parent=ventana_padre
    )
    if not filepath:
        return None
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenido_actual)
        return filepath
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return None

def guardar_archivo(filepath, contenido_actual, ventana_padre=None):
    """Guarda el contenido en el archivo especificado. Si no hay filepath, llama a guardar_archivo_como."""
    if not filepath:
        return guardar_archivo_como(contenido_actual, ventana_padre)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenido_actual)
        return filepath
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return None

if __name__ == '__main__':
    # Para probar esto, necesitas un root de Tkinter
    root = tk.Tk()
    root.withdraw() # No mostrar la ventana principal de Tk

    print("Probando abrir archivo...")
    content, fp = abrir_archivo()
    if content:
        print(f"Archivo abierto: {fp}")
        print(f"Contenido:\n{content[:100]}...") # Muestra primeros 100 caracteres

        print("\nProbando guardar archivo como...")
        new_fp = guardar_archivo_como("Este es un nuevo contenido de prueba.", root)
        if new_fp:
            print(f"Archivo guardado como: {new_fp}")

    root.destroy()