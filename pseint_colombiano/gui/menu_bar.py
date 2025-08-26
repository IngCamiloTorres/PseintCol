# pseint_colombiano/gui/menu_bar.py
"""
Define la barra de menú de la aplicación.
Tkinter no tiene un widget CTkMenuBar, así que usamos el Menú estándar de Tk.
"""
import tkinter as tk
from tkinter import Menu, messagebox
from utils import file_handler # Ajusta la ruta si es necesario
from core.keywords_col import COMMAND_TOOLTIPS # Para la ayuda de comandos

class AppMenuBar:
    def __init__(self, root_window, app_commands):
        """
        Inicializa la barra de menú.
        root_window: La ventana principal de CTk.
        app_commands: Un diccionario o objeto con los comandos que el menú llamará.
                      Ej: {'nuevo_archivo': app.nuevo_archivo_func, ...}
        """
        self.root = root_window
        self.commands = app_commands

        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar) # Asociar el menú con la ventana

        self._crear_menu_archivo()
        self._crear_menu_editar()
        self._crear_menu_ejecutar()
        self._crear_menu_apariencia()
        self._crear_menu_ayuda()

    def _crear_menu_archivo(self):
        menu_archivo = Menu(self.menubar, tearoff=0)
        menu_archivo.add_command(label="Nuevo", command=self.commands.get('nuevo_archivo'), accelerator="Ctrl+N")
        menu_archivo.add_command(label="Abrir...", command=self.commands.get('abrir_archivo'), accelerator="Ctrl+O")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Guardar", command=self.commands.get('guardar_archivo'), accelerator="Ctrl+S")
        menu_archivo.add_command(label="Guardar Como...", command=self.commands.get('guardar_archivo_como'), accelerator="Ctrl+Shift+S")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.commands.get('salir_app'))
        self.menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        # Atajos de teclado (bindings a nivel de ventana principal)
        self.root.bind_all("<Control-n>", lambda e: self.commands.get('nuevo_archivo')())
        self.root.bind_all("<Control-o>", lambda e: self.commands.get('abrir_archivo')())
        self.root.bind_all("<Control-s>", lambda e: self.commands.get('guardar_archivo')())
        self.root.bind_all("<Control-S>", lambda e: self.commands.get('guardar_archivo_como')()) # Shift+S

    def _crear_menu_editar(self):
        menu_editar = Menu(self.menubar, tearoff=0)
        menu_editar.add_command(label="Deshacer", command=self.commands.get('deshacer'), accelerator="Ctrl+Z")
        menu_editar.add_command(label="Rehacer", command=self.commands.get('rehacer'), accelerator="Ctrl+Y")
        menu_editar.add_separator()
        menu_editar.add_command(label="Cortar", command=self.commands.get('cortar'), accelerator="Ctrl+X")
        menu_editar.add_command(label="Copiar", command=self.commands.get('copiar'), accelerator="Ctrl+C")
        menu_editar.add_command(label="Pegar", command=self.commands.get('pegar'), accelerator="Ctrl+V")
        menu_editar.add_separator()
        menu_editar.add_command(label="Seleccionar Todo", command=self.commands.get('seleccionar_todo'), accelerator="Ctrl+A")
        # TODO: Añadir Buscar, Reemplazar
        self.menubar.add_cascade(label="Editar", menu=menu_editar)

    def _crear_menu_ejecutar(self):
        menu_ejecutar = Menu(self.menubar, tearoff=0)
        menu_ejecutar.add_command(label="Ejecutar Algoritmo", command=self.commands.get('ejecutar_algoritmo'), accelerator="F5")
        menu_ejecutar.add_command(label="Ejecutar Paso a Paso", command=self.commands.get('ejecutar_paso_a_paso'), accelerator="F8", state="disabled") # TODO
        menu_ejecutar.add_separator()
        menu_ejecutar.add_command(label="Limpiar Consola", command=self.commands.get('limpiar_consola'))
        self.menubar.add_cascade(label="Ejecutar", menu=menu_ejecutar)

        self.root.bind_all("<F5>", lambda e: self.commands.get('ejecutar_algoritmo')())
        # self.root.bind_all("<F8>", lambda e: self.commands.get('ejecutar_paso_a_paso')())


    def _crear_menu_apariencia(self):
        menu_apariencia = Menu(self.menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=self.commands.get('get_current_theme_mode', lambda: "light")()) # Obtener tema actual

        menu_apariencia.add_radiobutton(label="Tema Claro", variable=self.theme_var, value="light",
                                       command=lambda: self.commands.get('set_theme')("light"))
        menu_apariencia.add_radiobutton(label="Tema Oscuro", variable=self.theme_var, value="dark",
                                       command=lambda: self.commands.get('set_theme')("dark"))
        menu_apariencia.add_radiobutton(label="Tema del Sistema", variable=self.theme_var, value="system",
                                       command=lambda: self.commands.get('set_theme')("system"))
        self.menubar.add_cascade(label="Apariencia", menu=menu_apariencia)

    def update_theme_selection(self, theme_mode):
        """Actualiza la selección del radio button del tema."""
        self.theme_var.set(theme_mode)


    def _crear_menu_ayuda(self):
        menu_ayuda = Menu(self.menubar, tearoff=0)
        
        # Submenú para ayuda de comandos
        ayuda_comandos_menu = Menu(menu_ayuda, tearoff=0)
        # Ordenar comandos para el menú
        sorted_commands = sorted(COMMAND_TOOLTIPS.keys())
        for cmd in sorted_commands:
            tooltip = COMMAND_TOOLTIPS[cmd]
            # Limitar longitud del tooltip en el menú o usar un diálogo
            ayuda_comandos_menu.add_command(label=cmd, command=lambda c=cmd, t=tooltip: self._mostrar_ayuda_comando(c, t))
        
        menu_ayuda.add_cascade(label="Ayuda de Comandos", menu=ayuda_comandos_menu)
        menu_ayuda.add_separator()
        menu_ayuda.add_command(label="Acerca de PseudoCol...", command=self.commands.get('mostrar_acerca_de'))
        self.menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

    def _mostrar_ayuda_comando(self, comando, descripcion):
        """Muestra un messagebox con la ayuda del comando."""
        messagebox.showinfo(f"Ayuda: {comando}", f"Comando: {comando}\n\nDescripción:\n{descripcion}", parent=self.root)


