import pandas as pd
import geopy 

data = pd.read_csv("Datasets\\Prices-Export_Retail_Jan 2000 to May 2026.csv")

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

filtered_data = data.drop(labels=["Country", "Price Date", "Price Type", "Collection Frequency", 
    "Data Type", "Upper (95%) CI", "Lower (95%) CI", "Forecast Methodology", "Data Source", 
    "Currency", "Day"], axis=1)

filtered_data.head()
for col in ['Commodity', 'Admin 1', 'Admin 2']:
    print(filtered_data[col].value_counts(), "\n")

# Some info on the dataset:
# Eggs are the only produce sold per unit, the rest are in kilograms

# Form the z-score normalization
# Form the coefficient of variation
