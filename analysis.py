import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import warnings

# Suppress minor warnings for clean output
warnings.filterwarnings('ignore')

# --- CONFIGURATION & AESTHETICS ---
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'sans-serif'

FILE_NAME = '/Users/bhoumik/Desktop/sixth_mass_extinction/red-list-index/red-list-index.csv'
VALUE_COL = 'Red List Index'

# --- LOAD AND CLEAN DATA ---
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    print(f"Error: Could not find {FILE_NAME}.")
    exit()

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors='coerce')
df = df.dropna(subset=['Year', VALUE_COL])

# ==========================================
# GRAPH 1: The "Wave of Red" Heatmap (Slide 1)
# ==========================================
countries_df = df[~df['Entity'].str.contains(r'UN SDG|World', na=False)].copy()
heatmap_data = countries_df.pivot(index='Entity', columns='Year', values=VALUE_COL)

latest_year = heatmap_data.columns.max()
worst_30 = heatmap_data.nsmallest(30, latest_year)

plt.figure(figsize=(14, 10))
sns.heatmap(worst_30, cmap="coolwarm_r", vmin=0.4, vmax=1.0, 
            cbar_kws={'label': 'Red List Index (Red = Critical Risk)'})
plt.title("The Wave of Red: 30 Most At-Risk Nations Over Time", fontsize=18, fontweight='bold', pad=20)
plt.ylabel("")
plt.xlabel("Year")
plt.tight_layout()
plt.savefig('Slide1_Wave_of_Red_Heatmap.png', dpi=300)
plt.close()
print("Generated Slide 1: Heatmap")

# ==========================================
# GRAPH 2 (NEW): The Expanding Tail (Violin Plot)
# ==========================================
# Get only countries, drop World and Regions
countries_only = df[~df['Entity'].str.contains(r'UN SDG|World', na=False)].copy()

# Select years at ~5 year intervals to keep the plot clean and readable
years_to_plot = [1993, 1998, 2003, 2008, 2013, 2018, 2024]
violin_data = countries_only[countries_only['Year'].isin(years_to_plot)]

fig, ax = plt.subplots(figsize=(14, 8))
# Plot the distribution of the RLI across all countries for these specific years
sns.violinplot(data=violin_data, x='Year', y=VALUE_COL, palette='coolwarm_r', inner='quartile', hue='Year', legend=False, ax=ax)

ax.set_title("The Expanding Tail of Extinction: RLI Distribution Across Nations", fontweight='bold', pad=20)
ax.set_ylabel("Red List Index (Closer to 0 = Extinction)")
ax.set_xlabel("Year")
plt.tight_layout()
plt.savefig('Slide2_Expanding_Tail_Violin.png', dpi=300)
plt.close()
print("Generated Slide 2: Violin Plot")

# ==========================================
# GRAPH 3A: Regional Divergence Scatter (Slide 3 - Static)
# ==========================================
regions_df = df[df['Entity'].str.contains(r'UN SDG', na=False)].copy()
if not regions_df.empty:
    pivot_reg = regions_df.pivot(index='Entity', columns='Year', values=VALUE_COL)
    start_y, end_y = pivot_reg.columns.min(), pivot_reg.columns.max()
    
    pivot_reg['Total_Drop'] = pivot_reg[end_y] - pivot_reg[start_y]
    pivot_reg['Entity_Clean'] = pivot_reg.index.str.replace(r' \(UN SDG\)', '', regex=True)
    
    fig, ax = plt.subplots()
    sns.scatterplot(x=start_y, y='Total_Drop', data=pivot_reg, 
                    s=600, color='#3498db', alpha=0.9, edgecolor='black', ax=ax)
    
    for i in range(pivot_reg.shape[0]):
        plt.text(pivot_reg[start_y].iloc[i] + 0.003, pivot_reg['Total_Drop'].iloc[i], 
                 pivot_reg['Entity_Clean'].iloc[i], fontsize=10)

    ax.set_title(f"Extinction Inequality: Baseline Health vs. Total Decline", fontweight='bold', pad=20)
    ax.set_xlabel(f"Baseline Red List Index ({start_y})")
    ax.set_ylabel(f"Total Change by {end_y} (Negative = Worse)")
    plt.axhline(0, color='grey', linestyle='--', linewidth=1)
    
    plt.tight_layout()
    plt.savefig('Slide3_Regional_Divergence.png', dpi=300)
    plt.close()
    print("Generated Slide 3: Regional Scatterplot")

