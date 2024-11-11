import json
import requests
import tkinter as tk
from tkinter import ttk


def display_data_in_tab(tab_frame, data, parent_key=""):
    name_label = data.get("first_name", "Unknown")
    name_widget = tk.Label(tab_frame, text=f"Name: {name_label}", anchor="nw", width=20)
    name_widget.grid(row=0, column=0, padx=5, pady=2, sticky="nw")

    profession_label = data.get("profession", "Unknown")['name']
    profession_widget = tk.Label(tab_frame, text=f"Profession: {profession_label}", anchor="nw", width=20)
    profession_widget.grid(row=0, column=1, padx=5, pady=2, sticky="nw")

    sex_label = data.get("sex", "Unknown")
    sex_widget = tk.Label(tab_frame, text=f"Sex: {sex_label}")
    sex_widget.grid(row=1, column=0, padx=5, pady=2, sticky="nw")

    age_label = data.get("age", "Unknown")
    age_widget = tk.Label(tab_frame, text=f"Age: {age_label}", anchor="nw", width=20)
    age_widget.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

    orientation_label = data.get("orientation", "Unknown")
    orientation_widget = tk.Label(tab_frame, text=f"Orientation: {orientation_label}", anchor="nw", width=20)
    orientation_widget.grid(row=2, column=0, padx=5, pady=2, sticky="nw")


    # Traits
    row = 0
    traits_widget = tk.Label(tab_frame, text="Traits:", anchor="nw", width=20)
    traits_widget.grid(row=row, column=2, padx=5, pady=0, sticky="nw")
    traits = data.get("traits", [])
    row += 1
    for idx, t in enumerate(traits):
        name = t[0]['name']
        value = t[1]
        trait_label = tk.Label(tab_frame, text=f"{name}: {value}", anchor="w", width=20)
        column = idx % 2
        trait_label.grid(row=row, column=column + 2, padx=5, pady=2, sticky="w")
        if column == 1:
            row += 1

    # Beliefs
    row = 3
    beliefs_widget = tk.Label(tab_frame, text="Beliefs:", anchor="nw", width=20)
    beliefs_widget.grid(row=row, column=0, padx=5, pady=2, sticky="nw")
    beliefs = data.get("beliefs", [])
    row += 1
    for idx, b in enumerate(beliefs):
        name = b[0]['name']
        value = b[1]
        belief_label = tk.Label(tab_frame, text=f"{name}: {value}", anchor="w", width=20)
        column = idx % 2
        belief_label.grid(row=row, column=column, padx=5, pady=2, sticky="w")
        if column == 1:
            row += 1

    # Goals
    goals_widget = tk.Label(tab_frame, text="Goals:", anchor="nw", width=20)
    goals_widget.grid(row=row, column=0, padx=5, pady=2, sticky="nw")
    goals = data.get("goals", [])
    row += 1
    for idx, g in enumerate(goals):
        name = g[0]['name']
        value = g[1]
        goal_label = tk.Label(tab_frame, text=f"{name}: {value}", anchor="w", width=20)
        column = idx % 2
        goal_label.grid(row=row, column=column, padx=5, pady=2, sticky="w")
        if column == 1:
            row += 1

    # for i, (key, value) in enumerate(data.items()):
    #     label_key = f"{parent_key}.{key}" if parent_key else key
    #     label_key_widget = tk.Label(tab_frame, text=f"{label_key}:", anchor="w", width=20)
    #     label_key_widget.grid(row=i, column=0, padx=2, pady=2, sticky="w")

    #     label_value_widget = tk.Label(tab_frame, text=str(value), anchor="w", wraplength=500)
    #     label_value_widget.grid(row=i, column=1, padx=5, pady=0, sticky="w")

# Create a scrollable tab
def create_tab(entry):
    # Create the main frame for the tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=entry.get("first_name", "Unknown"))

    canvas = tk.Canvas(tab)

    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    # Pack the canvas and scrollbar into the tab frame
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Display each field in rows within the scrollable frame
    display_data_in_tab(scrollable_frame, entry)


if __name__ == "__main__":
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()

    root = tk.Tk()
    root.title("2Dorf 2Therapist")
    notebook = ttk.Notebook(root)

    # Create a tab for each entry in the JSON data
    for entry in data:
        create_tab(entry)

    notebook.pack(expand=True, fill="both")
    # Configure columns to expand proportionally
    root.geometry("1000x500")
    root.mainloop()