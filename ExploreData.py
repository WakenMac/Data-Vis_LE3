import pandas as pd
import geopy 

data = pd.read_csv("Datasets\\Prices_Retail_Jan 2000 to May 2026.csv")

# Gets the unique values per oolumn
for col in data.columns:
    print(col + ":")
    print(data[col].value_counts(), "\n")

# Filtering for data integrity & removal of unecessary columns
data = data[data['Collection Frequency'] == 'Monthly']
data = data[data['Data Type'] == 'Aggregated']

# Feature Engineering and Data Type Conversion
data['Price Date'] = pd.to_datetime(data['Price Date'], format="%d/%m/%Y")
data['Year'] = data['Price Date'].dt.year
data['Month'] = data['Price Date'].dt.month
data['Day'] = data['Price Date'].dt.day

fd = data.drop(labels=["Country", "Price Type", "Collection Frequency", 
    "Data Type", "Upper (95%) CI", "Lower (95%) CI", "Forecast Methodology", "Data Source", 
    "Currency", "Day"], axis=1)

fd.head()
for col in ['Commodity', 'Admin 1', 'Admin 2']:
    print(fd[col].value_counts(), "\n")

# Some info on the dataset:
# Eggs are the only produce sold per unit, the rest are in kilograms

# Form the z-score normalization
fd['Z_Score'] = fd.groupby('Commodity')['Price'].transform(
    lambda x: (x - x.mean()) / x.std(ddof=0)
)

# Form the coefficient of variation
fd = fd.sort_values(by=['Admin 1', 'Admin 2', 'Market Name', 'Commodity', 'Price Date'])
fd['Price_Fluctuation'] = fd.groupby(['Admin 1', 'Admin 2', 'Market Name', 'Commodity'])['Price'].diff()
fd['Percent_Change'] = fd.groupby(['Admin 1', 'Admin 2', 'Market Name', 'Commodity'])['Price'].pct_change() * 100
fd.head()

# Mapping the types of categories of commodities
category_mapping = {
    # Grains & Staples
    'Rice (regular, milled)': 'Grains & Staples', 'Rice (well milled)': 'Grains & Staples', 
    'Rice (special)': 'Grains & Staples', 'Rice (milled, superior)': 'Grains & Staples', 
    'Rice (premium)': 'Grains & Staples', 'Maize (yellow)': 'Grains & Staples', 
    'Maize (white)': 'Grains & Staples', 'Semolina (yellow)': 'Grains & Staples', 
    'Semolina (white)': 'Grains & Staples',
    
    # Meat & Poultry
    'Meat (pork)': 'Meat & Poultry', 'Meat (beef, chops with bones)': 'Meat & Poultry', 
    'Meat (chicken, whole)': 'Meat & Poultry', 'Eggs': 'Meat & Poultry', 
    'Meat (pork, with bones)': 'Meat & Poultry', 'Meat (beef)': 'Meat & Poultry', 
    'Eggs (duck)': 'Meat & Poultry', 'Meat (pork, hock)': 'Meat & Poultry', 
    'Chicken': 'Meat & Poultry',
    
    # Fish & Seafood
    'Fish (milkfish)': 'Fish & Seafood', 'Fish (roundscad)': 'Fish & Seafood', 
    'Fish (tilapia)': 'Fish & Seafood', 'Anchovies': 'Fish & Seafood', 
    'Shrimp (tiger)': 'Fish & Seafood', 'Crab': 'Fish & Seafood', 
    'Fish (redbelly yellowtail fusilier)': 'Fish & Seafood', 'Fish (slipmouth)': 'Fish & Seafood', 
    'Fish (fresh)': 'Fish & Seafood', 'Fish (threadfin bream)': 'Fish & Seafood', 
    'Shrimp (endeavor)': 'Fish & Seafood', 'Fish (mackerel, fresh)': 'Fish & Seafood', 
    'Fish (frigate tuna)': 'Fish & Seafood',
    
    # Fruits
    'Coconut': 'Fruits', 'Bananas (lakatan)': 'Fruits', 'Bananas (latundan)': 'Fruits', 
    'Calamansi': 'Fruits', 'Mangoes (carabao)': 'Fruits', 'Bananas (saba)': 'Fruits', 
    'Pineapples': 'Fruits', 'Mandarins': 'Fruits', 'Papaya': 'Fruits', 'Mangoes (piko)': 'Fruits',
    
    # Vegetables, Tubers & Legumes 
    'Tomatoes': 'Vegetables, Tubers & Legumes', 'Carrots': 'Vegetables, Tubers & Legumes', 
    'Cabbage': 'Vegetables, Tubers & Legumes', 'Onions (red)': 'Vegetables, Tubers & Legumes', 
    'Potatoes (Irish)': 'Vegetables, Tubers & Legumes', 'Eggplants': 'Vegetables, Tubers & Legumes', 
    'Bitter melon': 'Vegetables, Tubers & Legumes', 'Squashes': 'Vegetables, Tubers & Legumes', 
    'Beans (mung)': 'Vegetables, Tubers & Legumes', 'Choko': 'Vegetables, Tubers & Legumes', 
    'Ginger': 'Vegetables, Tubers & Legumes', 'Garlic': 'Vegetables, Tubers & Legumes', 
    'Beans (string)': 'Vegetables, Tubers & Legumes', 'Groundnuts (shelled)': 'Vegetables, Tubers & Legumes', 
    'Sweet potatoes': 'Vegetables, Tubers & Legumes', 'Beans (green, fresh)': 'Vegetables, Tubers & Legumes', 
    'Bottle gourd': 'Vegetables, Tubers & Legumes', 'Cabbage (chinese)': 'Vegetables, Tubers & Legumes', 
    'Onions (white)': 'Vegetables, Tubers & Legumes', 'Sweet Potato leaves': 'Vegetables, Tubers & Legumes', 
    'Groundnuts (unshelled)': 'Vegetables, Tubers & Legumes', 'Water spinach': 'Vegetables, Tubers & Legumes', 
    'Taro': 'Vegetables, Tubers & Legumes'
}

fd['Commodity_Type'] = fd['Commodity'].map(category_mapping)

# Checks if there exists a commodity that is not mapped
unmapped = fd[fd['Commodity_Type'].isna()]
if not unmapped.empty:
    print("Warning: The following items are missing a category:")
    print(unmapped['Commodity'].tolist())

fd['Price'] = fd['Price'].round(2)
fd['Percent_Change'] = fd['Percent_Change'].round(2)
fd['Price_Fluctuation'] = fd['Price_Fluctuation'].round(2)
fd.head()

fd.to_csv('Datasets\\prices_retail.csv', index = False)
