from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from plotnine import ggplot, aes, geom_point, theme_minimal
import pandas as pd

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

# For Summary Page: Filter 1
CHOICES = [ 
    "National", "Autonomous region in Muslim Mindanao", "Cordillera Administrative region", "National Capital region", 
    "Region I", "Region II", "Region III", "Region IV-A", "Region IV-B", "Region IX", "Region V", "Region VI", 
    "Region VII", "Region VIII", "Region X", "Region XI", "Region XII", "Region XIII"
]

# For Summary Page: Filter 2
COMMODITY_TYPES = ["All", "Grains & Staples", "Meat & Poultry", "Fish & Seafood", "Vegetables, Tubers & Legumes", "Fruits"]

def summary_page():
    """The instant-insight page"""

    tables_section = ui.navset_tab(
        # TAB 1: The Quick Look
        ui.nav_panel(
            "Quick View",
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
        ),

        ui.nav_panel(
            "Inter-Market Comparison",
            'Add Horizontal plot here'
        ),
        
        # TAB 2: The Deep Dive (Revealed when card is explored)
        ui.nav_panel(
            "Market Deep-Dive",
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
                bg="#f8f9fa"
            ),
            
            ui.div(
                'Z score per group (Price intensity per region for each commodity)',
                tables_section,
                ui.br(),
                ui.h4("Volatility of each Commodity Type"),
                ui.p("Coefficient of Variation measures relative volatility (Standard Deviation / Mean).", style="color: #666; font-size: 0.9em;"),
                output_widget("volatility_chart"),
            )
        ),
        full_screen=True
    )

    z_score_section = ui.card(
        ui.card_header("Regional Price Ranges (Z-Score Distribution)"),
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
    return ui.nav_panel(
        "Historical Data",

        'All of these are under one filter system',
            'Change in commodity price over time (Average)',
            'Dumbbell plot for market-market comparison (min-max analysis)',
            'Variability'
    )

def info_page():
    """The About/Context page."""
    return ui.nav_panel(
        "Info",
        ui.h3("About This Dashboard"),
        ui.markdown("""
        **Dataset:** WFP VAM Price Dataset
        
        **Data Dictionary:**
        * `Admin 1` / `Admin 2`: Regional and provincial boundaries.
        * `Commodity`: The specific food or non-food item.
        * `ALPS Phase`: Alert for Price Spikes indicator.
        * `Pewi`: Price Equivalent Wealth Index.
        
        *Data processing handled locally via Python and pandas.*
        """)
    )


app_ui = ui.page_fluid(
    # Header for the whole dashboard
    ui.h2("VAM Food Price Analysis", style="padding: 15px 0px; border-bottom: 1px solid #ccc;"),
    
    # The crucial function for left-sided navigation
    ui.navset_pill_list(
        summary_page(),
        historical_data_page(),
        info_page(),
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


        plot_df = temp_df.groupby('Admin 1')['Z_Score'].mean().reset_index()
        plot_df = plot_df.sort_values('Admin 1', ascending=False)

        fig = px.bar(
            plot_df,
            x="Z_Score",
            y="Admin 1",
            orientation="h",
            color="Z_Score",
            color_continuous_scale="RdYlGn_r", 
            title=f"Mean Price Deviation (Z-Score) by Region: {selected_type}"
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

app = App(app_ui, server)