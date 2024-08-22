import os
import tkinter as tk
from tkinter import messagebox

def show_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    result = messagebox.askyesno('Run Script', 'Do you want to run the update_stock_excel.py script?')
    return result

def run_script():
    os.system('python update_stock_excel.py')

def main():
    if show_popup():
        run_script()
        messagebox.showinfo('Done', 'Script has finished running.')

if __name__ == "__main__":
    main()
