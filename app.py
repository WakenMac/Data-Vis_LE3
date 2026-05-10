from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from plotnine import ggplot, aes, geom_point, theme_minimal
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('Datasets\\prices_retail.csv')
df['Price Date'] = pd.to_datetime(df['Price Date'])
latest_date = df['Price Date'].max()

recent_df = df[df['Price Date'] == latest_date]
avg_recent_df = recent_df.groupby('Commodity')[['Price', 'Price_Fluctuation', 'Percent_Change']].mean().reset_index()
avg_recent_df['Price'] = avg_recent_df['Price'].round(2)
avg_recent_df['Percent_Change'] = avg_recent_df['Percent_Change'].round(2)
avg_recent_df['Price_Fluctuation'] = avg_recent_df['Price_Fluctuation'].round(2)
avg_recent_df.rename(columns={
    'Price_Fluctuation': 'Change',
    'Percent_Change': '(%)'}, inplace=True)
all_months = df['Price Date'].dt.strftime('%b %Y').unique().tolist()
all_months.reverse()

# For Summary Page: Filter 1
CHOICES = [ 
    "National", "Region I", "Region II", "Region III", "Cordillera Administrative region", "National Capital region",
    "Region IV-A", "Region IV-B", "Region V", "Region VI", "Region VII", "Region VIII", "Region IX", "Region X", 
    "Region XI", "Region XII", "Region XIII", "Autonomous region in Muslim Mindanao", 
]

# For Summary Page: Filter 2
COMMODITY_TYPES = ["All", "Grains & Staples", "Meat & Poultry", "Fish & Seafood", "Vegetables, Tubers & Legumes", "Fruits"]

def summary_page():
    """The instant-insight page"""

    z_score_summary_card = ui.card(
        ui.h4("Average Price Fluctuation per Commodity Type"),
        ui.p(
            ui.HTML(
                'Here lies the change in prices between February and March.<br>'
                'The <em>Z-score</em> is a normalized format of price for fair comparison between different price ranges of '
                'different commodities. Their values represent <strong>how much standard deviations</strong> the recent price '
                'is far from the <strong>historical average price</strong> for a commodity.'
            ), 
            style="color: #666; font-size: 0.9em;"
        ),
        output_widget("monthly_z_comparison"),
    ),

    tables_section = ui.navset_tab(
        # TAB 1: The Quick Look
        ui.nav_panel(
            "Quick View",
            ui.card(
                ui.h4("Recent Top Commodity Price Hikes and Rollbacks"),
                ui.output_ui("dynamic_subtitle"),
                ui.layout_columns(
                    ui.card(
                        ui.h5("Top 5 Price Rollbacks", style="color: #28a745;"), 
                        ui.output_data_frame("rollback_table")
                    ),
                    ui.card(
                        ui.h5("Top 5 Price Hikes", style="color: #dc3545;"), 
                        ui.output_data_frame("hikes_table")
                    ),
                    gap="1rem"
                )
            )
        ),

        ui.nav_panel(
            "Inter-Market Comparison",
            ui.card(
                ui.h4("Comparison of Commodity Prices across the different Regional Markets"),
                ui.p(
                    ui.HTML(
                        "View which market sells your commodity at a <strong>cheaper</strong> price! <br>"
                    ), 
                    style="color: #666; font-size: 0.9em;"
                ),
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.h5("Market Analysis"),
                        ui.input_select(
                            "comparison_type",
                            "Step 1: Select Commodity Type",
                            choices=COMMODITY_TYPES,
                            selected=COMMODITY_TYPES[0]
                        ),

                        ui.input_select(
                            "comparison_commodity",
                            "Step 2: Select Specific Commodity",
                            choices=[] 
                        ),

                        position="left",
                        open="always",
                        bg="#f8f9fa"
                    ),

                    output_widget("market_comparison_chart"),
                    style="height: 400px; overflow-y: auto; padding: 0px;"
                )
            )
        ),
        
        # TAB 2: The Deep Dive (Revealed when card is explored)
        ui.nav_panel(
            "Market Deep-Dive",
            ui.card(
                ui.output_ui('dynamic_deep_dive'),
                ui.p(
                    ui.HTML(
                        "View the prices of your different commodities in your selective markets here! <br>"
                        "The <em>\"Change\"</em> column means the <strong>increase</strong> or <strong>decrease</strong> in price from last month. <br>"
                        "Select your market through the filter below"
                    ), 
                    style="color: #666; font-size: 0.9em;"
                ),
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.h5("Market Analysis"),
                        # This selector will be populated dynamically based on the region
                        ui.input_select("market_select", "Pick a Market:", choices=[]),
                        open="always"
                    ),
                    # The detailed table with ALPS logic
                    ui.output_data_frame("market_alps_table"),
                    style="height: 400px; overflow-y: auto; padding: 0px;"
                )
            )
        )
    )

    regional_analytics_section = ui.card(
        ui.layout_sidebar(
            # The sidebar is now inside the card
            ui.sidebar(
                ui.h4("Regional Filters"),
                ui.input_radio_buttons(
                    "region_filter",  
                    ui.span("Select Region:", style="margin-bottom: 15px; display: block;"),
                    choices=CHOICES,
                    selected="National Capital region"
                ),
                position="left", 
                open="desktop",
                bg="#f8f9fa",
                resizable=False
            ),
            
            ui.div(
                z_score_summary_card,
                tables_section,
                ui.br(),
                ui.card(
                    ui.h4("Magnitude of price changes for the past 12 months"),
                    ui.p(
                        ui.HTML(
                            "<em>Coefficient of Variation</em> (CV) measures the magnitude of price fluctuations.<br>"
                            "The <strong>higher</strong> the CV, the <strong>greater</strong> the price fluctuations."
                        ), 
                        style="color: #666; font-size: 0.9em;"
                    ),
                    output_widget("volatility_chart"),
                )
            )
        ),
        full_screen=True
    )

    z_score_section = ui.card(
        ui.h4("Regional Average Price Ranges (Z-Score Distribution)"),
        ui.p(
            ui.HTML(
                'Plots the different prices (<em>z-score</em>) of a commodity type across the 16 Philippine Regions.<br>'
                'The <strong>greener</strong> (smaller z-score) the bar, the <strong>cheaper</strong> the commodity type is in the particular region.'
            ), 
            style="color: #666; font-size: 0.9em;"
        ),
        ui.layout_sidebar(
            ui.sidebar(
                ui.h5("Commodity Filter"),
                ui.input_select(
                    "commodity_type_filter",
                    "Select Category:",
                    choices=COMMODITY_TYPES,
                    selected="All"
                ),
                # Set to left to stay out of the way of your main right-side sidebar
                position="left", 
                bg="#f8f9fa" 
            ),
            # The plot area
            output_widget("z_score_plot"),
        ),
        full_screen=True
    )
    
    return ui.nav_panel(
        "Summary",
        ui.div(
            regional_analytics_section,
            ui.br(),
            z_score_section
        )
    )

