# components/filters/filter_container.py
"""
Responsive Filter Container Component for Swaccha Andhra Dashboard
Optimized for desktop and mobile with theme support
"""

from dash import html, dcc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_filter_container(theme, container_id="main-filter-container"):
    """
    Create a responsive filter container with Agency, Cluster, Site, and Date filters
    
    Args:
        theme (dict): Current theme configuration
        container_id (str): Unique container ID
        
    Returns:
        html.Div: Complete filter container component
    """
    
    # Sample options - you'll replace these with real data later
    agency_options = [
        {'label': 'All Agencies', 'value': 'all'},
        {'label': 'Zigma', 'value': 'zigma'},
        {'label': 'Green Clean', 'value': 'green_clean'},
        {'label': 'EcoServe', 'value': 'ecoserve'},
        {'label': 'Urban Waste Solutions', 'value': 'urban_waste'}
    ]
    
    cluster_options = [
        {'label': 'All Clusters', 'value': 'all'},
        {'label': 'Nellore Municipal Corporation', 'value': 'nellore'},
        {'label': 'Chittor', 'value': 'chittor'},
        {'label': 'Tirupathi', 'value': 'tirupathi'},
        {'label': 'GVMC', 'value': 'gvmc'},
        {'label': 'Kurnool', 'value': 'kurnool'},
        {'label': 'Vijayawada', 'value': 'vijayawada'}
    ]
    
    site_options = [
        {'label': 'All Sites', 'value': 'all'},
        {'label': 'Allipuram', 'value': 'allipuram'},
        {'label': 'Donthalli', 'value': 'donthalli'},
        {'label': 'Kuppam', 'value': 'kuppam'},
        {'label': 'Palamaner', 'value': 'palamaner'},
        {'label': 'Madanapalle', 'value': 'madanapalle'},
        {'label': 'TPTY', 'value': 'tpty'},
        {'label': 'Vizagsac', 'value': 'vizagsac'}
    ]
    
    # Base styles for filter components
    filter_input_style = {
        "width": "100%",
        "padding": "0.75rem",
        "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
        "borderRadius": "8px",
        "backgroundColor": theme["card_bg"],
        "color": theme["text_primary"],
        "fontSize": "0.9rem",
        "fontWeight": "500",
        "outline": "none",
        "transition": "all 0.2s ease",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
    }
    
    filter_label_style = {
        "color": theme["text_primary"],
        "fontSize": "0.9rem",
        "fontWeight": "600",
        "marginBottom": "0.5rem",
        "display": "block"
    }
    
    # Create the main filter container
    return html.Div(
        id=container_id,
        className="filter-container-wrapper",
        style={
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
            "borderRadius": "12px",
            "padding": "1.5rem",
            "marginBottom": "2rem",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)"
        },
        children=[
            # Filter Container Header
            html.Div(
                className="filter-header",
                style={
                    "marginBottom": "1.5rem",
                    "textAlign": "center",
                    "borderBottom": f"2px solid {theme['accent_bg']}",
                    "paddingBottom": "1rem"
                },
            ),
            
            # Responsive Filter Grid
            html.Div(
                className="filter-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "1.5rem",
                    "marginBottom": "1.5rem"
                },
                children=[
                    # Agency Filter
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "🏢 Agency",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-agency-filter",
                                options=agency_options,
                                value='all',
                                placeholder="Select Agency...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Cluster Filter
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "🗺️ Cluster",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-cluster-filter",
                                options=cluster_options,
                                value='all',
                                placeholder="Select Cluster...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Site Filter
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "📍 Site",
                                style=filter_label_style
                            ),
                            dcc.Dropdown(
                                id=f"{container_id}-site-filter",
                                options=site_options,
                                value='all',
                                placeholder="Select Site...",
                                clearable=False,
                                style={
                                    "fontSize": "0.9rem"
                                },
                                className="custom-dropdown"
                            )
                        ]
                    ),
                    
                    # Date Range Filter
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label(
                                "📅 Date Range",
                                style=filter_label_style
                            ),
                            dcc.DatePickerRange(
                                id=f"{container_id}-date-filter",
                                start_date=datetime.now() - timedelta(days=7),
                                end_date=datetime.now(),
                                display_format='DD/MM/YYYY',
                                style={
                                    "width": "100%",
                                    "fontSize": "0.9rem"
                                },
                                className="custom-date-picker"
                            )
                        ]
                    )
                ]
            ),
            
            # Filter Action Buttons
            html.Div(
                className="filter-actions",
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "1rem",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "borderTop": f"1px solid {theme['accent_bg']}",
                    "paddingTop": "1.5rem"
                },
                children=[
                    # Apply Filters Button
                    html.Button(
                        [
                            html.Span("🔍", style={"marginRight": "0.5rem"}),
                            "Apply Filters"
                        ],
                        id=f"{container_id}-apply-btn",
                        className="filter-btn primary",
                        style={
                            "backgroundColor": theme["brand_primary"],
                            "color": "white",
                            "border": "none",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.2)",
                            "minWidth": "140px",
                            "justifyContent": "center"
                        }
                    ),
                    
                    # Reset Filters Button
                    html.Button(
                        [
                            html.Span("🔄", style={"marginRight": "0.5rem"}),
                            "Reset"
                        ],
                        id=f"{container_id}-reset-btn",
                        className="filter-btn secondary",
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "border": f"2px solid {theme.get('border_light', theme['accent_bg'])}",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "minWidth": "120px",
                            "justifyContent": "center"
                        }
                    ),
                    
                    # Export Data Button
                    html.Button(
                        [
                            html.Span("📊", style={"marginRight": "0.5rem"}),
                            "Export"
                        ],
                        id=f"{container_id}-export-btn",
                        className="filter-btn export",
                        style={
                            "backgroundColor": theme.get("success_color", "#38A169"),
                            "color": "white",
                            "border": "none",
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "minWidth": "120px",
                            "justifyContent": "center"
                        }
                    )
                ]
            ),
            
            # Filter Status Indicator
            html.Div(
                id=f"{container_id}-status",
                className="filter-status",
                style={
                    "marginTop": "1rem",
                    "padding": "0.75rem",
                    "backgroundColor": theme["accent_bg"],
                    "borderRadius": "8px",
                    "textAlign": "center",
                    "fontSize": "0.85rem",
                    "color": theme["text_secondary"],
                    "display": "none"  # Hidden by default, shown by callbacks
                },
                children=[
                    html.Span(id=f"{container_id}-status-text", children="Ready to filter data")
                ]
            )
        ]
    )


