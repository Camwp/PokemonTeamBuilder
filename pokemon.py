import pandas as pd
import random
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import mplcursors  # Import mplcursors for interactive hover labels
from PIL import Image, ImageTk  # Pillow for handling images


# Load evolution level data
evol_df = pd.read_excel("evols.xlsx")
evol_df.columns = evol_df.columns.str.strip().str.lower()

# Create a lookup to get the max evolved form by a given level
def get_final_evolution(name, max_level):
    current = name.lower()
    while True:
        evolutions = evol_df[(evol_df['evolving from'].str.lower() == current) & (evol_df['level'] <= max_level)]
        if evolutions.empty:
            return current
        current = evolutions.iloc[0]['evolving to'].lower()
q
# Helper to check if Pokémon is available at or below level
valid_pokemon_names_by_level = set()
for _, row in evol_df.iterrows():
    if row['level'] <= 100:
        valid_pokemon_names_by_level.add(row['evolving from'].lower())
        valid_pokemon_names_by_level.add(row['evolving to'].lower())

def is_pokemon_available_by_level(name, max_level):
    name = name.lower()
    for _, row in evol_df.iterrows():
        evolving_to = row['evolving to']
        if pd.isna(evolving_to):
            continue
        if evolving_to.lower() == name and row['level'] > max_level:
            return False
    return True

def manually_add_pokemon():
    """Allow the user to manually add a Pokémon to the team."""
    selected_item = manual_selection.get().strip().lower()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please enter a Pokémon name.")
        return
    
    selected_pokemon = df[df['name'].str.lower() == selected_item]
    if selected_pokemon.empty:
        messagebox.showinfo("Invalid Pokémon", "The Pokémon name entered is not valid.")
        return
    
    # Add to team
    pokemon = selected_pokemon.iloc[0]
    team_tree.insert("", "end", values=(pokemon['name'], pokemon['type1'], pokemon['type2'], 
                                        pokemon['hp'], pokemon['attack'], 
                                        pokemon['defense'], pokemon['speed']))
    messagebox.showinfo("Pokémon Added", f"{pokemon['name']} has been added to your team!")

def remove_pokemon():
    """Remove the selected Pokémon from the team."""
    selected_item = team_tree.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a Pokémon to remove.")
        return

    team_tree.delete(selected_item)
    messagebox.showinfo("Pokémon Removed", "The selected Pokémon has been removed from your team.")

def save_team():
    """Save the generated team to a CSV file."""
    if not team_tree.get_children():
        messagebox.showinfo("No Team Available", "Please generate or add Pokémon to a team first.")
        return
    
    team_list = []
    for row in team_tree.get_children():
        team_list.append(team_tree.item(row)['values'])
    
    team_df = pd.DataFrame(team_list, columns=["Name", "Type 1", "Type 2", "HP", "Attack", "Defense", "Speed"])
    team_df.to_csv("selected_team.csv", index=False)
    messagebox.showinfo("Team Saved", "Your team has been saved as 'selected_team.csv'.")

def swap_pokemon():
    selected_item = team_tree.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a Pokémon to swap.")
        return

    try:
        generation = int(gen_var.get())
        max_level = int(level_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid values for generation and level.")
        return

    prioritized_stat = stat_var.get().lower() if stat_var.get() and stat_var.get().lower() != "none" else None
    preferred_types = [t for t, var in type_vars.items() if var.get() == 1]
    excluded_types = [t for t, var in excluded_type_vars.items() if var.get() == 1]

    current_team_names = [team_tree.item(i)['values'][0].lower() for i in team_tree.get_children()]
    type_counts = {}
    for i in team_tree.get_children():
        t1 = team_tree.item(i)['values'][1].lower()
        t2 = team_tree.item(i)['values'][2].lower() if team_tree.item(i)['values'][2] else None
        for t in [t1, t2]:
            if t:
                type_counts[t] = type_counts.get(t, 0) + 1

    filtered_df = filter_by_generation(df, generation)
    if prioritized_stat in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=prioritized_stat, ascending=False)

    for _, pokemon in filtered_df.iterrows():
        name = pokemon['name'].lower()
        final_name = get_final_evolution(name, max_level)
        final_pokemon = df[df['name'].str.lower() == final_name]
        if final_pokemon.empty:
            continue

        pokemon = final_pokemon.iloc[0]
        if not is_pokemon_available_by_level(pokemon['name'], max_level):
            continue

        if pokemon['name'].lower() in current_team_names:
            continue

        if pokemon['type1'] in excluded_types or pokemon['type2'] in excluded_types:
            continue

        if type_counts.get(pokemon['type1'], 0) >= 2 or (pokemon['type2'] and type_counts.get(pokemon['type2'], 0) >= 2):
            continue

        # Found valid replacement
        team_tree.item(selected_item, values=(pokemon['name'], pokemon['type1'], pokemon['type2'], 
                                              pokemon['hp'], pokemon['attack'], 
                                              pokemon['defense'], pokemon['speed']))
        messagebox.showinfo("Pokémon Swapped", f"Swapped Pokémon with {pokemon['name']}.")
        return

    messagebox.showinfo("No Swap Available", "No suitable Pokémon found to swap in with current filters.")