def historical_data_page():
    """The instant-insight page"""

    style = ui.tags.style("""
        .bslib-sidebar-layout {
            --bslib-sidebar-width: 250px; /* Force a specific width */
        }
        .bslib-sidebar-layout[data-bslib-sidebar-position="top"] > .sidebar {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: white;
            border-bottom: 2px solid #007bff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Make the sidebar a bit taller to fit the labels nicely */
        .bslib-sidebar-layout[data-bslib-sidebar-position="top"] > .sidebar-content {
            padding: 15px 20px;
        }
    """)

    sidebar = ui.sidebar(
        ui.div(ui.input_select("hist_region", "Region", CHOICES)),
        ui.div(ui.input_select("hist_type", "Commodity Type", COMMODITY_TYPES)),
        ui.div(ui.input_select("hist_commodity", "Commodity", [])),
        ui.div(
            ui.input_date_range(
                "hist_dates", 
                "Select Timeframe",
                start="2024-01-15",
                end="2026-01-15",
                min="2000-01-15",
                max="2026-03-15",
                format="yyyy-mm-dd",
                separator=" to "
            )
        ),
        
        position="top",
        open="desktop",
        bg="#f8f9fa",
        resizable=False,
        width=300
    )

    return ui.nav_panel(
        "Historical Data",
        style,
        ui.layout_sidebar(
            sidebar,

            ui.card(
                ui.output_ui("price_narrative_summary"),
                style="border-left: 5px solid #007bff; background-color: #f0f7ff;" # Left-accent border
            ),

            ui.card(
                ui.output_ui('hist_trend_chart_header'),
                ui.p(
                    ui.HTML('The <strong>average price</strong> of a commodity across the different markets in the region'), 
                    style="color: #666; font-size: 0.9em;"
                ),
                output_widget("historical_trend_data"),
                full_screen=True
            ),

            ui.card(
                output_widget("market_min_max_plot"),
                full_screen=True
            ),

            style="padding: 20px;",
            fillable=False
        )
    )

