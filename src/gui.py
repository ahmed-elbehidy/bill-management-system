# gui.py
"""
Tkinter GUI for the Bill Management app.
"""

from tkinter import *
from datetime import datetime
from database import DBManager


class BillGUI:
    """Main Tkinter window for managing bills."""

    def __init__(self):
        self.root = Tk()
        self.root.title("Bill Management System")
        self.root.geometry("1300x700")
        self.root.resizable(False, False)

        # database manager
        self.db = DBManager()

        # available menu items
        self.menu_items = [
            ("Pizza", 8.50),
            ("Burger", 5.00),
            ("Pasta", 6.75),
            ("Sandwich", 4.25),
            ("Salad", 3.50),
            ("Juice", 2.00),
            ("Coffee", 1.50),
            ("Tea", 1.00),
            ("Ice Cream", 2.50),
        ]

        # UI build
        self._build_header()
        self._build_menu()
        self._build_order_form()
        self._build_bill_area()

        # entry storage
        self._order_vars = {name: StringVar() for name, _ in self.menu_items}

    # -------------------------
    # Section builders
    # -------------------------
    def _build_header(self):
        lbl = Label(
            self.root,
            text="BILL MANAGEMENT",
            bg="navy",
            fg="white",
            font=("Helvetica", 30, "bold"),
            pady=10,
        )
        lbl.pack(fill=X)

    def _build_menu(self):
        frame = Frame(self.root, bg="lightblue", bd=5, relief=RIDGE)
        frame.place(x=10, y=80, width=280, height=600)

        Label(frame, text="Menu", font=("Helvetica", 24, "bold"), fg="darkblue", bg="lightblue").pack(
            side=TOP, fill=X
        )

        for item, price in self.menu_items:
            line = Frame(frame, bg="lightblue")
            line.pack(fill=X, padx=20, pady=2)
            Label(line, text=item, font=("Arial", 16), bg="lightblue").pack(side=LEFT, anchor="w")
            Label(line, text=f"${price:.2f}", font=("Arial", 16), bg="lightblue").pack(side=RIGHT, anchor="e")

    def _build_order_form(self):
        frame = Frame(self.root, bd=5, relief=RIDGE)
        frame.place(x=300, y=80, width=380, height=600)

        self._entries = {}
        for idx, (name, _) in enumerate(self.menu_items):
            Label(frame, text=name, font=("Arial", 18), padx=10, pady=5).grid(row=idx, column=0, sticky="w")
            var = StringVar()
            self._entries[name] = var
            Entry(frame, textvariable=var, font=("Arial", 16), bd=5, width=10).grid(
                row=idx, column=1, padx=10, pady=5
            )

        btn_frame = Frame(frame)
        btn_frame.grid(row=len(self.menu_items), column=0, columnspan=2, pady=25)

        Button(btn_frame, text="Reset", width=12, font=("Arial", 16, "bold"),
               bg="lightgray", command=self._reset).grid(row=0, column=0, padx=8)
        Button(btn_frame, text="Total", width=12, font=("Arial", 16, "bold"),
               bg="lightgreen", command=self._calculate).grid(row=0, column=1, padx=8)
        Button(btn_frame, text="Show Orders", width=12, font=("Arial", 16, "bold"),
               bg="lightyellow", command=self.db.show_orders_window).grid(row=1, column=0, columnspan=2, pady=8)

    def _build_bill_area(self):
        frame = Frame(self.root, bd=5, relief=RIDGE)
        frame.place(x=700, y=80, width=600, height=600)

        Label(frame, text="Bill", font=("Helvetica", 24, "bold"), bg="lightyellow").pack(side=TOP, fill=X)

        self.bill_area = Text(frame, font=("Courier New", 14), bg="white")
        self.bill_area.pack(fill=BOTH, expand=True)

    # -------------------------
    # Button actions
    # -------------------------
    def _reset(self):
        """Clear all entry fields and bill text."""
        for var in self._entries.values():
            var.set("")
        self.bill_area.delete(1.0, END)

    def _calculate(self):
        """Compute totals and show bill in text area."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bill_area.delete(1.0, END)

        self.bill_area.insert(END, f"{'Item':<15}{'Qty':<10}{'Price':<15}{'Total':<10}\n")
        self.bill_area.insert(END, "-" * 55 + "\n")

        grand_total = 0.0
        for name, price in self.menu_items:
            val = self._entries[name].get().strip()
            if val.isdigit() and int(val) > 0:
                qty = int(val)
                total = qty * price
                grand_total += total
                self.bill_area.insert(END, f"{name:<15}{qty:<10}{price:<15.2f}{total:<10.2f}\n")
                self.db.add_order(name, qty, price, total, now)

        self.bill_area.insert(END, "-" * 55 + "\n")
        self.bill_area.insert(END, f"{'Total Amount:':<40}${grand_total:.2f}\n\n")
        self.bill_area.insert(END, "Thank you for visiting us!")

    # -------------------------
    # Run
    # -------------------------
    def run(self):
        self.root.mainloop()
