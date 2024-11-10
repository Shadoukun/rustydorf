import json
import requests
import tkinter as tk
from tkinter import ttk

response = requests.get('http://127.0.0.1:3000/dwarves')
data = response.json()

root = tk.Tk()
root.title("2Dorf 2Therapist")
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

def display_data_in_tab(tab_frame, data, parent_key=""):
    for i, (key, value) in enumerate(data.items()):
        label_key = f"{parent_key}.{key}" if parent_key else key
        label_key_widget = tk.Label(tab_frame, text=f"{label_key}:", anchor="w", width=20)
        label_key_widget.grid(row=i, column=0, padx=2, pady=2, sticky="w")

        label_value_widget = tk.Label(tab_frame, text=str(value), anchor="w", wraplength=500)
        label_value_widget.grid(row=i, column=1, padx=5, pady=0, sticky="w")

# Create a scrollable tab
def create_tab(entry):
    # Create the main frame for the tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=entry.get("first_name", "Unknown"))

    canvas = tk.Canvas(tab)
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar into the tab frame
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Display each field in rows within the scrollable frame
    display_data_in_tab(scrollable_frame, entry)


# Create a tab for each entry in the JSON data
for entry in data:
    create_tab(entry)

# Run the application
root.mainloop()