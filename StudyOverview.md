# Study Overview: Philippine Commodity Price Dashboard

## Authors
- Waken Cean C. Maclang
- Jeff Ronyl R. Pausal
- Theo Benedict Pasia


## Introduction
Food security in the archipelagic Philippines is a multi-dimensional challenge influenced by geography, climate, and infrastructure. While broad inflationary metrics provide a national overview, they often mask the acute price disparities experienced in remote or urban-congested regions. This study shifts the focus from national averages to a granular, market-centric analysis of 64 commodities from 2000 to 2026.


## Problem Statement:
1. The "Price Gap" Problem: “To what extent do consumers in different local markets face price disparities for the same essential commodity, and which specific markets consistently maintain the lowest price floors?”
2. The "Volatility Vulnerability" Problem: “Which commodity categories (e.g., Grains vs. Seafood) exhibit the highest sensitivity to market shocks, and how has this sensitivity evolved over the last 12 months?”
3. The "Erosion of Value" Problem: “How has the purchasing power of consumers changed over a specific multi-year period, and what is the exact 'peso-impact' of these changes on a per-kilo basis?”
4. The "Commodity Divergence" Problem: “Within a single region, are all food groups rising in price simultaneously (systemic inflation), or are hikes isolated to specific categories like Meat & Poultry?”


## Objectives:
The primary objective of this Learning Evidence is to develop and implement a comprehensive dashboard utilizing different data visualization tools that utilizes automated price tracking and statistical normalization techniques to identify, analyze, and communicate commodity price volatility and market disparities across various regions and markets.

Specfically, it aims to address the following objectives:
1. To Quantify Inter-Market Price Equity: Present visualizations that identifies price disparities across local markets to pinpoint specific geographic "hotspots" where consumers face significantly higher price floors for essential commodities.
2. To Evaluate Cross-Category Volatility Sensitivity: Assess the relative price sensitivity of different food groups (e.g., Grains, Meat, Seafood) by utilizing the Coefficient of Variation (CV) to determine which sectors are most vulnerable to supply chain disruptions.
3. To Track Longitudinal Purchasing Power Erosion: Measure the specific "peso-impact" of commodity price changes over time by correlating historical price trends with a narrative summary of absolute price acceleration.
4. To Visualize Systemic vs. Isolated Inflationary Trends: Enable high-density sector scanning to determine if price increases are systemic across an entire region or isolated to specific commodity types, allowing for more targeted policy interventions.


## Dataset Description
To address the problems and objectives of the study, the researchers have utilized the data from the **World Food Programme's (WFP) VAM (Vulnerability Analysis and Mapping) Global Food Prices database**. The dataset spans a **26-year period** from 2000 to 2023, capturing market-level food price records across the Philippines throughout the said period for time-series analysis. 

The dataset comprises **216,474 records** representing price observations collected at the individual market level in the Philippines, collected every 15th of the month.


## Methodology

### Commodity Type
This column is feature-engineered to serve as a high-level categorical abstraction. While raw datasets often list specific items (e.g., "Well-milled Rice," "Regular-milled Rice," "Red Onion," "White Onion"), these individual labels can be too granular for identifying broad economic shifts.

| Commodity Type | Commodity List |
| -------- | -------- |
| Grains & Staples    | Rice (regular, milled) Rice (well milled), Rice (special), Rice (milled, superior), Rice (premium), Maize (yellow), Maize (white), Semolina (yellow), Semolina (white) |
| Meat & Poultry    | Meat (pork), Meat (beef, chops with bones), Meat (chicken, whole), Eggs, Meat (pork, with bones), Meat (beef), Eggs (duck), Meat (pork, hock), Chicken   |
| Fish & Seafood | Fish (milkfish), Fish (roundscad), Fish (tilapia), Anchovies, Shrimp (tiger), Crab, Fish (redbelly yellowtail fusilier), Fish (slipmouth), Fish (fresh), Fish (threadfin bream), Shrimp (endeavor), Fish (mackerel, fresh), Fish (frigate tuna) |
| Fruits | Coconut, Bananas (lakatan), Bananas (latundan), Calamansi, Mangoes (carabao), Bananas (saba), Pineapples, Mandarins, Papaya, Mangoes (piko) |
| Vegetables, Tubers & Legumes | Tomatoes, Carrots, Cabbage, Onions (red), Potatoes (Irish), Eggplants, Bitter melon, Squashes, Beans (mung), Choko, Ginger, Garlic, Beans (string), Groundnuts (shelled), Sweet potatoes, Beans (green, fresh), Bottle gourd, Cabbage (chinese), Onions (white), Sweet Potato leaves, Groundnuts (unshelled), Water spinach, Taro |

\
This is designed for the following purposes:
1. Statistical Power for Volatility Metrics: To calculate the Coefficient of Variation (CV) effectively, by clustering data points through commodity types
2. Dimensionality Reduction: Through maximizing aggregates (e.g., mean, min, max, and std) to minimize the number of data points displayed
3. Economic Behavioral Analysis: Different types of food follow different supply chain rules. Categorizing them allows you to see if a price hike is a "Seafood-only" seasonal issue or a "Systemic" inflation affecting all types.
4. Trend Normalization: It allows for "Apples-to-Apples" comparisons. You can compare the average Z-score of the "Meat" sector against the "Vegetables" sector to see which part of the consumer's basket is under the most stress.

### The Z-Score
The *Z-Score* is used to determine how far a specific price point is from the historical average, measured in units of standard deviation. This allows for a "fair comparison" between commodities with vastly different price ranges (e.g., comparing a ₱5 increase in Rice vs. a ₱50 increase in Beef).

$$z = \frac{x - \\mu}{\\sigma}$$

Where:
- **$x$**: The observed price.
- **$\\mu$ (Mu)**: The mean (average) price for that specific commodity.
- **$\\sigma$ (Sigma)**: The standard deviation of the price.

### The Coefficient of Variation

The **Coefficient of Variation (The Sensitivity Meter)**
While the *Z-score* looks at a single data point, the CV looks at the "spread" of a whole category. It is a dimensionless ratio, which makes it the best tool for comparing volatility across different scales. The formula below was used for calculating the Coefficient of Variation (CV)

$$CV = \\frac{\\sigma}{\\mu}$$
- **$\\sigma$ (Sigma)**: The Standard Deviation of the price data.
- **$\\mu$ (Mu)**: The Mean (Average) of the price data.

Interpretation:
- **Low CV**: Indicates that the data points are close to the mean, suggesting price stability across markets or over time.
- **High CV**: Indicates a high level of dispersion relative to the mean, suggesting price volatility or significant price differences between markets.


