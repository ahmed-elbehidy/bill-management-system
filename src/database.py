# database.py
"""
DB layer for the Bill Management app.

This module provides a thin manager around an SQLite DB and a small
utility to display saved orders in a Tkinter window.
"""

import sqlite3
from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, BOTH, END


class DBManager:
    """Simple database manager for storing and showing orders."""

    DB_FILE = "bills.db"
    CREATE_SQL = """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL,
        date DATETIME NOT NULL
    );
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or self.DB_FILE
        self._conn = sqlite3.connect(self.db_path)
        self._cur = self._conn.cursor()
        self._ensure_schema()

    def _ensure_schema(self):
        """Create required table(s) if they don't exist."""
        self._cur.execute(self.CREATE_SQL)
        self._conn.commit()

    # ---------------------
    # Write helpers
    # ---------------------
    def add_order(self, item: str, quantity: int, price: float, total: float, date: str) -> None:
        """
        Insert one row representing an ordered item.

        Parameters:
            item: item name
            quantity: integer
            price: unit price
            total: quantity * price
            date: timestamp string (e.g. 'YYYY-MM-DD HH:MM:SS')
        """
        insert_sql = "INSERT INTO orders (item, quantity, price, total, date) VALUES (?, ?, ?, ?, ?)"
        self._cur.execute(insert_sql, (item, quantity, price, total, date))
        self._conn.commit()

    # ---------------------
    # Read helpers
    # ---------------------
    def fetch_order_dates(self):
        """Return a list of distinct dates in descending order."""
        self._cur.execute("SELECT DISTINCT date FROM orders ORDER BY date DESC")
        return [row[0] for row in self._cur.fetchall()]

    def fetch_items_for_date(self, date_stamp):
        """Return items for a given date (ordered by id)."""
        self._cur.execute(
            "SELECT item, quantity, price, total FROM orders WHERE date = ? ORDER BY id", (date_stamp,)
        )
        return self._cur.fetchall()

    # ---------------------
    # UI utility
    # ---------------------
    def show_orders_window(self, title="All Orders", width=800, height=600):
        """
        Pop up a Toplevel window and print formatted orders grouped by date.
        (Intended to be called from the Tkinter main app.)
        """
        dates = self.fetch_order_dates()

        orders_win = Toplevel()
        orders_win.title(title)
        orders_win.geometry(f"{width}x{height}")

        scrollbar = Scrollbar(orders_win)
        scrollbar.pack(side=RIGHT, fill=Y)

        text_area = Text(orders_win, font=("Courier New", 12), bg="white", yscrollcommand=scrollbar.set)
        text_area.pack(fill=BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        if not dates:
            text_area.insert(END, "No orders found in the database.")
            text_area.config(state="disabled")
            return

        for d in dates:
            text_area.insert(END, "\n" + "=" * 70 + "\n")
            text_area.insert(END, f"Date: {d}\n")
            text_area.insert(END, "=" * 70 + "\n\n")
            text_area.insert(END, f"{'Item':<20}{'Qty':<8}{'Price':<12}{'Total':<12}\n")
            text_area.insert(END, "-" * 52 + "\n")

            items = self.fetch_items_for_date(d)
            running_total = 0.0

            for itm, qty, price, tot in items:
                # ensure numeric formatting like the original
                text_area.insert(END, f"{itm:<20}{qty:<8}{price:<12.2f}{tot:<12.2f}\n")
                running_total += tot

            text_area.insert(END, "-" * 52 + "\n")
            text_area.insert(END, f"{'Total Bill:':<32}${running_total:.2f}\n\n")
            text_area.insert(END, "Thank you for visiting us!\n\n")

        text_area.config(state="disabled")

    # ---------------------
    # Cleanup
    # ---------------------
    def close(self):
        """Close DB connection (call before exiting app)."""
        try:
            self._conn.commit()
        finally:
            self._conn.close()


# Backwards-compatible alias (so other modules importing Database keep working)
Database = DBManager