def create_filter_container_styles():
    """
    Generate CSS styles for the filter container components
    
    Returns:
        str: CSS styles for responsive design
    """
    return """
    /* Filter Container Responsive Styles */
    .filter-container-wrapper {
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .filter-grid {
        width: 100%;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .filter-container-wrapper {
            padding: 1rem !important;
            margin: 1rem 0 !important;
        }
        
        .filter-grid {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
        }
        
        .filter-actions {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        
        .filter-btn {
            width: 100% !important;
            min-width: unset !important;
        }
        
        .filter-header h3 {
            font-size: 1.25rem !important;
        }
    }
    
    /* Tablet Optimizations */
    @media (min-width: 769px) and (max-width: 1024px) {
        .filter-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    
    /* Dropdown Customization */
    .custom-dropdown .Select-control {
        border-radius: 8px !important;
        border-width: 2px !important;
        min-height: 44px !important;
    }
    
    .custom-dropdown .Select-menu-outer {
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Date Picker Customization */
    .custom-date-picker .DateInput {
        border-radius: 8px !important;
        border-width: 2px !important;
    }
    
    .custom-date-picker .DateRangePickerInput {
        border-radius: 8px !important;
    }
    
    /* Button Hover Effects */
    .filter-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    .filter-btn:active {
        transform: translateY(0) !important;
    }
    
    /* Focus States */
    .custom-dropdown .Select-control:focus,
    .custom-date-picker .DateInput_input:focus {
        outline: 2px solid #3182CE !important;
        outline-offset: 2px !important;
    }
    """


def get_filter_callback_template():
    """
    Template for filter callbacks - you can use this as a starting point
    
    Returns:
        str: Python code template for implementing filter callbacks
    """
    return '''
from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate

@callback(
    [Output('filtered-data-display', 'children'),
     Output('main-filter-container-status', 'style'),
     Output('main-filter-container-status-text', 'children')],
    [Input('main-filter-container-apply-btn', 'n_clicks')],
    [State('main-filter-container-agency-filter', 'value'),
     State('main-filter-container-cluster-filter', 'value'),
     State('main-filter-container-site-filter', 'value'),
     State('main-filter-container-date-filter', 'start_date'),
     State('main-filter-container-date-filter', 'end_date')],
    prevent_initial_call=True
)
def apply_filters(n_clicks, agency, cluster, site, start_date, end_date):
    """Apply filters and update data display"""
    if not n_clicks:
        raise PreventUpdate
    
    # Your filtering logic here
    filtered_data = filter_data(agency, cluster, site, start_date, end_date)
    
    # Update status
    status_style = {"display": "block"}
    status_text = f"Filtered {len(filtered_data)} records"
    
    # Return filtered display, status visibility, and status text
    return create_filtered_display(filtered_data), status_style, status_text

@callback(
    [Output('main-filter-container-agency-filter', 'value'),
     Output('main-filter-container-cluster-filter', 'value'),
     Output('main-filter-container-site-filter', 'value'),
     Output('main-filter-container-date-filter', 'start_date'),
     Output('main-filter-container-date-filter', 'end_date')],
    [Input('main-filter-container-reset-btn', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Reset all filters to default values"""
    if not n_clicks:
        raise PreventUpdate
    
    return 'all', 'all', 'all', default_start_date, default_end_date
'''


# Export functions
__all__ = [
    'create_filter_container',
    'create_filter_container_styles', 
    'get_filter_callback_template'
]