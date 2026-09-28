import tkinter as tk
from datetime import datetime
import calendar

class DateField(tk.Frame):
    def __init__(self, parent, label_text="", placeholder="MM/DD/YYYY", **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        
        self.placeholder = placeholder
        self.has_placeholder = False
        
        if label_text:
            self.label = tk.Label(
                self, text=label_text, font=("Arial", 9, "bold"),
                fg="#111827", bg="white", anchor="w"
            )
            self.label.pack(fill="x", pady=(0, 6))
            
        self.entry_var = tk.StringVar()
        # Automatically format input as numbers are typed
        self.entry_var.trace_add("write", self._format_date_input)
        
        # Main entry container frame to hold entry and calendar button side-by-side
        input_container = tk.Frame(self, bg="white")
        input_container.pack(fill="x")
        
        self.entry = tk.Entry(
            input_container, textvariable=self.entry_var,
            font=("Arial", 11), bg="#FFFFFF", fg="#111827",
            relief="solid", bd=1
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=6)
        
        # Calendar Trigger Button
        self.cal_btn = tk.Button(
            input_container, text="📅", font=("Arial", 11),
            bg="#F3F4F6", fg="#111827", relief="solid", bd=1,
            command=self._open_calendar_popup, cursor="hand2"
        )
        self.cal_btn.pack(side="left", fill="y", padx=(2, 0))
        
        # Bind focus events for dynamic placeholder handling
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        if self.placeholder:
            self._set_placeholder_state()

    def _format_date_input(self, *args):
        if self.has_placeholder:
            return
            
        val = self.entry_var.get()
        # Extract only digits from user input
        digits = "".join([char for char in val if char.isdigit()])
        
        # Limit to maximum 8 digits (MMDDYYYY)
        if len(digits) > 8:
            digits = digits[:8]
            
        # Build formatted date string dynamically (MM/DD/YYYY)
        formatted = ""
        if len(digits) > 0:
            formatted = digits[:2]
        if len(digits) > 2:
            formatted += "/" + digits[2:4]
        if len(digits) > 4:
            formatted += "/" + digits[4:8]
            
        # Update entry variable only if formatted text differs to avoid loop
        if formatted != val:
            self.entry_var.set(formatted)

    def _set_placeholder_state(self):
        self.has_placeholder = True
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#9CA3AF")

    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.has_placeholder = False
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#111827")

    def _on_focus_out(self, event):
        if not self.entry.get():
            if self.placeholder:
                self._set_placeholder_state()

    def _open_calendar_popup(self):
        """Creates a popup calendar window to select date interactively."""
        top = tk.Toplevel(self)
        top.title("Select Date")
        top.geometry("260x280")
        top.resizable(False, False)
        top.grab_set()  # Make window modal
        
        now = datetime.now()
        self.cal_year = now.year
        self.cal_month = now.month
        
        header_frame = tk.Frame(top, bg="#0B2545", pady=5)
        header_frame.pack(fill="x")
        
        prev_btn = tk.Button(header_frame, text="<", command=lambda: self._change_month(-1, lbl_month, days_frame), bg="#0B2545", fg="white", relief="flat", font=("Arial", 10, "bold"))
        prev_btn.pack(side="left", padx=15)
        
        lbl_month = tk.Label(header_frame, text="", bg="#0B2545", fg="white", font=("Arial", 11, "bold"))
        lbl_month.pack(side="left", expand=True)
        
        next_btn = tk.Button(header_frame, text=">", command=lambda: self._change_month(1, lbl_month, days_frame), bg="#0B2545", fg="white", relief="flat", font=("Arial", 10, "bold"))
        next_btn.pack(side="right", padx=15)
        
        days_frame = tk.Frame(top, bg="white", padx=10, pady=10)
        days_frame.pack(fill="both", expand=True)
        
        self._build_calendar_grid(days_frame, lbl_month, top)

    def _change_month(self, delta, lbl_month, days_frame):
        self.cal_month += delta
        if self.cal_month > 12:
            self.cal_month = 1
            self.cal_year += 1
        elif self.cal_month < 1:
            self.cal_month = 12
            self.cal_year -= 1
        self._build_calendar_grid(days_frame, lbl_month, None)

    def _build_calendar_grid(self, days_frame, lbl_month, top_window):
        for widget in days_frame.winfo_children():
            widget.destroy()
            
        lbl_month.config(text=f"{calendar.month_name[self.cal_month]} {self.cal_year}")
        
        days_of_week = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for i, day in enumerate(days_of_week):
            tk.Label(days_frame, text=day, font=("Arial", 9, "bold"), fg="#6B7280", bg="white").grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            
        cal = calendar.monthcalendar(self.cal_year, self.cal_month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(days_frame, text="", bg="white").grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)
                else:
                    btn = tk.Button(
                        days_frame, text=str(day), font=("Arial", 9),
                        bg="#F9FAFB", fg="#111827", relief="flat",
                        command=lambda d=day: self._select_date(d, top_window)
                    )
                    btn.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)

        for i in range(7):
            days_frame.columnconfigure(i, weight=1)

    def _select_date(self, day, top_window):
        selected_date = f"{self.cal_month:02d}/{day:02d}/{self.cal_year}"
        if self.has_placeholder:
            self.has_placeholder = False
            self.entry.config(fg="#111827")
        self.entry_var.set(selected_date)
        if top_window:
            top_window.destroy()

    def get_value(self):
        if self.has_placeholder:
            return ""
        return self.entry_var.get()