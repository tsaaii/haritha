# data_loader.py
"""
Real CSV Data Loader and Processor for Waste Management Dashboard
Integrates with your existing filter_container.py
"""

import pandas as pd
import logging
from dash import html, dash_table, dcc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def load_csv_data_from_browser():
    """
    Load CSV data using browser file API
    This function will be called from JavaScript to load your data
    """
    try:
        # This would be replaced with actual file loading
        # For now, creating sample data based on your CSV structure
        
        # Based on your actual CSV data structure from project knowledge
        data = [
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 11540, "vehicle": "AP39VB2709", "time": "03:37:22 PM", "waste_type": "MSW", "trip_no": 34},
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 17350, "vehicle": "AP39UN2025", "time": "03:20:54 PM", "waste_type": "MSW", "trip_no": 33},
            {"Date": "2025-05-23", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 12610, "vehicle": "AP39VB2709", "time": "03:10:13 PM", "waste_type": "MSW", "trip_no": 32},
            {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
             "weight": 23390, "vehicle": "AP04UB0825", "time": "07:42:41 PM", "waste_type": "MSW", "trip_no": 229},
            {"Date": "2025-06-05", "agency": "donthalli", "site": "donthalli", "cluster": "NMC", 
             "weight": 19570, "vehicle": "AP39VB4518", "time": "07:33:40 PM", "waste_type": "MSW", "trip_no": 228},
            {"Date": "2025-06-04", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 7940, "vehicle": "AP39UM8487", "time": "04:27:11 PM", "waste_type": "MSW", "trip_no": 200},
            {"Date": "2025-06-04", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 10140, "vehicle": "AP39VB2709", "time": "03:04:41 PM", "waste_type": "MSW", "trip_no": 199},
            {"Date": "2025-06-04", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 9070, "vehicle": "AP39UM8487", "time": "02:59:19 PM", "waste_type": "MSW", "trip_no": 198},
            {"Date": "2025-06-03", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 15540, "vehicle": "AP39VB2709", "time": "12:04:06 PM", "waste_type": "MSW", "trip_no": 184},
            {"Date": "2025-06-03", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 14150, "vehicle": "AP39VB2709", "time": "11:27:53 AM", "waste_type": "MSW", "trip_no": 183},
            {"Date": "2025-05-31", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 12710, "vehicle": "AP39VB2709", "time": "06:54:06 PM", "waste_type": "MSW", "trip_no": 180},
            {"Date": "2025-05-31", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 11460, "vehicle": "AP39VB2709", "time": "06:26:58 PM", "waste_type": "MSW", "trip_no": 179},
            {"Date": "2025-05-24", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 16610, "vehicle": "AP39VB2709", "time": "03:38:18 PM", "waste_type": "MSW", "trip_no": 52},
            {"Date": "2025-05-24", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 24130, "vehicle": "AP39UN2025", "time": "02:55:04 PM", "waste_type": "MSW", "trip_no": 50},
            {"Date": "2025-05-22", "agency": "madanapalle", "site": "madanapalle", "cluster": "MM", 
             "weight": 14460, "vehicle": "AP39VB2709", "time": "07:05:44 PM", "waste_type": "MSW", "trip_no": 21},
        ]
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Add calculated fields
        df['day_of_week'] = df['Date'].dt.day_name()
        df['month'] = df['Date'].dt.strftime('%Y-%m')
        df['weight_tons'] = df['weight'] / 1000
        
        logger.info(f"Loaded {len(df)} records from waste management data")
        return df
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        return pd.DataFrame()

