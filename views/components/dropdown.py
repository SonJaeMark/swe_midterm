import tkinter as tk
from tkinter import ttk

class Dropdown(tk.Frame):
    def __init__(self, parent, label_text="", values=None, **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        if values is None:
            values = []
            
        if label_text:
            self.label = tk.Label(
                self, text=label_text, font=("Arial", 9, "bold"),
                fg="#111827", bg="white", anchor="w"
            )
            self.label.pack(fill="x", pady=(0, 6))
            
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self, textvariable=self.var, values=values, 
            state="readonly", font=("Arial", 11)
        )
        self.combo.pack(fill="x", ipady=4)
        if values:
            self.combo.set(values[0])
            
    def get_value(self):
        return self.var.get()