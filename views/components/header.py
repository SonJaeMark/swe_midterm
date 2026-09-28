import tkinter as tk

class Header(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", height=65, **kwargs)
        self.pack_propagate(False)
        
        # Logo text
        logo_label = tk.Label(
            self, text="MediQueue", 
            font=("Arial", 14, "bold"), fg="#0B2545", bg="white"
        )
        logo_label.pack(side="left", padx=25)
        
        # Portal description right side
        right_info = tk.Label(
            self, text="Authentication Portal   |   Login & Account Setup", 
            font=("Arial", 10), fg="#4B5563", bg="white"
        )
        right_info.pack(side="right", padx=25)