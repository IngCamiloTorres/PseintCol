# pseint_colombiano/gui/console_frame.py
"""
Frame que contiene la consola de salida y (opcionalmente) entrada.
"""
import customtkinter as ctk
import queue # Para comunicación thread-safe si la entrada es bloqueante

class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1) # Output area
        self.grid_rowconfigure(1, weight=0) # Input area (if used)
        self.grid_columnconfigure(0, weight=1)

        self.output_text = ctk.CTkTextbox(self, wrap="word", state="disabled", font=("Consolas", 11))
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5,0))

        # Para entrada de usuario (LEA)
        self.input_entry_visible = False # Para controlar la visibilidad
        self.input_entry = ctk.CTkEntry(self, font=("Consolas", 11), placeholder_text="Ingrese valor aquí...")
        # self.input_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5) # Se mostrará/ocultará dinámicamente
        self.input_entry.bind("<Return>", self._on_input_submit)
        
        self.input_queue = queue.Queue() # Para pasar la entrada del usuario al intérprete
        self.waiting_for_input = False

    def write_output(self, message):
        """Añade un mensaje a la consola de salida."""
        self.output_text.configure(state="normal")
        if not message.endswith("\n"):
            message += "\n" # PSeInt generalmente añade newline por MUESTRE
        self.output_text.insert("end", message)
        self.output_text.configure(state="disabled")
        self.output_text.see("end") # Auto-scroll

    def clear_output(self):
        """Limpia la consola de salida."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def request_input(self):
        """
        Prepara la GUI para recibir una entrada del usuario.
        Este método será llamado por el intérprete.
        Devuelve el valor ingresado (bloqueante en espíritu, pero no bloquea el hilo GUI).
        """
        if self.input_entry_visible: # Ya hay una petición de input activa
            self.write_output("[Error Interno Consola: Intento de múltiples LEA simultáneos]\n")
            return None 

        self.input_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_entry.configure(state="normal")
        self.input_entry.delete(0, "end")
        self.input_entry.focus_set()
        self.input_entry_visible = True
        self.waiting_for_input = True
        
        # Bucle de espera no bloqueante para la GUI
        # El intérprete debe esperar a que input_queue tenga un valor
        # Esto es un desafío de diseño: ¿Cómo hacer que el intérprete espere
        # sin congelar la GUI? Se puede usar un hilo para el intérprete o
        # un enfoque basado en eventos/callbacks.
        # Por ahora, el intérprete (si corre en el hilo principal)
        # se bloqueará aquí esperando la cola.
        # Para una GUI real, el intérprete DEBERÍA correr en otro hilo.
        try:
            # Timeout para evitar bloqueo indefinido si algo va mal
            # o para permitir que el hilo de la GUI procese eventos.
            # En una app real, esto se manejaría mejor con hilos y eventos.
            user_input = self.input_queue.get(timeout=300) # Espera 5 minutos máximo
            self.waiting_for_input = False # Ya no esperamos
            return user_input
        except queue.Empty:
            self.write_output("\n[Tiempo de espera para entrada agotado]\n")
            self.hide_input_entry() # Ocultar si se agota el tiempo
            self.waiting_for_input = False
            return None # O "" o un error específico
        finally:
            # Asegurarse de que el input entry se oculte si no lo hizo _on_input_submit
            if self.input_entry_visible and not self.waiting_for_input:
                 self.hide_input_entry()


    def _on_input_submit(self, event=None):
        """Cuando el usuario presiona Enter en el campo de entrada."""
        if not self.waiting_for_input: return # No hacer nada si no se esperaba input

        user_text = self.input_entry.get()
        self.write_output(f"{user_text}") # Simular eco de la entrada PSeInt
        self.input_queue.put(user_text) # Poner el texto en la cola para el intérprete
        self.hide_input_entry()

    def hide_input_entry(self):
        self.input_entry.delete(0, "end")
        self.input_entry.grid_remove()
        self.input_entry.configure(state="disabled")
        self.input_entry_visible = False
        # Devolver el foco al editor si es posible
        if hasattr(self.master, 'editor_frame') and hasattr(self.master.editor_frame, 'editor'):
            self.master.editor_frame.editor.focus_set()

    def is_waiting_for_input(self):
        return self.waiting_for_input


if __name__ == '__main__':
    app = ctk.CTk()
    app.title("Console Frame Test")
    app.geometry("600x400")

    console = ConsoleFrame(app)
    console.pack(expand=True, fill="both", padx=10, pady=10)

    console.write_output("Este es un mensaje de prueba.")
    console.write_output("Otro mensaje en la consola.")

    def test_input():
        console.write_output("Por favor, ingrese algo:")
        # En una aplicación real, el intérprete correría en otro hilo.
        # Aquí, para probar, lo hacemos de forma simple.
        # Esta llamada bloqueará hasta que se ingrese algo o haya timeout.
        # Lo ideal es no llamar request_input directamente desde el hilo de la GUI
        # de esta forma si el intérprete está en el mismo hilo.
        # Aquí lo hacemos para demostrar la funcionalidad del widget.
        
        # Para evitar bloqueo en test simple, usamos after para simular:
        app.after(100, _perform_request_input)

    def _perform_request_input():
        # Esta función se llamaría desde el hilo del intérprete
        user_data = console.request_input()
        if user_data is not None:
            console.write_output(f"Usted ingresó: {user_data}")
        else:
            console.write_output("No se recibió entrada o hubo timeout.")


    test_button = ctk.CTkButton(app, text="Probar Entrada (LEA)", command=test_input)
    test_button.pack(pady=10)

    app.mainloop()