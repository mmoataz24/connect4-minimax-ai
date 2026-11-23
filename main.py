import sys
import tkinter as tk

from gui import Connect4App
from benchmark import benchmark


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        benchmark()
    else:
        window = tk.Tk()
        Connect4App(window)
        window.mainloop()