def get_dynamic_filter_options(df):
    """
    Get filter options from actual data to replace static options in filter_container.py
    """
    if df.empty:
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}],
            'sites': [{'label': 'All Sites', 'value': 'all'}],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}]
        }
    
    try:
        # Extract unique values from your actual data
        agencies = sorted(df['agency'].unique())
        sites = sorted(df['site'].unique()) 
        clusters = sorted(df['cluster'].unique())
        
        options = {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}] + 
                       [{'label': agency.title(), 'value': agency} for agency in agencies],
            
            'sites': [{'label': 'All Sites', 'value': 'all'}] + 
                    [{'label': site.title(), 'value': site} for site in sites],
            
            'clusters': [{'label': 'All Clusters', 'value': 'all'}] + 
                       [{'label': cluster, 'value': cluster} for cluster in clusters]
        }
        
        logger.info(f"Generated filter options: {len(agencies)} agencies, {len(sites)} sites, {len(clusters)} clusters")
        return options
        
    except Exception as e:
        logger.error(f"Error generating filter options: {e}")
        return {
            'agencies': [{'label': 'All Agencies', 'value': 'all'}],
            'sites': [{'label': 'All Sites', 'value': 'all'}],
            'clusters': [{'label': 'All Clusters', 'value': 'all'}]
        }

def apply_filters_to_data(df, agency='all', cluster='all', site='all', start_date=None, end_date=None):
    """
    Apply filters to dataframe based on your filter container inputs
    """
    if df.empty:
        return df
    
    try:
        filtered_df = df.copy()
        
        # Agency filter
        if agency and agency != 'all':
            filtered_df = filtered_df[filtered_df['agency'] == agency]
            logger.info(f"Filtered by agency '{agency}': {len(filtered_df)} records remaining")
        
        # Cluster filter  
        if cluster and cluster != 'all':
            filtered_df = filtered_df[filtered_df['cluster'] == cluster]
            logger.info(f"Filtered by cluster '{cluster}': {len(filtered_df)} records remaining")
        
        # Site filter
        if site and site != 'all':
            filtered_df = filtered_df[filtered_df['site'] == site]
            logger.info(f"Filtered by site '{site}': {len(filtered_df)} records remaining")
        
        # Date range filter
        if start_date:
            start_dt = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['Date'] >= start_dt]
            logger.info(f"Filtered by start date '{start_date}': {len(filtered_df)} records remaining")
        
        if end_date:
            end_dt = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['Date'] <= end_dt]
            logger.info(f"Filtered by end date '{end_date}': {len(filtered_df)} records remaining")
        
        logger.info(f"Final filtered result: {len(df)} -> {len(filtered_df)} records")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error applying filters: {e}")
        return df

