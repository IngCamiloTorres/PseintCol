# pseint_colombiano/gui/editor_frame.py
"""
Frame que contiene el editor de pseudocódigo y el número de líneas.
"""
import customtkinter as ctk
import tkinter as tk # Para ctk.INSERT y otros tk constantes si es necesario
import re # Para tooltips y autocompletado
from utils.syntax_highlighter import SyntaxHighlighter # Ajusta la ruta si es necesario
from core.keywords_col import AUTOCOMPLETE_SUGGESTIONS, COMMAND_TOOLTIPS # Ajusta la ruta

class EditorFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Número de líneas
        self.line_numbers = ctk.CTkTextbox(self, width=40, font=("Consolas", 12),
                                           state="disabled", activate_scrollbars=False,
                                           text_color=("gray50", "gray50"))
        self.line_numbers.grid(row=0, column=0, sticky="ns", pady=(0,0), padx=(0,0))

        # Editor de texto
        self.editor = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="none", undo=True)
        self.editor.grid(row=0, column=1, sticky="nsew", pady=(0,0), padx=(0,0))

        # --- SINCRONIZACIÓN DE SCROLL CORREGIDA ---
        # Cuando el editor se desplaza, su comando yscrollcommand se activa.
        # Este comando (nuestro método) moverá los números de línea.
        self.editor.configure(yscrollcommand=self._on_editor_scroll)

        # No necesitamos configurar yscrollcommand para line_numbers si su scrollbar está desactivada
        # y solo sigue al editor. Si line_numbers pudiera ser scrolleado independientemente
        # (ej. con activate_scrollbars=True y el usuario interactuando con su scrollbar),
        # entonces sí necesitaríamos un self.line_numbers.configure(yscrollcommand=self._on_line_numbers_scroll)
        # para que mueva al editor, pero esto podría crear bucles si no se tiene cuidado.
        # Dado que activate_scrollbars=False, el scroll de line_numbers solo se controla programáticamente.

        # Resaltado de sintaxis
        self.highlighter = SyntaxHighlighter(self.editor)
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<Return>", self._on_enter_key)
        # Eventos de Rueda del Ratón para scroll
        self.editor.bind("<MouseWheel>", self._on_mouse_wheel) # Windows y macOS
        self.editor.bind("<Button-4>", self._on_mouse_wheel)    # Linux (scroll up)
        self.editor.bind("<Button-5>", self._on_mouse_wheel)    # Linux (scroll down)
        # Para line_numbers, si también queremos que responda al scroll del mouse (aunque no tenga barra visible)
        self.line_numbers.bind("<MouseWheel>", self._on_mouse_wheel)
        self.line_numbers.bind("<Button-4>", self._on_mouse_wheel)
        self.line_numbers.bind("<Button-5>", self._on_mouse_wheel)

        # Autocompletado (básico)
        self.autocomplete_listbox = None
        self.editor.bind("<KeyRelease>", self._handle_autocomplete, add="+")
        self.editor.bind("<FocusOut>", self._hide_autocomplete_on_focus_out)
        self.editor.bind("<Button-1>", self._hide_autocomplete_on_click, add="+") # Ocultar al hacer click en editor

        # Tooltips
        self.tooltip_label = None
        # self.editor.bind("<Motion>", self._show_command_tooltip) # Puede ser un poco molesto

        self._update_line_numbers()

    def _on_editor_scroll(self, first_str, last_str):
        """
        Llamado cuando el CTkTextbox del editor se desplaza.
        Actualiza la vista vertical del CTkTextbox de los números de línea.
        first_str y last_str son strings que representan floats (ej: "0.0", "0.231...")
        """
        self.line_numbers.yview_moveto(first_str)
        # Es importante que _update_line_numbers no se llame aquí en cada pixel de scroll
        # ya que es una operación costosa. Se llama en _on_key_release o cuando el contenido cambia.

    def _on_key_release(self, event=None):
        # Verificar si la tecla presionada podría afectar el número de líneas (Enter, Backspace, Delete)
        # o si es una tecla de movimiento que podría requerir re-sincronización si el contenido es muy dinámico.
        # Por simplicidad, actualizamos en la mayoría de las liberaciones de teclas, pero se podría optimizar.
        self._update_line_numbers()
        self.highlighter.highlight(event)
        if hasattr(self.master, 'set_unsaved_changes'):
             self.master.set_unsaved_changes(True)

    def _on_enter_key(self, event=None):
        current_line_index = self.editor.index(tk.INSERT).split('.')[0]
        current_line_text = self.editor.get(f"{current_line_index}.0", f"{current_line_index}.end")
        indentation = ""
        for char in current_line_text:
            if char == ' ': indentation += ' '
            elif char == '\t': indentation += '\t'
            else: break
        trigger_keywords = ["ENTONCES", "HAGA", "SINO", "DEOTROMODO"]
        if any(keyword.lower() in current_line_text.lower() for keyword in trigger_keywords):
            indentation += "  "
        self.editor.insert(tk.INSERT, f"\n{indentation}")
        self._update_line_numbers() # Actualizar después de insertar nueva línea
        return "break"

    def _update_line_numbers(self, event=None):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        try:
            # El índice "end-1c" puede fallar si el textbox está vacío.
            # Contar líneas basándose en el contenido real.
            content = self.editor.get("1.0", "end-1c")
            if not content: # Si está vacío
                num_editor_lines = 1
            else:
                num_editor_lines = content.count('\n') + 1

        except tk.TclError: # Esto puede pasar si el widget está en un estado extraño o vacío
            num_editor_lines = 1

        line_numbers_string = "\n".join(str(i) for i in range(1, int(num_editor_lines) + 1))
        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.configure(state="disabled")
        # Sincronizar el scroll después de actualizar el contenido de los números de línea.
        # Esto asegura que si se añaden/quitan muchas líneas, la vista se mantenga consistente.
        current_editor_scroll_pos = self.editor.yview()[0]
        self.line_numbers.yview_moveto(current_editor_scroll_pos)


    def _on_mouse_wheel(self, event):
        """Maneja el scroll con la rueda del ratón para el editor, los números de línea seguirán."""
        # El widget que origina el evento
        widget_scrolling = event.widget

        # Determinar dirección del scroll (normalizado para CustomTkinter)
        if event.num == 5 or event.delta < 0:  # Scroll hacia abajo
            scroll_units = 2 # Ajusta la cantidad de scroll
        elif event.num == 4 or event.delta > 0:  # Scroll hacia arriba
            scroll_units = -2 # Ajusta la cantidad de scroll
        else:
            return

        # Aplicar el scroll al editor principal.
        # Esto activará el self.editor.configure(yscrollcommand=self._on_editor_scroll)
        # que a su vez sincronizará self.line_numbers.
        self.editor.yview_scroll(scroll_units, "units")

        return "break" # Evitar que el evento se propague más y cause doble scroll.


    def get_content(self):
        return self.editor.get("1.0", "end-1c")

    def set_content(self, content):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self._update_line_numbers() # Importante llamar DESPUÉS de insertar contenido
        self.highlighter.highlight()
        if hasattr(self.master, 'set_unsaved_changes'):
             self.master.set_unsaved_changes(False)

    def clear_content(self):
        self.set_content("")

    def _handle_autocomplete(self, event=None):
        # Ignorar teclas que no sean alfanuméricas o de modificación que no queremos que activen/modifiquen el popup
        if event and event.keysym and not (event.keysym.isalnum() or event.keysym in ("BackSpace", "Delete", "Escape", "Down", "Up", "Return", "Tab")):
            return

        if event and event.keysym.isalnum() and len(event.keysym) == 1:
            current_pos = self.editor.index(tk.INSERT)
            line, char_pos = map(int, current_pos.split('.'))
            word_start_index = self.editor.search(r"\s", f"{line}.{char_pos}", backwards=True, regexp=True)
            if not word_start_index:
                word_start_index = f"{line}.0"
            else:
                 word_start_index = self.editor.index(f"{word_start_index}+1c")
            current_word = self.editor.get(word_start_index, f"{line}.{char_pos}").strip().upper()

            if not current_word or len(current_word) < 1: # Umbral mínimo para mostrar
                self._hide_autocomplete()
                return

            suggestions = [s for s in AUTOCOMPLETE_SUGGESTIONS if s.startswith(current_word)]
            if suggestions:
                self._show_autocomplete(suggestions, current_pos)
            else:
                self._hide_autocomplete()
        elif event and event.keysym == "BackSpace":
            # Reevaluar autocompletado después de borrar. Podría ser más complejo para no reabrir inmediatamente.
            # Por ahora, simplemente llamamos de nuevo para que se ajuste o cierre.
             self.editor.after(10, lambda: self._trigger_autocomplete_from_key(event)) # Pequeño delay
        elif event and event.keysym == "Escape":
            self._hide_autocomplete()
        elif self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            # Manejo de Teclas de Navegación/Selección para el popup (simplificado)
            if event.keysym == "Down":
                # Intentar dar foco al primer botón del popup
                try:
                    first_button = self.autocomplete_listbox.winfo_children()[0]
                    first_button.focus_set()
                except IndexError:
                    pass # No hay botones
                return "break"
            elif event.keysym == "Return" or event.keysym == "Tab":
                 # Si el foco está en un botón del popup, su comando se activará.
                 # Si el foco está en el editor, necesitamos una forma de seleccionar la primera sugerencia
                 # o la sugerencia actualmente "resaltada" (no implementado).
                 # Por simplicidad, si se presiona Enter/Tab en el editor y hay sugerencias,
                 # se podría tomar la primera.
                if self.editor.focus_get() == self.editor and self.autocomplete_listbox.winfo_children():
                    first_suggestion = self.autocomplete_listbox.winfo_children()[0].cget("text")
                    self._select_autocomplete_item(first_suggestion)
                return "break" # Evitar que Enter/Tab hagan su acción por defecto en el editor

    def _trigger_autocomplete_from_key(self, event):
        """Función auxiliar para llamar a _handle_autocomplete, usualmente con un delay."""
        # Simula un evento de liberación de tecla "alnum" para reutilizar la lógica.
        # Esto es un poco un hack, idealmente _handle_autocomplete se reestructuraría.
        class MockEvent:
            def __init__(self):
                # Obtener el último carácter alfanumérico antes del cursor para simular
                current_pos_str = self.editor.index(tk.INSERT)
                line, char_idx = map(int, current_pos_str.split('.'))
                if char_idx > 0:
                    # Obtener el carácter justo antes del cursor.
                    # Necesitamos el inicio de la palabra para el 'current_word' en _handle_autocomplete
                    self.keysym = self.editor.get(f"{line}.{char_idx-1}")
                    if not self.keysym.isalnum(): self.keysym = "a" # Fallback
                else:
                    self.keysym = "a" # Fallback si está al inicio de la línea

        mock_event = MockEvent()
        self._handle_autocomplete(mock_event)


    def _show_autocomplete(self, suggestions, cursor_pos_str):
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            self.autocomplete_listbox.destroy()

        x, y, _, height = self.editor.bbox(cursor_pos_str)
        editor_x = self.editor.winfo_rootx()
        editor_y = self.editor.winfo_rooty()
        popup_x = editor_x + x
        popup_y = editor_y + y + height + 2

        self.autocomplete_listbox = ctk.CTkToplevel(self.editor)
        self.autocomplete_listbox.overrideredirect(True)
        # Ajustar el tamaño máximo y el tamaño por item
        max_items_visible = 5
        item_height = 28 # Altura aproximada de un CTkButton
        popup_height = min(len(suggestions) * item_height, max_items_visible * item_height) + 4 # padding
        popup_width = 180 # Ancho fijo o calculado

        self.autocomplete_listbox.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        self.autocomplete_listbox.attributes("-topmost", True)
        self.autocomplete_listbox.lift()

        # Frame interno para scroll si hay muchas sugerencias (no implementado aquí por simplicidad)
        # Si son pocas, solo se apilan botones.

        for i, item_text in enumerate(suggestions):
            btn = ctk.CTkButton(self.autocomplete_listbox, text=item_text,
                                command=lambda i_t=item_text: self._select_autocomplete_item(i_t),
                                anchor="w", fg_color="transparent",
                                hover_color=("#cccccc", "#333333"), # Light, Dark hover
                                height=item_height - 4, corner_radius=3)
            btn.pack(fill="x", padx=2, pady=1)
            # Permitir navegación con Tab entre los botones del popup
            if i == 0: btn.focus() # Dar foco al primer botón

    def _hide_autocomplete_on_click(self, event=None):
        # Oculta si el click NO es sobre el popup de autocompletado
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            # Verificar si el click fue fuera del popup.
            # Esto es un poco complicado porque el popup es un Toplevel.
            # Una forma simple es ocultarlo y si el click fue en un botón del popup,
            # el comando del botón ya se habrá disparado.
            # self.editor.after(50, self._hide_autocomplete) # Pequeño delay
            pass # Dejar que _hide_autocomplete_on_focus_out lo maneje


    def _hide_autocomplete(self, event=None):
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            self.autocomplete_listbox.destroy()
        self.autocomplete_listbox = None

    def _hide_autocomplete_on_focus_out(self, event=None):
        # Si el foco sale del editor, y no va hacia el popup de autocompletado, ocultar.
        # Usamos un pequeño delay porque el cambio de foco no es instantáneo.
        self.editor.after(100, self._check_and_hide_autocomplete_after_delay)

    def _check_and_hide_autocomplete_after_delay(self):
        if not self.autocomplete_listbox or not self.autocomplete_listbox.winfo_exists():
            return

        focused_widget = self.winfo_toplevel().focus_get()

        # Si el foco se ha ido a algún widget que no es el editor ni parte del popup de autocompletado
        if focused_widget != self.editor and \
           (not hasattr(focused_widget, 'winfo_toplevel') or focused_widget.winfo_toplevel() != self.autocomplete_listbox):
            self._hide_autocomplete()


    def _select_autocomplete_item(self, item_text):
        current_pos_str = self.editor.index(tk.INSERT)
        line, char_pos = map(int, current_pos_str.split('.'))
        word_start_index_str = self.editor.search(r"\s", f"{line}.{char_pos}", backwards=True, regexp=True)
        if not word_start_index_str:
            word_start_index_str = f"{line}.0"
        else:
            word_start_index_str = self.editor.index(f"{word_start_index_str}+1c")

        self.editor.delete(word_start_index_str, current_pos_str) # Borrar hasta el cursor
        self.editor.insert(word_start_index_str, item_text + " ")
        self._hide_autocomplete()
        self.editor.focus_set()
        self.highlighter.highlight()


    def _show_command_tooltip(self, event):
        if self.tooltip_label and self.tooltip_label.winfo_exists():
            self.tooltip_label.destroy()
        self.tooltip_label = None

        index = self.editor.index(f"@{event.x},{event.y}")
        line, char_pos = map(int, index.split('.'))
        line_text = self.editor.get(f"{line}.0", f"{line}.end")
        found_keyword_tooltip = None

        for keyword, tooltip_text in COMMAND_TOOLTIPS.items():
            try:
                for match in re.finditer(r"(?i)\b" + re.escape(keyword) + r"\b", line_text):
                    start_char, end_char = match.span()
                    if start_char <= char_pos < end_char:
                        found_keyword_tooltip = tooltip_text
                        break
            except re.error: pass
            if found_keyword_tooltip: break

        if found_keyword_tooltip:
            # Usar CTkToplevel para el tooltip para que pueda posicionarse correctamente
            self.tooltip_label = ctk.CTkToplevel(self.editor)
            self.tooltip_label.overrideredirect(True)
            self.tooltip_label.attributes("-topmost", True)

            label_widget = ctk.CTkLabel(self.tooltip_label, text=found_keyword_tooltip,
                                        fg_color=("#F0F0F0", "#252525"), # Colores para light/dark
                                        text_color=("#101010", "#DCE4EE"),
                                        corner_radius=4, padx=5, pady=3,
                                        font=("Arial", 10)) # Ajusta la fuente
            label_widget.pack()

            # Posicionar el tooltip cerca del cursor del ratón
            # Las coordenadas del evento son relativas al editor
            root_x = self.editor.winfo_rootx() + event.x + 10 # Desplazamiento X
            root_y = self.editor.winfo_rooty() + event.y + 20 # Desplazamiento Y
            self.tooltip_label.geometry(f"+{root_x}+{root_y}")
            self.tooltip_label.lift()

            self.editor.after(3000, self._hide_tooltip)

    def _hide_tooltip(self):
        if self.tooltip_label and self.tooltip_label.winfo_exists():
            self.tooltip_label.destroy()
        self.tooltip_label = None