def generate_team():
    global team
    try:
        generation_text = gen_var.get().strip()
        level_text = level_var.get().strip()

        try:
            generation = int(gen_var.get())
            level_text = level_var.get().strip()
            if not level_text:
                raise ValueError("Max level is required.")
            max_level = int(level_text)
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))
            return
    
        if not generation_text.isdigit():
            raise ValueError("Invalid numerical input.")

        
        generation = int(generation_text)
        max_level = int(level_text)

        if generation < 1 or generation > 8:
            raise ValueError("Generation must be between 1 and 8.")
        
        prioritized_stat = stat_var.get().lower() if stat_var.get() else None
        if prioritized_stat == "none":
            prioritized_stat == None
        preferred_types = [t for t, var in type_vars.items() if var.get() == 1] if type_vars else []
        excluded_types = [t for t, var in excluded_type_vars.items() if var.get() == 1] if excluded_type_vars else []
        
        filtered_df = filter_by_generation(df, generation)
        
        if filtered_df.empty:
            messagebox.showinfo("No Pokémon Found", "No Pokémon match the selected criteria. Try adjusting the filters.")
            return
        
        team = select_custom_team(filtered_df, prioritized_stat, preferred_types, excluded_types, max_level)
        
        for row in team_tree.get_children():
            team_tree.delete(row)
        
        for _, pokemon in team.iterrows():
            team_tree.insert("", "end", values=(pokemon['name'], pokemon['type1'], pokemon['type2'], 
                                                 pokemon['hp'], pokemon['attack'], 
                                                 pokemon['defense'], pokemon['speed']))
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numerical value for Generation (1-8).")

