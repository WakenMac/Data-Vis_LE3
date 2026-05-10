# Study Overview: Philippine Commodity Price Dashboard

## Authors
- Waken Cean C. Maclang
- Jeff Ronyl R. Pausal
- Theo Benedict Pasia

## Objectives
The main objectives of this dashboard are:
- To provide people with a comprehensive overview of the Price Fluctuations of the 64 price commodities.
- To present a market-to-market comparison of prices across different regions in the Philippines.
- To create an interactive visual interface for users to explore the dashboard and determine different price hikes and fluctuations over time.

## Methodology
The **Z-Score** is used to determine how far a specific price point is from the historical average, measured in units of standard deviation. This allows for a "fair comparison" between commodities with vastly different price ranges (e.g., comparing a ₱5 increase in Rice vs. a ₱50 increase in Beef).

$$z = \\frac{x - \\mu}{\\sigma}$$

Where:
- **$x$**: The observed price.
- **$\\mu$ (Mu)**: The mean (average) price for that specific commodity.
- **$\\sigma$ (Sigma)**: The standard deviation of the price.

The **Coefficient of Variation (The Sensitivity Meter)**
While the Z-score looks at a single data point, the CV looks at the "spread" of a whole category. It is a dimensionless ratio, which makes it the best tool for comparing volatility across different scales.
