import pandas as pd
import random
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import mplcursors  # Import mplcursors for interactive hover labels

def load_pokemon_data(file_path):
    """Load and clean the Pokémon dataset."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()  # Ensure all columns are lowercase
    return df

def filter_by_generation(df, generation):
    """Filter Pokémon by generation."""
    return df[df['generation'] == generation]

def select_custom_team(df, prioritize_stat=None, preferred_types=None):
    """Select a custom team of 6 Pokémon based on user preferences."""
    if df.empty:
        return pd.DataFrame()
    
    if prioritize_stat and prioritize_stat in df.columns:
        df = df.sort_values(by=prioritize_stat, ascending=False)
    
    team = []
    used_types = set()
    
    for _, pokemon in df.iterrows():
        pokemon_types = {pokemon['type1'], pokemon.get('type2', None)}
        if not used_types.intersection(pokemon_types) or (preferred_types and (pokemon['type1'] in preferred_types or pokemon['type2'] in preferred_types)):
            team.append(pokemon)
            used_types.update(pokemon_types)
        if len(team) == 6:
            break
    
    return pd.DataFrame(team)



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


def analyze_team():
    """Analyze the selected team."""
    if team.empty:
        messagebox.showinfo("No Team Available", "Please generate or select a team first.")
        return
    
    strongest_pokemon = team.loc[team['attack'].idxmax()]
    weakest_pokemon = team.loc[team['defense'].idxmin()]
    
    messagebox.showinfo("Team Analysis", 
                        f"Strongest Pokémon (Highest Attack): {strongest_pokemon['name']}\n"
                        f"Weakest Pokémon (Lowest Defense): {weakest_pokemon['name']}")
    
    plot_type_strengths(team)
    plot_weight_vs_base_stats(team)

def remove_pokemon():
    """Remove the selected Pokémon from the team."""
    selected_item = team_tree.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a Pokémon to remove.")
        return

    team_tree.delete(selected_item)
    messagebox.showinfo("Pokémon Removed", "The selected Pokémon has been removed from your team.")


def analyze_all_pokemon():
    """Analyze all Pokémon in the dataset."""
    plot_type_strengths(df)
    plot_weight_vs_base_stats(df)


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
    """Allow the user to swap out a selected Pokémon."""
    selected_item = team_tree.selection()
    if not selected_item:
        messagebox.showinfo("No Selection", "Please select a Pokémon to swap.")
        return
    
    available_pokemon = df.sample(n=1).iloc[0]
    
    team_tree.item(selected_item, values=(available_pokemon['name'], available_pokemon['type1'], available_pokemon['type2'], 
                                          available_pokemon['hp'], available_pokemon['attack'], 
                                          available_pokemon['defense'], available_pokemon['speed']))
    messagebox.showinfo("Pokémon Swapped", f"Swapped Pokémon with {available_pokemon['name']}.")

def generate_team():
    global team
    try:
        generation_text = gen_var.get().strip()
        
        if not generation_text.isdigit():
            raise ValueError("Invalid numerical input.")
        
        generation = int(generation_text)
        
        if generation < 1 or generation > 8:
            raise ValueError("Generation must be between 1 and 8.")
        
        prioritized_stat = stat_var.get().lower() if stat_var.get() else None
        preferred_types = [t for t, var in type_vars.items() if var.get() == 1] if type_vars else []
        
        filtered_df = filter_by_generation(df, generation)
        
        if filtered_df.empty:
            messagebox.showinfo("No Pokémon Found", "No Pokémon match the selected criteria. Try adjusting the filters.")
            return
        
        team = select_custom_team(filtered_df, prioritized_stat, preferred_types)
        
        for row in team_tree.get_children():
            team_tree.delete(row)
        
        for _, pokemon in team.iterrows():
            team_tree.insert("", "end", values=(pokemon['name'], pokemon['type1'], pokemon['type2'], 
                                                 pokemon['hp'], pokemon['attack'], 
                                                 pokemon['defense'], pokemon['speed']))
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numerical value for Generation (1-8).")

df = load_pokemon_data("pokemon.csv")
team = pd.DataFrame()

type_vars = {}

root = tk.Tk()
root.title("Pokémon Team Builder")
root.geometry("1000x700")

tk.Label(root, text="Select Generation (1-8):").pack()
gen_var = tk.StringVar()
gen_dropdown = ttk.Combobox(root, textvariable=gen_var, values=[str(i) for i in range(1, 9)])
gen_dropdown.pack()

tk.Label(root, text="Select Stat to Prioritize (Optional):").pack()
stat_var = tk.StringVar()
stat_dropdown = ttk.Combobox(root, textvariable=stat_var, values=["hp", "attack", "defense", "speed", "base_total"])
stat_dropdown.pack()

tk.Label(root, text="Select Preferred Types (Optional):").pack()
type_frame = tk.Frame(root)
type_frame.pack()
types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", 
         "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
type_vars = {}
for i, t in enumerate(types):
    var = tk.IntVar()
    chk = tk.Checkbutton(type_frame, text=t, variable=var)
    chk.grid(row=i//6, column=i%6, sticky='w')
    type_vars[t.lower()] = var

tk.Label(root, text="Manually Add Pokémon:").pack()
manual_selection = tk.StringVar()
manual_entry = tk.Entry(root, textvariable=manual_selection)
manual_entry.pack()
tk.Button(root, text="Add Pokémon", command=manually_add_pokemon).pack()

tk.Button(root, text="Analyze All Pokémon", command=lambda: [plot_type_strengths(df), plot_weight_vs_base_stats(df)]).pack()

tk.Button(root, text="Generate Team", command=generate_team).pack()
tk.Button(root, text="Analyze Team", command=analyze_team).pack()
tk.Button(root, text="Swap Pokémon", command=swap_pokemon).pack()
tk.Button(root, text="Save Team", command=save_team).pack()
tk.Button(root, text="Remove Pokémon", command=remove_pokemon).pack()

columns = ("Name", "Type 1", "Type 2", "HP", "Attack", "Defense", "Speed")
team_tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    team_tree.heading(col, text=col)
    team_tree.column(col, width=120)
team_tree.pack(expand=True, fill="both")

root.mainloop()