def info_page():
    """The About/Context page."""
    return ui.nav_panel(
        "Info",
        ui.h3("About This Dashboard"),
        ui.markdown("""
        
        #### Authors: 

        **Dataset:** WFP VAM Price Dataset
        
        **Data Dictionary:**
        * `Admin 1` / `Admin 2`: Regional and provincial boundaries.
        * `Commodity`: The specific food or non-food item.
        * `ALPS Phase`: Alert for Price Spikes indicator.
        * `Pewi`: Price Equivalent Wealth Index.
        
        #### Methodology: Price Volatility & Normalization

        This document outlines the mathematical foundations for analyzing commodity price fluctuations using Z-Scores and the Coefficient of Variation (CV).

        ---

        ###### 1. Z-Score (Standard Score)

        The **Z-Score** is used to determine how far a specific price point is from the historical average, measured in units of standard deviation. This allows for a "fair comparison" between commodities with vastly different price ranges (e.g., comparing a ₱5 increase in Rice vs. a ₱50 increase in Beef).

        ####### The Formula
        $$z = \\frac{x - \\mu}{\\sigma}$$

        Where:
        - **$x$**: The observed price.
        - **$\\mu$ (Mu)**: The mean (average) price for that specific commodity.
        - **$\\sigma$ (Sigma)**: The standard deviation of the price.

        ### Python Implementation
        In your system, you utilize the `.transform()` method to apply this calculation across grouped commodities:

        ```python
        fd['Z_Score'] = fd.groupby('Commodity')['Price'].transform(
            lambda x: (x - x.mean()) / x.std(ddof=0)
        )
        """)
    )


app_ui = ui.page_fluid(
    # Header for the whole dashboard
    ui.h2("The 26-year Philippine Food Price Dynamics", style="padding: 15px 0px; border-bottom: 1px solid #ccc;"),
    
    # The crucial function for left-sided navigation
    ui.navset_pill_list(
        info_page(),
        summary_page(),
        historical_data_page(),
        id="main_nav",
        well=True, # Adds a subtle background behind the navigation pills
        widths=(2, 10)
    )
)

