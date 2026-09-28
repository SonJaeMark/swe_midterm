import tkinter as tk

class Button(tk.Button):
    def __init__(self, parent, text="", command=None, bg="#111827", fg="white", **kwargs):
        super().__init__(
            parent, text=text, command=command,
            font=("Arial", 11, "bold"), bg=bg, fg=fg,
            activebackground="#1F2937", activeforeground="white",
            relief="flat", cursor="hand2", bd=0, **kwargs
        )