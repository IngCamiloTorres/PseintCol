# pseint_colombiano/gui/main_window.py
"""
Ventana principal de la aplicación PseudoCol.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, PanedWindow
import os

import tkinter as tk

from .editor_frame import EditorFrame
from .console_frame import ConsoleFrame
from .menu_bar import AppMenuBar
from .theme_manager import ThemeManager
from utils import file_handler # Ajusta la ruta si es necesario
from core.lexer import Lexer # Ajusta la ruta
from core.parser import Parser # Ajusta la ruta
from core.interpreter import Interpreter # Ajusta la ruta
import threading # Para ejecutar el intérprete en un hilo separado

APP_NAME = "PseudoCol Uni"
APP_VERSION = "0.1.0"

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}")
        self.geometry("900x700")
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Manejar cierre de ventana

        self.current_filepath = None
        self.unsaved_changes = False

        self.theme_manager = ThemeManager(self)
        self.theme_manager.set_theme("system") # O "light", "dark"

        self._setup_ui()
        self._setup_menu()
        
        # Estado para la ejecución
        self.interpreter_thread = None
        self.is_running = False


    def _setup_ui(self):
        """Configura la interfaz de usuario principal con paneles."""
        # PanedWindow para dividir editor y consola
        # Usamos el PanedWindow de tkinter ya que CTk no tiene uno directamente,
        # pero se puede estilizar o encapsular si es necesario.
        self.paned_window = PanedWindow(self, orient=ctk.VERTICAL, sashrelief=ctk.RAISED, bd=2)
        self.paned_window.pack(expand=True, fill="both")

        self.editor_frame = EditorFrame(self.paned_window)
        # self.editor_frame.pack(expand=True, fill="both") # No pack, añadir a paned_window
        self.paned_window.add(self.editor_frame, minsize=200) # minsize para evitar que se colapse

        self.console_frame = ConsoleFrame(self.paned_window)
        # self.console_frame.pack(expand=True, fill="both", pady=(5,0)) # No pack
        self.paned_window.add(self.console_frame, minsize=100)

        # Ajustar la proporción inicial (ej. 70% editor, 30% consola)
        self.paned_window.sash_place(0, 0, int(self.winfo_height() * 0.7)) # Esto es un poco tentativo al inicio
        self.after(100, lambda: self.paned_window.sash_place(0, 0, int(self.winfo_height() * 0.7)))


    def _setup_menu(self):
        """Configura la barra de menú."""
        app_commands = {
            'nuevo_archivo': self.cmd_nuevo_archivo,
            'abrir_archivo': self.cmd_abrir_archivo,
            'guardar_archivo': self.cmd_guardar_archivo,
            'guardar_archivo_como': self.cmd_guardar_archivo_como,
            'salir_app': self._on_closing,
            'deshacer': self.cmd_deshacer,
            'rehacer': self.cmd_rehacer,
            'cortar': self.cmd_cortar,
            'copiar': self.cmd_copiar,
            'pegar': self.cmd_pegar,
            'seleccionar_todo': self.cmd_seleccionar_todo,
            'ejecutar_algoritmo': self.cmd_ejecutar_algoritmo,
            'ejecutar_paso_a_paso': self.cmd_ejecutar_paso_a_paso, # Placeholder
            'limpiar_consola': self.cmd_limpiar_consola,
            'set_theme': self.cmd_set_theme,
            'get_current_theme_mode': lambda: self.theme_manager.get_current_theme_mode(),
            'mostrar_acerca_de': self.cmd_mostrar_acerca_de,
        }
        self.menu = AppMenuBar(self, app_commands)

    def _update_title(self):
        """Actualiza el título de la ventana con el nombre del archivo y estado de guardado."""
        filename = os.path.basename(self.current_filepath) if self.current_filepath else "Sin Título"
        dirty_marker = "*" if self.unsaved_changes else ""
        self.title(f"{filename}{dirty_marker} - {APP_NAME}")

    def set_unsaved_changes(self,狀態):
        if self.unsaved_changes != 狀態:
            self.unsaved_changes = 狀態
            self._update_title()

    # --- Comandos de Menú ---
    def cmd_nuevo_archivo(self):
        if self.unsaved_changes:
            if not messagebox.askyesno("Guardar Cambios", 
                                       "Tiene cambios sin guardar. ¿Desea guardarlos antes de crear un nuevo archivo?",
                                       parent=self):
                # Si el usuario dice NO a guardar, o si falla el guardado, no continuar.
                # Si dice SÍ y el guardado es exitoso, cmd_guardar_archivo manejará el resto.
                # La lógica aquí es: si no quiere guardar, simplemente no guardamos.
                pass # Continuar para limpiar
            else: # Usuario quiere guardar
                if not self.cmd_guardar_archivo():
                    return # Guardado cancelado o fallido, no continuar.
        
        self.editor_frame.clear_content()
        self.console_frame.clear_output()
        self.current_filepath = None
        self.set_unsaved_changes(False)


    def cmd_abrir_archivo(self):
        if self.unsaved_changes:
            if not messagebox.askyesno("Guardar Cambios", 
                                       "Tiene cambios sin guardar. ¿Desea guardarlos antes de abrir otro archivo?",
                                       parent=self):
                pass
            else:
                if not self.cmd_guardar_archivo():
                    return
        
        contenido, filepath = file_handler.abrir_archivo()
        if contenido is not None and filepath:
            self.editor_frame.set_content(contenido)
            self.current_filepath = filepath
            self.set_unsaved_changes(False)
            self.console_frame.clear_output()

    def cmd_guardar_archivo(self):
        if not self.current_filepath:
            return self.cmd_guardar_archivo_como()
        else:
            contenido = self.editor_frame.get_content()
            filepath = file_handler.guardar_archivo(self.current_filepath, contenido, self)
            if filepath:
                self.current_filepath = filepath
                self.set_unsaved_changes(False)
                # messagebox.showinfo("Guardado", "Archivo guardado exitosamente.", parent=self)
                return True
            else:
                messagebox.showerror("Error", "No se pudo guardar el archivo.", parent=self)
                return False

    def cmd_guardar_archivo_como(self):
        contenido = self.editor_frame.get_content()
        filepath = file_handler.guardar_archivo_como(contenido, self)
        if filepath:
            self.current_filepath = filepath
            self.set_unsaved_changes(False)
            # messagebox.showinfo("Guardado", f"Archivo guardado como {os.path.basename(filepath)}", parent=self)
            return True
        return False # Usuario canceló o hubo error

    def _on_closing(self):
        if self.is_running:
            messagebox.showwarning("Ejecución en Progreso", 
                                   "Un algoritmo se está ejecutando. Por favor, espere a que termine o deténgalo.", 
                                   parent=self)
            return

        if self.unsaved_changes:
            respuesta = messagebox.askyesnocancel("Salir", 
                                                "Tiene cambios sin guardar. ¿Desea guardarlos antes de salir?",
                                                parent=self)
            if respuesta is True: # Sí (guardar)
                if not self.cmd_guardar_archivo():
                    return # No salir si el guardado falla o se cancela
            elif respuesta is None: # Cancelar
                return
        self.destroy()

    # Comandos de Edición (básicos, usan eventos de widget de texto)
    def _get_focused_text_widget(self):
        focused = self.focus_get()
        if isinstance(focused, ctk.CTkTextbox): return focused
        if isinstance(focused, ctk.CTkEntry): return focused
        # Por defecto, el editor si no hay otro foco de texto claro
        return self.editor_frame.editor

    def cmd_deshacer(self):
        widget = self._get_focused_text_widget()
        if hasattr(widget, 'edit_undo'):
            try: widget.edit_undo()
            except tk.TclError: pass # No hay nada que deshacer
    
    def cmd_rehacer(self):
        widget = self._get_focused_text_widget()
        if hasattr(widget, 'edit_redo'):
            try: widget.edit_redo()
            except tk.TclError: pass # No hay nada que rehacer

    def cmd_cortar(self):
        widget = self._get_focused_text_widget()
        if widget and widget.tag_ranges("sel"):
            widget.event_generate("<<Cut>>")
            self.set_unsaved_changes(True)

    def cmd_copiar(self):
        widget = self._get_focused_text_widget()
        if widget and widget.tag_ranges("sel"):
            widget.event_generate("<<Copy>>")

    def cmd_pegar(self):
        widget = self._get_focused_text_widget()
        if widget:
            widget.event_generate("<<Paste>>")
            self.set_unsaved_changes(True)

    def cmd_seleccionar_todo(self):
        widget = self._get_focused_text_widget()
        if isinstance(widget, ctk.CTkTextbox):
            widget.tag_add("sel", "1.0", "end")
        elif isinstance(widget, ctk.CTkEntry):
            widget.select_range(0, 'end')


    def cmd_ejecutar_algoritmo(self):
        if self.is_running:
            messagebox.showwarning("En ejecución", "Ya hay un algoritmo en ejecución.", parent=self)
            return
        
        if self.console_frame.is_waiting_for_input():
            messagebox.showwarning("Entrada pendiente", "La consola está esperando una entrada. Finalice la ejecución actual.", parent=self)
            return

        codigo = self.editor_frame.get_content()
        if not codigo.strip():
            messagebox.showinfo("Vacío", "No hay código para ejecutar.", parent=self)
            return

        self.console_frame.clear_output()
        self.console_frame.write_output(">>> Iniciando ejecución...\n")
        self.is_running = True

        # Ejecutar en un hilo separado para no bloquear la GUI
        self.interpreter_thread = threading.Thread(target=self._run_code_thread, args=(codigo,), daemon=True)
        self.interpreter_thread.start()
        
        # Deshabilitar controles sensibles durante la ejecución
        self._toggle_execution_controls(enabled=False)

        # Programar una verificación periódica para ver si el hilo ha terminado
        self.after(100, self._check_interpreter_thread)


    def _run_code_thread(self, codigo):
        """Función que se ejecuta en el hilo del intérprete."""
        lexer = Lexer(codigo)
        tokens, errors_lex = lexer.tokenize()

        if errors_lex:
            for error in errors_lex:
                self.console_frame.write_output(f"Error Léxico: {error}")
            # self.console_frame.write_output("\n<<< Ejecución fallida (errores léxicos).")
            # self.is_running = False # Se establecerá en _check_interpreter_thread
            return # Terminar el hilo

        # Imprimir tokens (opcional, para depuración)
        # self.console_frame.write_output("Tokens:\n")
        # for token in tokens: self.console_frame.write_output(str(token))
        # self.console_frame.write_output("\n")

        parser = Parser(tokens)
        ast_node, errors_par = parser.parse()

        if errors_par:
            for error in errors_par:
                self.console_frame.write_output(f"Error Sintáctico: {error}")
            # self.console_frame.write_output("\n<<< Ejecución fallida (errores sintácticos).")
            # self.is_running = False
            return

        if ast_node is None: # Si el AST es None pero no hubo errores explícitos (raro)
            self.console_frame.write_output("Error: No se pudo construir el árbol de sintaxis (AST).")
            # self.console_frame.write_output("\n<<< Ejecución fallida.")
            # self.is_running = False
            return

        # Imprimir AST (opcional, para depuración)
        # self.console_frame.write_output("AST:\n")
        # self.console_frame.write_output(str(ast_node)) # Puede ser muy largo
        # self.console_frame.write_output("\n")

        interpreter = Interpreter(
            console_input_func=self.console_frame.request_input,
            console_output_func=self.console_frame.write_output
        )
        try:
            interpreter.interpret(ast_node)
            # self.console_frame.write_output("\n<<< Ejecución completada.")
        except Exception as e: # Captura errores de runtime del intérprete o errores inesperados
            self.console_frame.write_output(f"Error en ejecución: {e}")
            # self.console_frame.write_output("\n<<< Ejecución fallida (error de runtime).")
        finally:
            # self.is_running = False # El hilo principal de la GUI lo gestionará
            pass # No modificar is_running aquí, se hace en el hilo principal


    def _check_interpreter_thread(self):
        """Verifica si el hilo del intérprete ha terminado."""
        if self.interpreter_thread and self.interpreter_thread.is_alive():
            self.after(100, self._check_interpreter_thread) # Volver a verificar
        else:
            # El hilo ha terminado
            self.is_running = False
            if self.console_frame.is_waiting_for_input():
                # Si el hilo terminó pero la consola aún espera input (ej. por timeout en LEA)
                self.console_frame.hide_input_entry() # Asegurar que se oculte
                self.console_frame.waiting_for_input = False # Resetear estado

            # Añadir mensaje de fin de ejecución si no lo hubo ya por error
            # Esto es un poco heurístico, la salida final puede variar.
            # Se podría mejorar con un estado más explícito del intérprete.
            final_output = self.console_frame.output_text.get("end-2l linestart", "end-1c") # Última línea
            if "<<<" not in final_output: # Si no hay un mensaje de fin de ejecución explícito
                 self.console_frame.write_output("\n<<< Ejecución finalizada.")
            
            self._toggle_execution_controls(enabled=True) # Reactivar controles
            self.interpreter_thread = None # Limpiar referencia al hilo


    def _toggle_execution_controls(self, enabled: bool):
        """Habilita o deshabilita controles durante la ejecución."""
        state = "normal" if enabled else "disabled"
        
        # Menú Archivo (parcial)
        self.menu.menubar.entryconfig("Archivo", state=state) # Todo el menú archivo
        # Podrías ser más granular:
        # self.menu.menu_archivo.entryconfig("Nuevo", state=state)
        # self.menu.menu_archivo.entryconfig("Abrir...", state=state)
        # ... excepto Salir, quizás

        # Menú Ejecutar
        # self.menu.menu_ejecutar.entryconfig("Ejecutar Algoritmo", state=state)
        self.menu.menubar.entryconfig("Ejecutar", state=state) # Todo el menú ejecutar

        # Editor (hacerlo de solo lectura)
        editor_state = "normal" if enabled else "disabled"
        self.editor_frame.editor.configure(state=editor_state)
        # Si lo pones disabled, no se puede ni seleccionar texto.
        # Podrías interceptar eventos de teclado si quieres permitir lectura pero no edición.
        # Por ahora, lo más simple es deshabilitarlo.

    def cmd_ejecutar_paso_a_paso(self):
        messagebox.showinfo("Próximamente", "La ejecución paso a paso aún no está implementada.", parent=self)

    def cmd_limpiar_consola(self):
        self.console_frame.clear_output()

    def cmd_set_theme(self, theme_name):
        self.theme_manager.set_theme(theme_name)
        self.menu.update_theme_selection(self.theme_manager.current_theme) # Sincronizar radio button del menú
        # El highlighter ya se actualiza desde theme_manager si la referencia es correcta.

    def cmd_mostrar_acerca_de(self):
        messagebox.showinfo(f"Acerca de {APP_NAME}",
                            f"{APP_NAME} v{APP_VERSION}\n\n"
                            "Simulador de PSeInt con léxico colombiano.\n"
                            "Proyecto para la universidad.\n\n"
                            "Desarrollado con Python y CustomTkinter.",
                            parent=self)

if __name__ == '__main__':
    # Código de prueba para la ventana principal
    # Necesita que las importaciones relativas funcionen,
    # así que se debe ejecutar desde la raíz del proyecto
    # o ajustar sys.path.
    # python -m gui.main_window (si está en un paquete)
    
    # Para prueba directa, ajustamos path (no ideal para producción)
    import sys
    import os
    # Añadir el directorio padre de 'gui' al path para que encuentre 'core', 'utils'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) 
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Ahora las importaciones relativas desde MainWindow deberían funcionar mejor
    app = MainWindow()
    app.mainloop()