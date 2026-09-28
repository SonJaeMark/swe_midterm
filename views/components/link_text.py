import tkinter as tk

class LinkText(tk.Label):
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(
            parent, text=text, font=("Arial", 9),
            fg="#2563EB", bg="white", cursor="hand2", **kwargs
        )
        self.command = command
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)
        self.bind("<Enter>", lambda e: self.config(font=("Arial", 9, "underline")))
        self.bind("<Leave>", lambda e: self.config(font=("Arial", 9)))