def create_filtered_data_display(filtered_df, theme, filters_applied):
    """
    Create the main data display that shows in 'filtered-data-display' div
    This is what users see after clicking 'Apply Filters' button
    """
    try:
        if filtered_df.empty:
            return html.Div([
                html.Div([
                    html.H3("📭 No Data Found", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "marginBottom": "1rem"
                    }),
                    html.P("No records match your current filter criteria.", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "marginBottom": "1rem"
                    }),
                    html.P("Try adjusting your filters or resetting them to see all data.", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "fontSize": "0.9rem"
                    })
                ], style={
                    "padding": "3rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "12px",
                    "border": f"2px dashed {theme['accent_bg']}"
                })
            ])
        
        # Calculate summary statistics
        total_records = len(filtered_df)
        total_weight = filtered_df['weight'].sum()
        avg_weight = filtered_df['weight'].mean()
        unique_agencies = filtered_df['agency'].nunique()
        unique_sites = filtered_df['site'].nunique()
        unique_clusters = filtered_df['cluster'].nunique()
        date_range = f"{filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}"
        
        return html.Div([
            # Header with filter summary
            html.Div([
                html.H2("🔍 Filtered Waste Management Data", style={
                    "color": theme["text_primary"],
                    "fontSize": "2rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }),
                html.Div([
                    html.Strong("Applied Filters: ", style={"color": theme["text_primary"]}),
                    html.Span(" | ".join([f"{k}: {v}" for k, v in filters_applied.items() if v != 'all']), 
                             style={"color": theme["text_secondary"]})
                ], style={"textAlign": "center", "marginBottom": "1.5rem"})
            ], style={
                "padding": "1.5rem",
                "backgroundColor": theme["accent_bg"],
                "borderRadius": "12px",
                "marginBottom": "2rem",
                "border": f"1px solid {theme.get('border_light', theme['card_bg'])}"
            }),
            
            # Summary Statistics Cards
            html.Div([
                html.H3("📊 Summary Statistics", style={
                    "color": theme["text_primary"],
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }),
                html.Div([
                    create_summary_card("Total Records", f"{total_records:,}", "📝", theme),
                    create_summary_card("Total Weight", f"{total_weight:,.0f} kg", "⚖️", theme),
                    create_summary_card("Average Weight", f"{avg_weight:.0f} kg", "📊", theme),
                    create_summary_card("Agencies", str(unique_agencies), "🏢", theme),
                    create_summary_card("Sites", str(unique_sites), "📍", theme),
                    create_summary_card("Clusters", str(unique_clusters), "🏘️", theme),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "1rem",
                    "marginBottom": "2rem"
                })
            ]),
            
            # Data Visualizations
            html.Div([
                html.H3("📈 Data Visualizations", style={
                    "color": theme["text_primary"],
                    "marginBottom": "1rem"
                }),
                create_data_charts(filtered_df, theme)
            ], style={"marginBottom": "2rem"}),
            
            # Data Table
            html.Div([
                html.H3("📋 Detailed Records", style={
                    "color": theme["text_primary"],
                    "marginBottom": "1rem"
                }),
                create_data_table(filtered_df, theme)
            ]),
            
            # Footer with metadata
            html.Div([
                html.Hr(style={"margin": "2rem 0", "border": f"1px solid {theme['accent_bg']}"}),
                html.Div([
                    html.P(f"📅 Date Range: {date_range}", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "margin": "0.5rem 0",
                        "fontSize": "0.9rem"
                    }),
                    html.P(f"🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style={
                        "color": theme["text_secondary"],
                        "textAlign": "center",
                        "margin": "0.5rem 0",
                        "fontSize": "0.9rem"
                    })
                ])
            ])
        ])
        
    except Exception as e:
        logger.error(f"Error creating filtered data display: {e}")
        return html.Div([
            html.Div(f"❌ Error displaying filtered data: {str(e)}", style={
                "color": theme.get("error", "#E53E3E"),
                "textAlign": "center",
                "padding": "2rem",
                "backgroundColor": theme["card_bg"],
                "borderRadius": "8px",
                "border": f"2px solid {theme.get('error', '#E53E3E')}"
            })
        ])

def create_summary_card(title, value, icon, theme):
    """Create individual summary statistic cards"""
    return html.Div([
        html.Div([
            html.Span(icon, style={
                "fontSize": "2rem",
                "marginBottom": "0.5rem",
                "display": "block"
            }),
            html.H4(title, style={
                "color": theme["text_secondary"],
                "fontSize": "0.85rem",
                "fontWeight": "600",
                "margin": "0",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px"
            }),
            html.Div(value, style={
                "color": theme["text_primary"],
                "fontSize": "1.8rem",
                "fontWeight": "700",
                "margin": "0.5rem 0 0 0",
                "lineHeight": "1"
            })
        ])
    ], style={
        "backgroundColor": theme["card_bg"],
        "padding": "1.5rem",
        "borderRadius": "12px",
        "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
        "textAlign": "center",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
        "transition": "transform 0.2s ease",
        "cursor": "default"
    })

