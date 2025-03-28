# Overview

I built a program that lets users build and analyze custom Pokémon teams using filters like generation, types, stats, and evolution levels.

The dataset I used contains information on over 1,300 Pokémon, including base stats, types, generation, and evolution levels. I found this dataset on Kaggle and added a custom evolution sheet for level-based evolutions.

My goal was to create a fun and interactive way to explore the dataset while learning to filter, sort, and visualize data using tools like Pandas and Matplotlib.

[Dataset](https://www.kaggle.com/datasets/rounakbanik/pokemon)

[Software Demo Video](http://youtube.link.goes.here)

# Data Analysis Results

#### **Which pokemon types have the highest average base stats?**
> Dragon, Psychic, and Steel types had the highest average total base stats across all generations.<br>

#### **Is there any connection betweek a pokemon's weight and total base stats?**
> Heavier Pokémon often have higher base stats, but there are many exceptions. The scatter plot showed a loose positive trend.<br>

#### **What are the weakness and strengths of a custom built team?**
> The program analyzes type matchups for your team and shows what types they are strong or weak against based on the type chart.<br>

# Development Environment

### **Tools:**
- VS Code
- Python
- Excel

### **Language:**
- Python

### **Libraries:**
- Pandas
- MatPlotLib
- TKinter
- Pillow

# Useful Websites

* [Pandas](https://pandas.pydata.org/docs/)
* [Kaggle Datasets](https://www.kaggle.com/)
* [MatPlotLib](https://matplotlib.org/stable/index.html)
* [Mplcursors](https://mplcursors.readthedocs.io/en/stable/)

# Future Work

* Display level of pokemon generated for team and what level it evolves last / next
* Add more interactive options for opponents team for speculation of good team mebers against theirs
* Allow for loading of team file to team can be analyzed at any point.