# callbacks/public_landing_callbacks.py
"""
Callbacks for Enhanced Public Landing Page
Handles data refresh and dynamic updates
"""

from dash import callback, Input, Output, html, dcc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

from layouts.enhanced_public_landing import (
    load_dashboard_data,
    create_weekly_trips_histogram,
    create_daily_waste_line_chart,
    create_hourly_analysis_charts,
    create_cluster_performance_chart,
    create_summary_metrics
)
from utils.theme_utils import get_theme_styles

logger = logging.getLogger(__name__)

@callback(
    [Output('public-summary-metrics', 'children'),
     Output('public-weekly-histogram', 'children'),
     Output('public-daily-line-chart', 'children'),
     Output('public-hourly-analysis', 'children'),
     Output('public-cluster-performance', 'children')],
    [Input('public-data-refresh', 'n_intervals'),
     Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_public_dashboard_data(n_intervals, theme_name):
    """Update all dashboard visualizations with fresh data"""
    try:
        # Load fresh data
        dashboard_data = load_dashboard_data()
        
        # Get theme
        theme_styles = get_theme_styles(theme_name or 'dark')
        theme = theme_styles["theme"]
        
        # Create updated components
        summary_metrics = create_summary_metrics(dashboard_data, theme)
        weekly_histogram = create_weekly_trips_histogram(dashboard_data, theme)
        daily_line_chart = create_daily_waste_line_chart(dashboard_data, theme)
        hourly_analysis = create_hourly_analysis_charts(dashboard_data, theme)
        cluster_performance = create_cluster_performance_chart(dashboard_data, theme)
        
        logger.info(f"Public dashboard updated - Interval: {n_intervals}, Records: {len(dashboard_data)}")
        
        return (
            summary_metrics,
            weekly_histogram,
            daily_line_chart,
            hourly_analysis,
            cluster_performance
        )
        
    except Exception as e:
        logger.error(f"Error updating public dashboard: {e}")
        
        # Return error components
        error_style = {
            'textAlign': 'center',
            'color': '#ff6b6b',
            'padding': '2rem',
            'backgroundColor': 'rgba(255, 107, 107, 0.1)',
            'borderRadius': '8px',
            'border': '1px solid #ff6b6b'
        }
        
        error_component = html.Div(
            "⚠️ Error loading dashboard data",
            style=error_style
        )
        
        return (error_component, error_component, error_component, error_component, error_component)

@callback(
    Output('public-last-updated', 'children'),
    [Input('public-data-refresh', 'n_intervals')]
)
def update_last_updated_timestamp(n_intervals):
    """Update the last updated timestamp"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"Last updated: {current_time}"

# Optional: Callback to show loading state during data refresh
@callback(
    Output('public-loading-indicator', 'style'),
    [Input('public-data-refresh', 'n_intervals')],
    prevent_initial_call=True
)
def show_loading_indicator(n_intervals):
    """Show loading indicator briefly during refresh"""
    # This could trigger a brief loading animation
    # For now, we'll keep it hidden
    return {'display': 'none'}

# Export for import in main application
__all__ = [
    'update_public_dashboard_data',
    'update_last_updated_timestamp',
    'show_loading_indicator'
]