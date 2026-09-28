import tkinter as tk

class TextField(tk.Frame):
    def __init__(self, parent, label_text="", placeholder="", is_password=False, numeric_only=False, **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        
        self.placeholder = placeholder
        self.is_password = is_password
        self.numeric_only = numeric_only
        self.has_placeholder = False
        
        if label_text:
            self.label = tk.Label(
                self, text=label_text, font=("Arial", 9, "bold"),
                fg="#111827", bg="white", anchor="w"
            )
            self.label.pack(fill="x", pady=(0, 6))
            
        self.entry_var = tk.StringVar()
        
        # Setup validation command for numbers only
        vcmd = (self.register(self._validate_numeric), '%P') if numeric_only else None
        
        self.entry = tk.Entry(
            self, textvariable=self.entry_var,
            font=("Arial", 11), bg="#FFFFFF", fg="#111827",
            relief="solid", bd=1,
            validate='key' if numeric_only else 'none',
            validatecommand=vcmd if numeric_only else None
        )
        self.entry.pack(fill="x", ipady=8, ipadx=6)
        
        # Bind focus events for dynamic placeholder handling
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Initialize placeholder if provided
        if self.placeholder:
            self._set_placeholder_state()

    def _validate_numeric(self, proposed_value):
        # Allow empty string (for backspacing/clearing) or digits only
        if proposed_value == "":
            return True
        return proposed_value.isdigit()

    def _set_placeholder_state(self):
        self.has_placeholder = True
        # Temporarily disable validation to allow text placeholders
        if self.numeric_only:
            self.entry.config(validate='none')
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#9CA3AF")  # Placeholder grey color
        if self.is_password:
            self.entry.config(show="")  # Show text normally for placeholder

    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.has_placeholder = False
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#111827")  # Normal text color
            if self.is_password:
                self.entry.config(show="*")  # Mask password input
        
        # Re-enable validation when focused
        if self.numeric_only:
            self.entry.config(validate='key')

    def _on_focus_out(self, event):
        if not self.entry.get():
            if self.placeholder:
                self._set_placeholder_state()

    def get_value(self):
        if self.has_placeholder:
            return ""
        return self.entry_var.get()