def server(input, output, session):
    
    # Summary Filter: By Region
    @reactive.calc
    def filtered_data():
        selected_region = input.region_filter()
        
        if not selected_region:
            return pd.DataFrame(columns=df.columns)
        if selected_region == "National":
            return df

        return df[df['Admin 1'] == selected_region]

    # Z-Score Summary Chart (Lollipop Chart)
    @render_widget
    def monthly_z_comparison():
        # 1. Get region-filtered data
        df_region = filtered_data()
        if df_region.empty:
            return go.Figure().update_layout(title="No data available.")

        # 2. Filter and Pivot
        # Focus on Feb and March 2026
        mask = (df_region['Price Date'].dt.year == 2026) & (df_region['Price Date'].dt.month.isin([2, 3]))
        comparison_df = df_region[mask].copy()
        comparison_df['Month'] = comparison_df['Price Date'].dt.month_name()

        # Calculate Mean Z-Score per Category and Month
        stats = comparison_df.groupby(['Commodity_Type', 'Month'])['Z_Score'].mean().round(2).reset_index()

        # Pivot so we have 'February' and 'March' as columns
        pivot_df = stats.pivot(index='Commodity_Type', columns='Month', values='Z_Score').reset_index()
        
        # Ensure both months exist to avoid errors
        if 'February' not in pivot_df.columns or 'March' not in pivot_df.columns:
            return go.Figure().update_layout(title="Insufficient data for monthly comparison.")

        # 3. Build the Dumbbell Plot
        fig = go.Figure()

        # Add the Connector Lines (The "Bar" of the dumbbell)
        for i in range(len(pivot_df)):
            fig.add_trace(go.Scatter(
                x=[pivot_df['February'][i], pivot_df['March'][i]],
                y=[pivot_df['Commodity_Type'][i], pivot_df['Commodity_Type'][i]],
                mode='lines',
                line=dict(color='#cbd5e1', width=3), # Light slate gray line
                showlegend=False,
                hoverinfo='none'
            ))

        # Add February Points (The Baseline)
        fig.add_trace(go.Scatter(
            x=pivot_df['February'],
            y=pivot_df['Commodity_Type'],
            mode='markers',
            name='February',
            marker=dict(color='#94a3b8', size=12) # Muted gray
        ))

        # Add March Points (The Current State)
        fig.add_trace(go.Scatter(
            x=pivot_df['March'],
            y=pivot_df['Commodity_Type'],
            mode='markers',
            name='March',
            marker=dict(color='#3b82f6', size=12) # Active blue
        ))

        # 4. Styling the Layout
        fig.update_layout(
            xaxis_title="Average Z-Score (National Deviation)",
            yaxis_title="",
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="closest"
        )
        
        # Add the 0-line for "National Average" reference
        fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.3)

        return fig

    # Dynamic Subtitles
    @render.ui
    def dynamic_subtitle():
        # 1. Grab the reactively filtered dataset
        current_df = filtered_data()
        
        # 2. Safety check: If the user clears the filter, provide fallback text
        if current_df.empty:
            return ui.p(
                "Please select a region to view market data.", 
                style="color: #666; font-size: 0.9em;"
            )
            
        # 3. Calculate the variables
        # .nunique() is a Pandas trick that counts the number of UNIQUE markets
        num_markets = current_df['Market Name'].nunique()
        region_name = input.region_filter()
        
        # 4. Construct the dynamic string
        text_content = f"Listed are the different changes in price. Averaged based on the {num_markets} markets in the {region_name}."
        
        # 5. Return it wrapped in the styled paragraph tag
        return ui.p(text_content, style="color: #666; font-size: 0.9em;")
    
    # Rollback Table
    @render.data_frame
    def rollback_table():
        current_df = filtered_data()
        
        if current_df.empty:
            # Returns a blank table with the correct column headers
            empty_df = pd.DataFrame(columns=['Commodity', 'Price', 'Change', '(%)'])
            return render.DataGrid(empty_df)
            
        latest_date = current_df['Price Date'].max()
        recent_df = current_df[current_df['Price Date'] == latest_date]
        avg_recent_df = recent_df.groupby('Commodity')[['Price', 'Price_Fluctuation', 'Percent_Change']].mean().reset_index()
        avg_recent_df['Price'] = avg_recent_df['Price'].round(2)
        avg_recent_df['Price_Fluctuation'] = avg_recent_df['Price_Fluctuation'].round(2)
        avg_recent_df['Percent_Change'] = avg_recent_df['Percent_Change'].round(2)
        
        avg_recent_df.rename(columns={
            'Price_Fluctuation': 'Change',
            'Percent_Change': '(%)'
        }, inplace=True)
        
        rollbacks = avg_recent_df.nsmallest(5, '(%)')
        
        return render.DataGrid(rollbacks)

    # Hike table
    @render.data_frame
    def hikes_table():
        current_df = filtered_data()
        
        if current_df.empty:
            empty_df = pd.DataFrame(columns=['Commodity', 'Price', 'Change', '(%)'])
            return render.DataGrid(empty_df)
            
        latest_date = current_df['Price Date'].max()
        recent_df = current_df[current_df['Price Date'] == latest_date]
        avg_recent_df = recent_df.groupby('Commodity')[['Price', 'Price_Fluctuation', 'Percent_Change']].mean().reset_index()
        avg_recent_df['Price'] = avg_recent_df['Price'].round(2)
        avg_recent_df['Price_Fluctuation'] = avg_recent_df['Price_Fluctuation'].round(2)
        avg_recent_df['Percent_Change'] = avg_recent_df['Percent_Change'].round(2)
        
        avg_recent_df.rename(columns={
            'Price_Fluctuation': 'Change',
            'Percent_Change': '(%)'
        }, inplace=True)
        hikes = avg_recent_df.nlargest(5, '(%)')
        
        return render.DataGrid(hikes)

    # Summary Filter: By Market (Deep Dive)
    @reactive.effect
    def _update_markets():
        current_df = filtered_data()
        if not current_df.empty:
            markets = sorted(current_df['Market Name'].unique().tolist())
            ui.update_select("market_select", choices=markets)

    # Inter-Market Comparison: Update Commodity List
    @reactive.effect
    def _update_comparison_commodities():
        selected_type = input.comparison_type()
        
        if not selected_type:
            return

        # 2. Filter the global dataframe for that specific type
        # Assuming your global data is 'df'
        filtered_list = None
        if selected_type != 'All':
            filtered_list = df[df['Commodity_Type'] == selected_type]
        else:
            filtered_list = df

        # 3. Extract unique commodity names and sort them
        available_commodities = sorted(filtered_list['Commodity'].unique().tolist())
        
        # 4. Update the UI element directly
        ui.update_select(
            "comparison_commodity",
            choices=available_commodities,
            selected=available_commodities[0] if available_commodities else None
        )

    # Inter-Market Comparison: Horizontal Bar Chart
    @render_widget
    def market_comparison_chart():
        # 1. Reactive Filtering
        target_commodity = input.comparison_commodity()
        if not target_commodity:
            return px.bar(title="Select a commodity to see comparison")

        # 2. Extract data for this specific commodity
        # Use the global 'df' or your reactive filtered_data()
        comp_df = filtered_data()
        comp_df = comp_df[comp_df['Commodity'] == target_commodity].copy()
        
        # 3. CRITICAL: Filter for the most recent date available for this item
        latest_date = comp_df['Price Date'].max()
        recent_comp_df = comp_df[comp_df['Price Date'] == latest_date].copy()
        
        # 4. SORT: Cheapest at the top
        # In Plotly horizontal bars, the 'top' of the chart corresponds to the 
        # start of the dataframe if we reverse the Y-axis.
        recent_comp_df = recent_comp_df.sort_values(by='Price', ascending=True)

        PRICE_GRADIENT = [
            [0, "#1a9850"],   # Deep Green (Cheapest)
            [0.25, "#91cf60"], # Light Green
            [0.5, "#ffffbf"],  # Pale Yellow (Mid-range/Average)
            [0.75, "#fc8d59"], # Orange/Coral
            [1, "#d73027"]    # Deep Red (Most Expensive)
        ]

        # 5. Create the Plot
        fig = px.bar(
            recent_comp_df,
            x='Price',
            y='Market Name',
            orientation='h',
            color='Price',
            # 'RdYlGn_r' gives us Green (low) to Red (high)
            color_continuous_scale=PRICE_GRADIENT,
            text_auto='.2f', # Shows the price on the bar itself
            title=f"Prices as of {latest_date.strftime('%B %Y')}"
        )

        # 6. Formatting for the MSI Cyborg 15 display
        fig.update_layout(
            xaxis_title="Price (PHP)",
            yaxis_title="",
            # This ensures the cheapest (first in DF) is at the TOP
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False, # Hides the color bar for a cleaner look
            margin=dict(l=20, r=20, t=60, b=20),
            hovermode="y unified"
        )
        
        return fig

    # Market Deep Dive: H4 Region 
    @render.ui
    def dynamic_deep_dive():
        selected_region = input.region_filter()
        
        if not selected_region:
            return ui.h4("No region is selected.")
        if selected_region == "National":
            return ui.h4("Current price of commodities per Market in the Philippines")
        else:
            return ui.h4("Current price of commodities per Market in the " + selected_region)

    # Summary DF: The By Market info
    @render.data_frame
    def market_alps_table():
        current_df = filtered_data()
        selected_market = input.market_select()
        
        if current_df.empty or not selected_market:
            return pd.DataFrame()

        # Filter for market and latest date
        market_df = current_df[current_df['Market Name'] == selected_market]
        latest_date = market_df['Price Date'].max()
        final_df = market_df[market_df['Price Date'] == latest_date].copy()
        
        # Rounding and Formatting
        final_df['Price'] = final_df['Price'].round(2)
        final_df['Price_Fluctuation'] = final_df['Price_Fluctuation'].round(2)
        
        # Select and Rename columns
        result = final_df[['Commodity', 'Price', 'Price_Fluctuation', 'ALPS Phase']]
        result = result.rename(columns={'Price_Fluctuation': 'Change (₱)'})
        
        def color_phases(val):
            color = 'black'
            if "Crisis" in val: color = 'red'
            elif "Alert" in val: color = 'orange'
            elif "Stress" in val: color = '#d4af37' # Dark Gold/Yellow
            elif "Normal" in val: color = 'green'
            return f'color: {color}; font-weight: bold;'

        # Sort by biggest hikes by default
        return render.DataGrid(
            result.sort_values('Commodity', ascending=True),
            width="100%",    # Forces the table to touch the left and right edges of the card
            height="100%",   # Ensures it fills the vertical space if the card is tall 
            filters=True,
            summary=False)

    # Volatility Chart
    @render_widget
    def volatility_chart():
        current_df = filtered_data()
        recent_months = current_df['Price Date'].drop_duplicates().nlargest(12)
        df_recent = current_df[current_df['Price Date'].isin(recent_months)]
        
        cv_df = df_recent.groupby(['Price Date', 'Commodity_Type'])['Price'].agg(['std', 'mean']).reset_index()
        cv_df['CV'] = cv_df['std'] / cv_df['mean']
        cv_df['CV'] = cv_df['CV'].fillna(0)
        cv_df = cv_df.sort_values('Price Date')
        
        # Build the Plotly figure
        fig = px.line(
            cv_df,
            x='Price Date',
            y='CV',
            title='',
            color='Commodity_Type',
            labels={"Commodity_Type": "Commodity Type"},
            markers=True
        )
        
        # Clean up the layout to fit perfectly inside the ui.card
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20), # Removes unnecessary white space
            hovermode='x unified',
            legend=dict(
                orientation="h",     # Horizontal legend below the chart
                yanchor="bottom",
                y=-0.3,              # Push it below the x-axis
                xanchor="center",
                x=0.5
            )
        )
        
        return fig

    # z-score
    @render_widget
    def z_score_plot():
        selected_type = input.commodity_type_filter()

        if selected_type == "All":
            temp_df = df.copy()
        else:
            temp_df = df[df['Commodity_Type'] == selected_type].copy()
            
        if temp_df.empty:
            return px.bar(title="No data available for this selection.")


        plot_df = temp_df.groupby('Admin 1')['Z_Score'].mean().round(2).reset_index()
        plot_df = plot_df.sort_values('Admin 1', ascending=False)

        fig = px.bar(
            plot_df,
            x="Z_Score",
            y="Admin 1",
            orientation="h",
            color="Z_Score",
            color_continuous_scale="RdYlGn_r", 
            title=""
        )

        fig.update_layout(
            xaxis_title="Mean Z-Score (Relative to National Average)",
            yaxis_title="",
            margin=dict(l=10, r=20, t=40, b=10),
            coloraxis_showscale=False 
        )
        
        # Add a vertical reference line at 0 (the national average)
        fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="black")
        
        return fig

    # Historical Filter: By Region
    @reactive.calc
    def hist_filter_data():
        date_range = input.hist_dates()
        start_date = date_range[0]
        end_date = date_range[1]
        region = input.hist_region()
        comm = input.hist_commodity()
        dff = df.copy()

        dff['Price Date'] = pd.to_datetime(dff['Price Date']).dt.date
        
        if region != "National":
            dff = dff[dff['Admin 1'] == region]
            
        dff = dff[dff['Commodity'] == comm]
        
        # Apply the calendar range
        mask = (dff['Price Date'] >= start_date) & (dff['Price Date'] <= end_date)
        dff = dff.loc[mask]
        
        return dff.sort_values("Price Date")

    # Historical Data: Update Commodity Filter
    @reactive.effect
    def _update_hist_type():
        # 1. Get the current type selected
        selected_type = input.hist_type()
        
        if not selected_type:
            return
        
        filtered_df = df.copy()
        region = input.hist_region()
        if region != 'National':
            filtered_df = filtered_df[filtered_df['Admin 1'] == region]

        filtered_list = None
        if selected_type != 'All':
            filtered_list = filtered_df[filtered_df['Commodity_Type'] == selected_type]
        else:
            filtered_list = filtered_df

        available_commodities = sorted(filtered_list['Commodity'].unique().tolist())
        
        # 4. Update the UI element directly
        ui.update_select(
            "hist_commodity",
            choices=available_commodities,
            selected=available_commodities[0] if available_commodities else None
        )

    # Historical Price Change
    @render.ui
    def price_narrative_summary():
        df_base = hist_filter_data()
        
        if df_base.empty:
            return ui.p("No data available for the selected parameters.")

        df_base['Price Date'] = pd.to_datetime(df_base['Price Date'])
        start_date = df_base['Price Date'].min()
        end_date = df_base['Price Date'].max()

        # 3. Extract average prices for start and end points
        # We look for data in the specific months/years selected
        start_avg = df_base[df_base['Price Date'] == start_date]['Price'].mean()
        end_avg = df_base[df_base['Price Date'] == end_date]['Price'].mean()

        # Error handling if still no data
        if pd.isna(start_avg) or pd.isna(end_avg):
            return ui.p("Insufficient data to calculate a comparison.")

        # 4. Calculate the delta
        diff = end_avg - start_avg
        pct_change = (diff / start_avg) * 100
        direction = "increased" if diff >= 0 else "decreased"
        
        # 5. Format the strings
        start_label = start_date.strftime("%B, %Y")
        end_label = end_date.strftime("%B, %Y")

        return ui.div(
            ui.h4(f"On a National level, {input.hist_commodity()} cost...", style="margin-bottom: 5px; color: #333;") if input.hist_region() == 'National' 
                else ui.h4(f"In the {input.hist_region()}, {input.hist_commodity()} cost...", style="margin-bottom: 5px; color: #333;"),
            ui.p(
                ui.HTML(
                    f"<strong>₱{start_avg:,.2f}</strong> in {start_label} and "
                    f"<strong>₱{end_avg:,.2f}</strong> in {end_label}"
                ),
                style="margin-bottom: 5px; font-size: 1.1em;"
            ),
            ui.p(
                f"It has {direction} by {abs(pct_change):.1f}%, and you are now spending "
                f"{abs(diff):.2f} pesos {'more' if diff >= 0 else 'less'} per kilo.",
                style="color: #555;"
            )
        )

    # Historical Trend Chart
    @render.ui
    def hist_trend_chart_header():
        return ui.HTML(
            f'<h4>Price Trend for {str(input.hist_commodity())}</h4>'
        )

    # Historical Line Chart
    @render_widget
    def historical_trend_data():
        data = hist_filter_data()
        data = data.groupby('Price Date')['Price'].mean().round(2).reset_index()
        
        if data.empty:
            return px.line(title="No data available for the selected filters.")

        # 4. Create the Line Chart
        fig = px.line(
            data,
            x='Price Date',
            y='Price',
            title="",
            template="plotly_white",
            markers=True, # Adds dots to each data point for better visibility
            color_discrete_sequence=['#007bff'] # Professional blue
        )

        # 5. Fine-tuning for your MSI Cyborg 15 screen
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Average Price (PHP)",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20),
        )

        # 6. Formatting the Line and Grid
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )
        
        fig.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='#f0f0f0',
            # This ensures the date format is readable
            tickformat="%b %Y" 
        )
        
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

        return fig

    # Historical Min-Max Plot
    @render_widget
    def market_min_max_plot():
        # 1. Use your reactive historical filter
        df_base = hist_filter_data()
        
        if df_base.empty:
            return go.Figure().update_layout(title="No data available.")

        # 2. Aggregate Min and Max prices for each market
        market_stats = df_base.groupby('Market Name')['Price'].agg(['min', 'max']).reset_index()
        
        # 3. Sort by the maximum price to create a clean "ascending" visual
        market_stats = market_stats.sort_values('max', ascending=True)

        fig = go.Figure()

        # 4. Add the connecting "bars" (the lines between dots)
        for i, row in market_stats.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['min'], row['max']],
                y=[row['Market Name'], row['Market Name']],
                mode='lines',
                line=dict(color='#d3d3d3', width=4),
                showlegend=False,
                hoverinfo='none'
            ))

        # 5. Add the "Min" dots (The floor price)
        fig.add_trace(go.Scatter(
            x=market_stats['min'],
            y=market_stats['Market Name'],
            mode='markers',
            name='Min Price',
            marker=dict(color='#1a9850', size=10), # Forest Green
            hovertemplate='Min Price: ₱%{x:.2f}<extra></extra>'
        ))

        # 6. Add the "Max" dots (The ceiling price)
        fig.add_trace(go.Scatter(
            x=market_stats['max'],
            y=market_stats['Market Name'],
            mode='markers',
            name='Max Price',
            marker=dict(color='#d73027', size=10), # Crimson Red
            hovertemplate='Max Price: ₱%{x:.2f}<extra></extra>'
        ))

        # 7. Styling for your MSI Cyborg 15
        fig.update_layout(
            title=f"Price Range (Min vs Max) by Market for {input.hist_commodity()}",
            xaxis_title="Price (PHP)",
            yaxis_title="",
            template="plotly_white",
            height=max(400, len(market_stats) * 30), # Adjusts height based on number of markets
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig


app = App(app_ui, server)