def create_data_table(filtered_df, theme, max_rows=50):
    """Create interactive data table"""
    try:
        if filtered_df.empty:
            return html.Div("No data to display", style={"textAlign": "center", "padding": "2rem"})
        
        # Prepare data for table display
        display_df = filtered_df.head(max_rows).copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Weight (kg)'] = display_df['weight'].apply(lambda x: f"{x:,}")
        
        # Select columns for display
        columns_to_show = ['Date', 'agency', 'site', 'cluster', 'Weight (kg)', 'vehicle', 'time', 'waste_type']
        table_df = display_df[['Date', 'agency', 'site', 'cluster', 'Weight (kg)', 'vehicle', 'time', 'waste_type']]
        
        return html.Div([
            html.P(f"Showing first {min(len(filtered_df), max_rows)} of {len(filtered_df):,} records", 
                  style={"color": theme["text_secondary"], "fontSize": "0.9rem", "marginBottom": "1rem"}),
            
            dash_table.DataTable(
                data=table_df.to_dict('records'),
                columns=[
                    {"name": "Date", "id": "Date"},
                    {"name": "Agency", "id": "agency"},
                    {"name": "Site", "id": "site"},
                    {"name": "Cluster", "id": "cluster"},
                    {"name": "Weight (kg)", "id": "Weight (kg)"},
                    {"name": "Vehicle", "id": "vehicle"},
                    {"name": "Time", "id": "time"},
                    {"name": "Type", "id": "waste_type"}
                ],
                style_table={
                    'overflowX': 'auto',
                    'backgroundColor': theme["card_bg"]
                },
                style_cell={
                    'backgroundColor': theme["card_bg"],
                    'color': theme["text_primary"],
                    'border': f'1px solid {theme.get("border_light", theme["accent_bg"])}',
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '0.9rem'
                },
                style_header={
                    'backgroundColor': theme["accent_bg"],
                    'color': theme["text_primary"],
                    'fontWeight': 'bold',
                    'border': f'1px solid {theme.get("border_light", theme["accent_bg"])}',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': theme.get("table_stripe", theme["accent_bg"])
                    }
                ],
                page_size=20,
                sort_action="native",
                filter_action="native",
                export_format="csv"
            )
        ])
        
    except Exception as e:
        logger.error(f"Error creating data table: {e}")
        return html.Div(f"Error creating table: {str(e)}")

def create_data_charts(filtered_df, theme):
    """Create visualization charts"""
    try:
        if filtered_df.empty:
            return html.Div("No data available for charts", style={"textAlign": "center", "padding": "2rem"})
        
        charts = []
        
        # Chart 1: Weight by Agency
        if len(filtered_df['agency'].unique()) > 1:
            agency_weights = filtered_df.groupby('agency')['weight'].sum().reset_index()
            
            fig1 = px.bar(
                agency_weights, 
                x='agency', 
                y='weight',
                title='Total Weight by Agency (kg)',
                color='weight',
                color_continuous_scale='Viridis'
            )
            fig1.update_layout(
                plot_bgcolor=theme["card_bg"],
                paper_bgcolor=theme["card_bg"],
                font_color=theme["text_primary"],
                title_font_color=theme["text_primary"],
                height=400
            )
            
            charts.append(dcc.Graph(figure=fig1, style={"marginBottom": "1rem"}))
        
        # Chart 2: Daily Collection Trends
        if len(filtered_df['Date'].unique()) > 1:
            daily_data = filtered_df.groupby('Date').agg({
                'weight': 'sum',
                'agency': 'count'
            }).reset_index()
            daily_data.rename(columns={'agency': 'collections'}, inplace=True)
            
            fig2 = px.line(
                daily_data, 
                x='Date', 
                y='weight',
                title='Daily Weight Collection Trends (kg)',
                markers=True
            )
            fig2.update_layout(
                plot_bgcolor=theme["card_bg"],
                paper_bgcolor=theme["card_bg"],
                font_color=theme["text_primary"],
                title_font_color=theme["text_primary"],
                height=400
            )
            
            charts.append(dcc.Graph(figure=fig2))
        
        if not charts:
            return html.Div("Insufficient data for visualizations", style={
                "textAlign": "center", 
                "padding": "2rem",
                "color": theme["text_secondary"]
            })
        
        return html.Div(charts, style={
            "display": "grid",
            "gridTemplateColumns": "1fr",
            "gap": "1rem"
        })
        
    except Exception as e:
        logger.error(f"Error creating charts: {e}")
        return html.Div(f"Error creating charts: {str(e)}")

# Global data storage
_cached_data = None

def get_cached_data():
    """Get cached data or load fresh"""
    global _cached_data
    if _cached_data is None:
        _cached_data = load_csv_data_from_browser()
    return _cached_data

def refresh_cached_data():
    """Force refresh of cached data"""
    global _cached_data
    _cached_data = load_csv_data_from_browser()
    return _cached_data