# main.py
"""
Entry point for the Bill Management System.
"""

from gui import BillGUI


def main():
    app = BillGUI()
    app.run()


if __name__ == "__main__":
    main()
