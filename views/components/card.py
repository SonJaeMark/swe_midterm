import tkinter as tk

class Card(tk.Frame):
    def __init__(self, parent, bg="white", **kwargs):
        super().__init__(parent, bg=bg, relief="flat", bd=0, **kwargs)