# ==========================================
# GRAPH 3B: Animated Regional Drop (Slide 3 - Dynamic HTML)
# ==========================================
regions_clean = regions_df.copy()
regions_clean['Entity'] = regions_clean['Entity'].str.replace(r' \(UN SDG\)', '', regex=True)
regions_clean = regions_clean.sort_values(by=['Year', 'Entity'])

fig_dynamic = px.bar(
    regions_clean, x="Entity", y=VALUE_COL, color="Entity",
    animation_frame="Year", animation_group="Entity",
    range_y=[0.6, 1.0], 
    title="Dynamic Decline: Regional Red List Index (1993-2024)",
    labels={"Entity": "Region", VALUE_COL: "Red List Index"}
)
fig_dynamic.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})
fig_dynamic.write_html("Slide3_Dynamic_Animated_RLI.html")
print("Generated Slide 3 (Bonus): Dynamic HTML Animation")

# ==========================================
# GRAPH 4: Country Extremes (Slide 4)
# ==========================================
pivot_all = df.pivot(index='Entity', columns='Year', values=VALUE_COL)
start_y, end_y = pivot_all.columns.min(), pivot_all.columns.max()

countries = pivot_all[~pivot_all.index.str.contains(r'UN SDG|World', na=False)].copy()
countries.dropna(subset=[start_y, end_y], inplace=True)
countries['Change'] = countries[end_y] - countries[start_y]

extremes = pd.concat([countries.nsmallest(5, 'Change'), countries.nlargest(5, 'Change')]).sort_values('Change')
extremes_reset = extremes.reset_index()

fig, ax = plt.subplots()
colors = ['#e74c3c' if x < 0 else '#1abc9c' for x in extremes_reset['Change']]

sns.barplot(data=extremes_reset, x='Change', y='Entity', palette=colors, hue='Entity', legend=False, ax=ax)

ax.set_title(f"The Frontlines: Top 5 Worst and Best Performing Nations", fontweight='bold', pad=20)
ax.set_xlabel("Absolute Change in Red List Index")
ax.set_ylabel("")
plt.axvline(0, color='black', linewidth=1.5)

plt.tight_layout()
plt.savefig('Slide4_Country_Extremes.png', dpi=300)
plt.close()
print("Generated Slide 4: Extremes Bar Chart")

# ==========================================
# GRAPH 5: Forecasting the Cliff (Slide 5)
# ==========================================
world_df = df[df['Entity'] == 'World'].sort_values('Year').copy()
if not world_df.empty:
    world_clean = world_df.dropna(subset=[VALUE_COL])
    x = world_clean['Year']
    y = world_clean[VALUE_COL]
    
    # 2nd Degree Polynomial Fit for accelerating trend
    z2 = np.polyfit(x, y, 2)
    p2 = np.poly1d(z2)
    
    x_future = np.arange(x.min(), 2051)
    y_pred = p2(x_future)
    
    fig, ax = plt.subplots()
    sns.lineplot(x=x, y=y, color='black', linewidth=4, label='Historical Data', ax=ax)
    sns.lineplot(x=x_future[x_future >= x.max()], y=y_pred[x_future >= x.max()], 
                 color='#e74c3c', linestyle='--', linewidth=3, label='Accelerating Trend (Forecast)', ax=ax)
    
    ax.set_title("Forecasting the Cliff: Projected Global Extinction Risk to 2050", fontweight='bold', pad=20)
    ax.set_ylabel("Global Red List Index")
    ax.set_xlabel("Year")
    ax.set_xlim(x.min(), 2050)
    
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig('Slide5_Forecast.png', dpi=300)
    plt.close()
    print("Generated Slide 5: Polynomial Forecast")

print("\nSuccess! All visual assets are saved in your current directory.")