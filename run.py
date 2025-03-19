import pandas as pd
import matplotlib.pyplot as plt

# Load the datasets
income_df = pd.read_csv("MEHOINUSCAA646N.csv")
housing_df = pd.read_csv("CASTHPI.csv")
cpi_df = pd.read_csv("CUURA422SA0.csv")

# Convert dates to datetime format
income_df["observation_date"] = pd.to_datetime(income_df["observation_date"])
housing_df["observation_date"] = pd.to_datetime(housing_df["observation_date"])
cpi_df["observation_date"] = pd.to_datetime(cpi_df["observation_date"])

# Extract year
income_df["Year"] = income_df["observation_date"].dt.year
housing_df["Year"] = housing_df["observation_date"].dt.year
cpi_df["Year"] = cpi_df["observation_date"].dt.year

# Aggregate CPI and Housing Price Index to yearly average
cpi_yearly = cpi_df.groupby("Year")["CUURA422SA0"].mean().reset_index()
housing_yearly = housing_df.groupby("Year")["CASTHPI"].mean().reset_index()

# Convert Housing Price Index to actual values (in thousands)
housing_yearly["CASTHPI"] = housing_yearly["CASTHPI"] * 1000

# Merge datasets on Year
merged_df = income_df.merge(housing_yearly, on="Year", how="inner")
merged_df = merged_df.merge(cpi_yearly, on="Year", how="inner")

# Rename columns
merged_df.rename(columns={
    "MEHOINUSCAA646N": "Median_Income",
    "CASTHPI": "Housing_Price_Index",
    "CUURA422SA0": "CPI"
}, inplace=True)

# Filter for years 1984-2023
merged_df = merged_df[(merged_df["Year"] >= 1984) & (merged_df["Year"] <= 2025)]

# Normalize values to show relative changes over time
merged_df["CPI_Normalized"] = merged_df["CPI"] / merged_df["CPI"].iloc[0]
merged_df["Housing_Price_Normalized"] = merged_df["Housing_Price_Index"] / merged_df["Housing_Price_Index"].iloc[0]
merged_df["Income_Normalized"] = merged_df["Median_Income"] / merged_df["Median_Income"].iloc[0]
merged_df["Affordability_Ratio_Normalized"] = merged_df["Housing_Price_Index"] / merged_df["Median_Income"]
merged_df["Affordability_Ratio_Normalized"] /= merged_df["Affordability_Ratio_Normalized"].iloc[0]

# Create a single figure with multiple subplots
fig, axs = plt.subplots(5, 1, figsize=(10, 30))

# Figure 1: CPI Over Time
axs[0].plot(merged_df["Year"], merged_df["CPI"], label="CPI", marker="o", color="g")
axs[0].set_xlabel("Year")
axs[0].set_ylabel("Consumer Price Index (CPI)")
axs[0].set_title("Figure 1: California CPI (1984-2024)")
axs[0].legend()
axs[0].grid(True)

# Figure 2: Median House Price Index
axs[1].plot(merged_df["Year"], merged_df["Housing_Price_Index"], label="Housing Price Index", marker="s", color="b")
axs[1].set_xlabel("Year")
axs[1].set_ylabel("House Price (Thousands)")
axs[1].set_title("Figure 2: California Median House Price Index (1984-2024)")
axs[1].legend()
axs[1].grid(True)

# Figure 3: Median Household Income
axs[2].plot(merged_df["Year"], merged_df["Median_Income"], label="Median Household Income", marker="d", color="r")
axs[2].set_xlabel("Year")
axs[2].set_ylabel("Income (Dollars)")
axs[2].set_title("Figure 3: California Median Household Income (1984-2023)")
axs[2].legend()
axs[2].grid(True)

# Figure 4: Adjusted Housing Affordability Ratio Over Time
axs[3].plot(merged_df["Year"], merged_df["Affordability_Ratio_Normalized"], label="Normalized Affordability Ratio (House Price / Income)", marker="x", color="m")
axs[3].set_xlabel("Year")
axs[3].set_ylabel("Affordability Ratio (Relative to 1984)")
axs[3].set_title("Figure 4: Adjusted Housing Affordability Ratio Over Time (1984-2023)")
axs[3].legend()
axs[3].grid(True)

# Figure 5: Overlay of All Trends (Normalized to Start at 1)
axs[4].plot(merged_df["Year"], merged_df["CPI_Normalized"], label="CPI", linestyle="-", color="g")
axs[4].plot(merged_df["Year"], merged_df["Housing_Price_Normalized"], label="Housing Price Index", linestyle="-", color="b")
axs[4].plot(merged_df["Year"], merged_df["Income_Normalized"], label="Median Household Income", linestyle="-", color="r")
axs[4].plot(merged_df["Year"], merged_df["Affordability_Ratio_Normalized"], label="Affordability Ratio", linestyle="-", color="m")
axs[4].set_xlabel("Year")
axs[4].set_ylabel("Relative Growth (1984=1)")
axs[4].set_title("Figure 5: Overlay of CPI, Housing Price, Income, and Affordability Ratio (Normalized)")
axs[4].legend()
axs[4].grid(True)

# Adjust layout and show the plots
plt.tight_layout()
plt.show()

# Save final processed data
merged_df.to_csv("processed_housing_data.csv", index=False)