if __name__ == '__main__':
    import customtkinter as ctk

    app_root = ctk.CTk()
    app_root.geometry("600x400")
    app_root.title("MenuBar Test")
    ctk.set_appearance_mode("System") # o Light, Dark

    # Funciones de comando mock (simuladas)
    def mock_nuevo(): print("Comando: Nuevo Archivo")
    def mock_abrir(): print("Comando: Abrir Archivo")
    def mock_guardar(): print("Comando: Guardar Archivo")
    def mock_guardar_como(): print("Comando: Guardar Archivo Como")
    def mock_salir(): app_root.quit()
    def mock_deshacer(): print("Comando: Deshacer")
    def mock_rehacer(): print("Comando: Rehacer")
    def mock_cortar(): print("Comando: Cortar")
    def mock_copiar(): print("Comando: Copiar")
    def mock_pegar(): print("Comando: Pegar")
    def mock_seleccionar_todo(): print("Comando: Seleccionar Todo")
    def mock_ejecutar(): print("Comando: Ejecutar Algoritmo")
    def mock_paso_a_paso(): print("Comando: Ejecutar Paso a Paso")
    def mock_limpiar_consola(): print("Comando: Limpiar Consola")
    
    current_theme_mode = ctk.get_appearance_mode().lower()

    def mock_set_theme(theme):
        print(f"Comando: Establecer Tema a {theme}")
        ctk.set_appearance_mode(theme)
        # Actualizar el menú si el tema fue cambiado por otro lado
        menubar_instance.update_theme_selection(theme.lower())
        # En una app real, esto también actualizaría el resaltador, etc.
        global current_theme_mode
        current_theme_mode = theme.lower()


    def mock_get_current_theme():
        # Esto es un poco circular para el test, pero simula la app guardando el estado
        return current_theme_mode


    def mock_acerca_de():
        messagebox.showinfo("Acerca de", "PseudoCol Test v0.1\nUn simple test de Menú.", parent=app_root)

    mock_commands = {
        'nuevo_archivo': mock_nuevo, 'abrir_archivo': mock_abrir,
        'guardar_archivo': mock_guardar, 'guardar_archivo_como': mock_guardar_como,
        'salir_app': mock_salir,
        'deshacer': mock_deshacer, 'rehacer': mock_rehacer,
        'cortar': mock_cortar, 'copiar': mock_copiar, 'pegar': mock_pegar,
        'seleccionar_todo': mock_seleccionar_todo,
        'ejecutar_algoritmo': mock_ejecutar, 'ejecutar_paso_a_paso': mock_paso_a_paso,
        'limpiar_consola': mock_limpiar_consola,
        'set_theme': mock_set_theme,
        'get_current_theme_mode': mock_get_current_theme, # Para inicializar el radio button
        'mostrar_acerca_de': mock_acerca_de,
    }

    menubar_instance = AppMenuBar(app_root, mock_commands)
    
    # Inicializar el tema en el menú
    menubar_instance.update_theme_selection(ctk.get_appearance_mode().lower())


    ctk.CTkLabel(app_root, text="Ventana principal con Menú Estándar de Tkinter").pack(padx=20, pady=20)
    app_root.mainloop()