def load_pokemon_data(file_path):
    """Load and clean the Pokémon dataset."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()  # Ensure all columns are lowercase
    return df

def filter_by_generation(df, generation):
    """Filter Pokémon by generation."""
    return df[df['generation'] == generation]

def select_custom_team(df, prioritize_stat=None, preferred_types=None, excluded_types=None, max_level=None):
    if df.empty:
        return pd.DataFrame()

    if prioritize_stat and prioritize_stat in df.columns:
        df = df.sort_values(by=prioritize_stat, ascending=False)

    team = []
    used_types = set()

    for _, pokemon in df.iterrows():
        name = pokemon['name'].lower()
        final_name = get_final_evolution(name, max_level) if max_level is not None else name
        final_pokemon = df[df['name'].str.lower() == final_name]
        if final_pokemon.empty:
            continue

        pokemon = final_pokemon.iloc[0]

        if max_level is not None and not is_pokemon_available_by_level(pokemon['name'], max_level):
            continue

        pokemon_types = {pokemon['type1'], pokemon.get('type2', None)}

        if excluded_types and (pokemon['type1'] in excluded_types or pokemon['type2'] in excluded_types):
            continue

        if not used_types.intersection(pokemon_types) or (preferred_types and (pokemon['type1'] in preferred_types or pokemon['type2'] in preferred_types)):
            team.append(pokemon)
            used_types.update(pokemon_types)
        if len(team) == 6:
            break

    return pd.DataFrame(team)

def clear_team():
    """Clears the entire Pokémon team from the table and resets the team dataframe."""
    global team  # Ensure we're modifying the global team dataframe

    if not team_tree.get_children():
        messagebox.showinfo("No Team Available", "There is no team to clear.")
        return

    # Remove all items from the GUI table
    for row in team_tree.get_children():
        team_tree.delete(row)

    # Reset the team dataframe
    team = pd.DataFrame()

    messagebox.showinfo("Team Cleared", "Your team has been cleared successfully.")

def plot_type_strengths(df):
    """Plot average base stats per Pokémon type with interactivity."""
    type_stats = df.groupby('type1')[['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']].mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = type_stats.plot(kind='bar', ax=ax)
    plt.title("Average Base Stats by Pokémon Type")
    plt.xlabel("Type")
    plt.ylabel("Average Stat Value")
    plt.legend()
    plt.xticks(rotation=45)
    


    plt.show(block=False)

def plot_weight_vs_base_stats(df):
    """Plot Pokémon weight vs. base stats with interactivity."""
    if 'weight_kg' not in df.columns:
        messagebox.showerror("Error", "Column 'weight_kg' not found in dataset.")
        return
    
    df = df.dropna(subset=['weight_kg'])  # Remove rows where weight_kg is NaN
    
    fig, ax = plt.subplots(figsize=(10, 5))
    scatter = ax.scatter(df['weight_kg'], df['base_total'], alpha=0.5)
    plt.title("Weight vs Base Total Stats")
    plt.xlabel("Weight (kg)")
    plt.ylabel("Base Total Stats")
    
    # Add interactive labels
    cursor = mplcursors.cursor(scatter, hover=True)
    @cursor.connect("add")
    def on_hover(sel):
        index = sel.index
        sel.annotation.set_text(
            f"Name: {df.iloc[index]['name']}\nWeight: {df.iloc[index]['weight_kg']} kg\nBase Total: {df.iloc[index]['base_total']}"
        )

    plt.show(block=False)

def process_type_chart(chart):
    """Process the type effectiveness chart to normalize type names."""
    print("\n[DEBUG] Type Chart Initial Columns:", chart.columns.tolist())  # Debugging print

    # Ensure the first column is actually the type names
    if "Type" in chart.columns:
        chart.rename(columns={"Type": "type"}, inplace=True)
    else:
        # Assume the first column is the type names if there's no "Type" column
        chart.insert(0, "type", chart.index)
        chart.reset_index(drop=True, inplace=True)

    print("\n[DEBUG] Type Chart After Renaming Columns:", chart.columns.tolist())  # Debugging print

    # Normalize column names
    chart.columns = chart.columns.str.lower().str.strip()

    # Ensure type names in the column are properly formatted
    chart["type"] = chart["type"].astype(str).str.lower().str.strip()

    print("\n[DEBUG] Type Chart Before Setting Index:\n", chart.head())  # Debugging print

    # Ensure 'type' is used as an index
    chart.set_index("type", inplace=True)

    print("\n[DEBUG] Type Chart Index After Processing:", chart.index.tolist())  # Debugging print
    return chart

def load_type_chart(file_path):
    """Load and debug the Pokémon type effectiveness chart."""
    try:
        type_chart = pd.read_csv(file_path)

        # Log raw data for verification
        print("\n[DEBUG] Raw Type Chart Data:")
        print(type_chart.head(10))  # Show the first 10 rows

        # Log column headers before any modification
        print("\n[DEBUG] Type Chart Columns BEFORE processing:")
        print(type_chart.columns.tolist())

        # Normalize column names (strip spaces and lowercase)
        type_chart.columns = type_chart.columns.str.strip().str.lower()

        # Log column headers after normalization
        print("\n[DEBUG] Type Chart Columns AFTER processing:")
        print(type_chart.columns.tolist())

        # Ensure the "Type" column exists
        if 'type' not in type_chart.columns:
            print("\n[ERROR] 'Type' column not found in the CSV! Check formatting.")
            return None

        # Set "Type" as index for easy lookups
        type_chart.set_index("type", inplace=True)

        print("\n[INFO] Type Chart Successfully Loaded and Processed.")
        return type_chart

    except Exception as e:
        print(f"\n[ERROR] Failed to load type chart: {e}")
        return None

type_chart = load_type_chart("chart.csv")
if type_chart is None:
    print("[ERROR] Type Chart failed to load! Exiting...")
    exit()
type_chart = process_type_chart(type_chart)  # Apply normalization


def get_type_effectiveness(pokemon_type, type_chart):
    

    """Retrieve type effectiveness from the chart safely."""
    if pd.isna(pokemon_type):  # Handle missing type
        return None
    pokemon_type = pokemon_type.lower().strip()  # Normalize
    if pokemon_type not in type_chart.index:
        print(f"[ERROR] Type '{pokemon_type}' not found in type chart!")  # Debugging
        print("[DEBUG] Available Types in Chart:", type_chart.index.tolist())  # Log available types
        return None
    return type_chart.loc[pokemon_type]

def analyze_team():
    """Analyze the selected team and generate type effectiveness details."""
    if team.empty:
        messagebox.showinfo("No Team Available", "Please generate or select a team first.")
        return

    strongest_pokemon = team.loc[team['attack'].idxmax()]
    weakest_pokemon = team.loc[team['defense'].idxmin()]

    team_analysis = f"**Team Analysis & Stats**\n\n"
    team_analysis += f"**Strongest Pokémon:** {strongest_pokemon['name']} (Attack: {strongest_pokemon['attack']})\n"
    team_analysis += f"**Weakest Pokémon:** {weakest_pokemon['name']} (Defense: {weakest_pokemon['defense']})\n\n"

    # Generate type effectiveness details
    team_analysis += generate_team_recommendations(team, type_chart)

    # Display the analysis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0, 1, team_analysis, fontsize=12, verticalalignment='top', family="monospace")
    ax.axis("off")
    plt.title("Team Type Effectiveness Analysis")
    plt.show(block=False)

    plot_type_strengths(team)
    plot_weight_vs_base_stats(team)

def generate_team_recommendations(team, type_chart):
    
    """Analyze Pokémon team and display their type effectiveness."""
    report = "**Team Type Effectiveness Analysis**\n\n"

    for _, row in team.iterrows():
        p_name = row["name"]
        type1 = row["type1"]
        type2 = row["type2"] if pd.notna(row["type2"]) else None

        print(f"[DEBUG] Analyzing Pokémon: {p_name}, Type: {type1}/{type2 if type2 else ''}")

        type1_effectiveness = get_type_effectiveness(type1, type_chart)
        type2_effectiveness = get_type_effectiveness(type2, type_chart) if type2 else None

        if type1_effectiveness is not None:
            print(f"[DEBUG] {type1} Effectiveness:\n{type1_effectiveness}\n")

        if type2_effectiveness is not None:
            print(f"[DEBUG] {type2} Effectiveness:\n{type2_effectiveness}\n")

        strong_against = []
        weak_against = []

        # Combine effectiveness from both types (if dual-type)
        for t in type_chart.columns:
            type1_value = type1_effectiveness[t] if type1_effectiveness is not None else 1
            type2_value = type2_effectiveness[t] if type2_effectiveness is not None else 1
            total_effectiveness = type1_value * type2_value  # Combine for dual-types

            if total_effectiveness > 1:
                strong_against.append(t)
            elif total_effectiveness < 1:
                weak_against.append(t)

        report += f"🔹 **{p_name} ({type1}{'/' + type2 if type2 else ''})**\n"
        report += f"   - **Strong Against:** {', '.join(strong_against) if strong_against else 'None'}\n"
        report += f"   - **Weak Against:** {', '.join(weak_against) if weak_against else 'None'}\n\n"

    print(report)  # Print report for debugging
    return report

def analyze_all_pokemon():
    """Analyze all Pokémon in the dataset."""
    plot_type_strengths(df)
    plot_weight_vs_base_stats(df)


df = load_pokemon_data("pokemon.csv")
team = pd.DataFrame()

type_vars = {}
excluded_type_vars = {}



# === Begin Tkinter GUI ===
root = tk.Tk()
root.title("Pokémon Team Builder")
root.geometry("1000x750")
root.configure(bg="#4a4544")  # Light background color for a cleaner UI

# === Load and Set Background Image ===
bg_image = Image.open("pika.jpg")
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)  # Covers entire window

# === Title ===
title_label = tk.Label(root, text="Pokémon Team Builder", font=("Arial", 18, "bold"), bg="#ff5859")
title_label.grid(row=0, column=0, columnspan=3, pady=10)
tk.Button(root, text="Analyze All Pokémon", command=lambda: [plot_type_strengths(df), plot_weight_vs_base_stats(df)]).grid(row=1, column=0, columnspan=3, pady=10)

# === Generation Selection ===
gen_frame = ttk.LabelFrame(root, text="Select Generation")
gen_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

gen_var = tk.StringVar()
gen_dropdown = ttk.Combobox(gen_frame, textvariable=gen_var, values=[str(i) for i in range(1, 9)], state="readonly")
gen_dropdown.grid(row=0, column=0, padx=10, pady=5)

# === Stat Priority Selection ===
stat_frame = ttk.LabelFrame(root, text="Stat to Prioritize (Optional)")
stat_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

stat_var = tk.StringVar()
stat_dropdown = ttk.Combobox(stat_frame, textvariable=stat_var, values=["none","hp", "attack", "defense", "speed", "base_total"], state="readonly")
stat_dropdown.grid(row=0, column=0, padx=10, pady=5)



# === Preferred Types Selection ===
type_frame = ttk.LabelFrame(root, text="Select Preferred Types (Optional)")
type_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", 
         "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]

type_vars = {}
for i, t in enumerate(types):
    var = tk.IntVar()
    chk = tk.Checkbutton(type_frame, text=t, variable=var, bg="#f5f5f5")
    chk.grid(row=i // 6, column=i % 6, sticky="w", padx=5, pady=2)
    type_vars[t.lower()] = var

# === Excluded Types Selection ===
exclude_frame = ttk.LabelFrame(root, text="Select Types to Exclude (Optional)")
exclude_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

excluded_type_vars = {}
for i, t in enumerate(types):
    var = tk.IntVar()
    chk = tk.Checkbutton(exclude_frame, text=t, variable=var, bg="#f5f5f5")
    chk.grid(row=i // 6, column=i % 6, sticky="w", padx=5, pady=2)
    excluded_type_vars[t.lower()] = var

# === Manual Pokémon Entry ===
manual_frame = ttk.LabelFrame(root, text="Manually Add Pokémon")
manual_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

manual_selection = tk.StringVar()
manual_entry = tk.Entry(manual_frame, textvariable=manual_selection)
manual_entry.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
tk.Button(manual_frame, text="Add Pokémon", command=lambda: print("Adding Pokémon")).grid(row=0, column=1, padx=10, pady=5)

# UI addition for Level input
level_frame = ttk.LabelFrame(root, text="Max Level")
level_frame.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

level_var = tk.StringVar()
level_entry = tk.Entry(level_frame, textvariable=level_var)
level_entry.grid(row=0, column=0, padx=10, pady=5)



# === Button Grid ===
button_frame = tk.Frame(root, bg="#f5f5f5")
button_frame.grid(row=5, column=0, columnspan=3, pady=15)

buttons = [
    ("Generate Team", generate_team),
    ("Analyze Team", analyze_team),
    ("Save Team", save_team),
    ("Swap Pokémon", swap_pokemon),
    ("Remove Pokémon", remove_pokemon),
    ("Clear Team", clear_team),
]

for i, (text, command) in enumerate(buttons):
    tk.Button(button_frame, text=text, command=command, width=15).grid(row=i // 3, column=i % 3, padx=10, pady=5)

# === Team Display Table ===
team_frame = ttk.LabelFrame(root, text="Selected Pokémon Team")
team_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

columns = ("Name", "Type 1", "Type 2", "HP", "Attack", "Defense", "Speed")
team_tree = ttk.Treeview(team_frame, columns=columns, show="headings", height=10)

for col in columns:
    team_tree.heading(col, text=col)
    team_tree.column(col, width=120)

team_tree.pack(expand=True, fill="both")

# Make the grid columns responsive
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

root.mainloop()