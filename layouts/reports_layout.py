# layouts/reports_layout.py
"""
Reports Page Layout with Comprehensive Filter Container
Following themes.py structure with Agency, Cluster, Site, and Date filters
"""

from dash import html, dcc
from datetime import datetime, timedelta
from config.themes import THEMES, DEFAULT_THEME

def create_reports_layout(theme_name=None, user_data=None):
    """
    Create comprehensive reports page layout with filter container
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): User information
        
    Returns:
        html.Div: Complete reports layout
    """
    if theme_name is None:
        theme_name = DEFAULT_THEME
    
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    
    return html.Div(
        style={
            'minHeight': '100vh',
            'backgroundColor': theme['primary_bg'],
            'color': theme['text_primary'],
            'fontFamily': 'Inter, sans-serif'
        },
        children=[
            # Page Header
            create_reports_header(theme),
            
            # Filter Container
            create_filter_container(theme),
            
            # Content Area (placeholder for now)
            create_content_area(theme)
        ]
    )

def create_reports_header(theme):
    """Create reports page header section"""
    return html.Div(
        style={
            'background': f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            'padding': '2rem',
            'borderBottom': f"1px solid {theme['border_light']}",
            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.1)'
        },
        children=[
            html.Div(
                style={
                    'maxWidth': '1200px',
                    'margin': '0 auto',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center'
                },
                children=[
                    # Title Section
                    html.Div([
                        html.H1(
                            "📋 Reports Dashboard",
                            style={
                                'color': theme['text_primary'],
                                'fontSize': '2.5rem',
                                'fontWeight': '700',
                                'margin': '0',
                                'display': 'flex',
                                'alignItems': 'center',
                                'gap': '1rem'
                            }
                        ),
                        html.P(
                            "Generate and analyze comprehensive reports across all districts and sites",
                            style={
                                'color': theme['text_secondary'],
                                'fontSize': '1.1rem',
                                'margin': '0.5rem 0 0 0',
                                'lineHeight': '1.4'
                            }
                        )
                    ]),
                    
                    # Quick Actions
                    html.Div(
                        style={'display': 'flex', 'gap': '1rem'},
                        children=[
                            html.Button(
                                "📊 Generate Report",
                                id="generate-report-btn",
                                style={
                                    'background': theme['brand_primary'],
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '0.75rem 1.5rem',
                                    'borderRadius': '8px',
                                    'fontSize': '1rem',
                                    'fontWeight': '600',
                                    'cursor': 'pointer',
                                    'transition': 'all 0.2s ease',
                                    'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.2)'
                                }
                            ),
                            html.Button(
                                "📤 Export Data",
                                id="export-data-btn",
                                style={
                                    'background': 'transparent',
                                    'color': theme['text_primary'],
                                    'border': f"2px solid {theme['border_medium']}",
                                    'padding': '0.75rem 1.5rem',
                                    'borderRadius': '8px',
                                    'fontSize': '1rem',
                                    'fontWeight': '600',
                                    'cursor': 'pointer',
                                    'transition': 'all 0.2s ease'
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_filter_container(theme):
    """Create comprehensive filter container with all requested filters"""
    return html.Div(
        style={
            'maxWidth': '1200px',
            'margin': '2rem auto',
            'padding': '0 2rem'
        },
        children=[
            # Filter Container Header
            html.Div(
                style={
                    'marginBottom': '1.5rem'
                },
                children=[
                    html.H2(
                        "🔍 Filters",
                        style={
                            'color': theme['text_primary'],
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'margin': '0 0 0.5rem 0',
                            'display': 'flex',
                            'alignItems': 'center',
                            'gap': '0.5rem'
                        }
                    ),
                    html.P(
                        "Select criteria to filter and customize your reports",
                        style={
                            'color': theme['text_secondary'],
                            'fontSize': '0.9rem',
                            'margin': '0'
                        }
                    )
                ]
            ),
            
            # Filter Grid
            html.Div(
                style={
                    'background': theme['card_bg'],
                    'border': f"1px solid {theme['border_light']}",
                    'borderRadius': '12px',
                    'padding': '2rem',
                    'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.1)'
                },
                children=[
                    # Filter Row 1: Agency and Cluster
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': '1fr 1fr',
                            'gap': '2rem',
                            'marginBottom': '1.5rem'
                        },
                        children=[
                            # Agency Name Filter
                            create_filter_item(
                                label="Agency Name",
                                component_id="agency-filter",
                                filter_type="dropdown",
                                options=[
                                    {'label': 'All Agencies', 'value': 'all'},
                                    {'label': 'Swaccha Andhra Pradesh', 'value': 'swaccha_ap'},
                                    {'label': 'Municipal Corporation', 'value': 'municipal_corp'},
                                    {'label': 'District Collector Office', 'value': 'district_collector'},
                                    {'label': 'Panchayat Raj Department', 'value': 'panchayat_raj'},
                                    {'label': 'Environmental Protection', 'value': 'env_protection'}
                                ],
                                placeholder="Select Agency",
                                theme=theme
                            ),
                            
                            # Cluster Name Filter
                            create_filter_item(
                                label="Cluster Name",
                                component_id="cluster-filter",
                                filter_type="dropdown",
                                options=[
                                    {'label': 'All Clusters', 'value': 'all'},
                                    {'label': 'Coastal Cluster', 'value': 'coastal'},
                                    {'label': 'Central Cluster', 'value': 'central'},
                                    {'label': 'Northern Cluster', 'value': 'northern'},
                                    {'label': 'Southern Cluster', 'value': 'southern'},
                                    {'label': 'Eastern Cluster', 'value': 'eastern'},
                                    {'label': 'Western Cluster', 'value': 'western'}
                                ],
                                placeholder="Select Cluster",
                                theme=theme
                            )
                        ]
                    ),
                    
                    # Filter Row 2: Site and Date
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': '1fr 1fr',
                            'gap': '2rem',
                            'marginBottom': '1.5rem'
                        },
                        children=[
                            # Site Name Filter
                            create_filter_item(
                                label="Site Name",
                                component_id="site-filter",
                                filter_type="dropdown",
                                options=[
                                    {'label': 'All Sites', 'value': 'all'},
                                    {'label': 'Visakhapatnam Central', 'value': 'vsk_central'},
                                    {'label': 'Vijayawada Junction', 'value': 'vjw_junction'},
                                    {'label': 'Guntur Main', 'value': 'gnt_main'},
                                    {'label': 'Tirupati Temple', 'value': 'ttp_temple'},
                                    {'label': 'Kurnool District', 'value': 'knl_district'},
                                    {'label': 'Anantapur Rural', 'value': 'atp_rural'},
                                    {'label': 'Nellore Coastal', 'value': 'nlr_coastal'},
                                    {'label': 'Kadapa Mining', 'value': 'kdp_mining'},
                                    {'label': 'Chittoor Border', 'value': 'ctr_border'}
                                ],
                                placeholder="Select Site",
                                theme=theme
                            ),
                            
                            # Date Filter
                            create_date_filter(theme)
                        ]
                    ),
                    
                    # Filter Actions
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'alignItems': 'center',
                            'paddingTop': '1.5rem',
                            'borderTop': f"1px solid {theme['border_light']}"
                        },
                        children=[
                            # Filter Status
                            html.Div(
                                id="filter-status",
                                style={
                                    'color': theme['text_secondary'],
                                    'fontSize': '0.9rem'
                                },
                                children="No filters applied"
                            ),
                            
                            # Action Buttons
                            html.Div(
                                style={'display': 'flex', 'gap': '1rem'},
                                children=[
                                    html.Button(
                                        "🔄 Reset Filters",
                                        id="reset-filters-btn",
                                        style={
                                            'background': 'transparent',
                                            'color': theme['text_secondary'],
                                            'border': f"1px solid {theme['border_medium']}",
                                            'padding': '0.5rem 1rem',
                                            'borderRadius': '6px',
                                            'fontSize': '0.9rem',
                                            'cursor': 'pointer',
                                            'transition': 'all 0.2s ease'
                                        }
                                    ),
                                    html.Button(
                                        "✅ Apply Filters",
                                        id="apply-filters-btn",
                                        style={
                                            'background': theme['brand_primary'],
                                            'color': 'white',
                                            'border': 'none',
                                            'padding': '0.5rem 1.5rem',
                                            'borderRadius': '6px',
                                            'fontSize': '0.9rem',
                                            'fontWeight': '600',
                                            'cursor': 'pointer',
                                            'transition': 'all 0.2s ease',
                                            'boxShadow': '0 2px 6px rgba(0, 0, 0, 0.2)'
                                        }
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_filter_item(label, component_id, filter_type, options=None, placeholder="", theme=None):
    """Create individual filter item"""
    return html.Div(
        children=[
            html.Label(
                label,
                style={
                    'display': 'block',
                    'color': theme['text_primary'],
                    'fontSize': '0.9rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem'
                }
            ),
            dcc.Dropdown(
                id=component_id,
                options=options or [],
                placeholder=placeholder,
                style={
                    'fontSize': '0.9rem'
                },
                className="custom-dropdown"
            )
        ]
    )

def create_date_filter(theme):
    """Create date range filter component"""
    # Calculate default date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    return html.Div(
        children=[
            html.Label(
                "Date Range",
                style={
                    'display': 'block',
                    'color': theme['text_primary'],
                    'fontSize': '0.9rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem'
                }
            ),
            
            # Date range picker
            html.Div(
                style={
                    'display': 'grid',
                    'gridTemplateColumns': '1fr auto 1fr',
                    'gap': '0.5rem',
                    'alignItems': 'center'
                },
                children=[
                    dcc.DatePickerSingle(
                        id='start-date-picker',
                        date=start_date,
                        display_format='DD/MM/YYYY',
                        style={'width': '100%'}
                    ),
                    html.Span(
                        "to",
                        style={
                            'color': theme['text_secondary'],
                            'fontSize': '0.8rem',
                            'textAlign': 'center'
                        }
                    ),
                    dcc.DatePickerSingle(
                        id='end-date-picker',
                        date=end_date,
                        display_format='DD/MM/YYYY',
                        style={'width': '100%'}
                    )
                ]
            ),
            
            # Quick date range buttons
            html.Div(
                style={
                    'display': 'flex',
                    'gap': '0.5rem',
                    'marginTop': '0.75rem',
                    'flexWrap': 'wrap'
                },
                children=[
                    html.Button(
                        "Last 7 days",
                        id="date-7days-btn",
                        style=create_quick_date_btn_style(theme)
                    ),
                    html.Button(
                        "Last 30 days",
                        id="date-30days-btn",
                        style=create_quick_date_btn_style(theme)
                    ),
                    html.Button(
                        "Last 90 days",
                        id="date-90days-btn",
                        style=create_quick_date_btn_style(theme)
                    ),
                    html.Button(
                        "This Year",
                        id="date-year-btn",
                        style=create_quick_date_btn_style(theme)
                    )
                ]
            )
        ]
    )

def create_quick_date_btn_style(theme):
    """Create consistent style for quick date buttons"""
    return {
        'background': 'transparent',
        'color': theme['text_secondary'],
        'border': f"1px solid {theme['border_light']}",
        'padding': '0.25rem 0.75rem',
        'borderRadius': '4px',
        'fontSize': '0.8rem',
        'cursor': 'pointer',
        'transition': 'all 0.2s ease'
    }

def create_content_area(theme):
    """Create content area placeholder for reports"""
    return html.Div(
        style={
            'maxWidth': '1200px',
            'margin': '2rem auto',
            'padding': '0 2rem'
        },
        children=[
            html.Div(
                style={
                    'background': theme['card_bg'],
                    'border': f"1px solid {theme['border_light']}",
                    'borderRadius': '12px',
                    'padding': '3rem',
                    'textAlign': 'center',
                    'minHeight': '300px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'alignItems': 'center'
                },
                children=[
                    html.Div(
                        "📊",
                        style={
                            'fontSize': '4rem',
                            'marginBottom': '1rem',
                            'opacity': '0.5'
                        }
                    ),
                    html.H3(
                        "Reports will appear here",
                        style={
                            'color': theme['text_primary'],
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '0.5rem'
                        }
                    ),
                    html.P(
                        "Apply filters above and click 'Apply Filters' to generate reports based on your selected criteria.",
                        style={
                            'color': theme['text_secondary'],
                            'fontSize': '1rem',
                            'lineHeight': '1.5',
                            'maxWidth': '500px'
                        }
                    )
                ]
            )
        ]
    )

# CSS for custom dropdown styling
REPORTS_CSS = """
.custom-dropdown .Select-control {
    background-color: var(--card-bg);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    min-height: 40px;
}

.custom-dropdown .Select-placeholder {
    color: var(--text-secondary);
}

.custom-dropdown .Select-value-label {
    color: var(--text-primary);
}

.custom-dropdown .Select-menu-outer {
    background-color: var(--card-bg);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.custom-dropdown .Select-option {
    background-color: var(--card-bg);
    color: var(--text-primary);
    padding: 10px 12px;
}

.custom-dropdown .Select-option:hover {
    background-color: var(--accent-bg);
}

.custom-dropdown .Select-option.is-selected {
    background-color: var(--brand-primary);
    color: white;
}
"""