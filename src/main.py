import tkinter as tk
from src.gui import AdvancementApp

def main():
    root = tk.Tk()
    # On Mac, sometimes theme helps, but let's stick to default ttk for now.
    app = AdvancementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
