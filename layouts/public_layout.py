# layouts/public_layout.py
"""
Enhanced Auto-Rotating Public Landing Page Layout for Swaccha Andhra Corporation
Complete implementation with all requested enhancements
"""

from dash import html, dcc, callback, Input, Output, clientside_callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import os
import numpy as np

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

logger = logging.getLogger(__name__)

def load_csv_visualization_data():
    """Load data from csv_outputs_data_viz.csv"""
    try:
        csv_path = 'data/csv_outputs_data_viz.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            logger.info(f"✅ Loaded {len(df)} records from CSV visualization data")
            
            # Convert date column to datetime if needed
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            return df
        else:
            logger.warning(f"CSV file not found at {csv_path}")
            return create_sample_data()
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data matching CSV structure for testing"""
    agencies = ['Swaccha Andhra Corporation', 'Municipal Corp', 'Zigma Agency', 'Green Solutions']
    clusters = ['Nellore Municipal Corporation', 'Chittor', 'Tirupathi', 'GVMC', 'Kurnool']
    sites = ['Site A', 'Site B', 'Site C', 'Site D', 'Site E', 'Site F']
    
    data = []
    base_date = datetime.now() - timedelta(days=2)
    
    for i in range(100):
        # Create multiple tickets per day with different hours
        ticket_date = base_date + timedelta(days=i//20, hours=i%24)
        data.append({
            'Agency': np.random.choice(agencies),
            'Sub_contractor': f'Contractor {i%3 + 1}',
            'Cluster': np.random.choice(clusters),
            'Site': np.random.choice(sites),
            'Machines': f'Machine Type {i%4 + 1}',
            'Total_capacity_per_day': np.random.randint(100, 500),
            'Total_waste_to_be_remediated': f'{np.random.randint(500, 2000)} tons',
            'date': ticket_date.strftime('%Y-%m-%d %H:%M:%S'),
            'ticket_no': f'TKT{i:03d}',
            'net_weight_calculated': np.random.randint(50, 300)
        })
    
    return pd.DataFrame(data)

def format_indian_number(number):
    """Format number in Indian numbering system (xx,xx,xxx)"""
    if number == 0:
        return "0"
    
    # Convert to string and reverse for easier processing
    num_str = str(int(number))
    if len(num_str) <= 3:
        return num_str
    
    # Indian numbering: last 3 digits, then groups of 2
    result = num_str[-3:]  # Last 3 digits
    remaining = num_str[:-3]
    
    # Add groups of 2 digits from right to left
    while remaining:
        if len(remaining) >= 2:
            result = remaining[-2:] + ',' + result
            remaining = remaining[:-2]
        else:
            result = remaining + ',' + result
            remaining = ''
    
    return result

def get_last_available_date(df):
    """Get the last available date from the dataset"""
    if df.empty or 'date' not in df.columns:
        return datetime.now().date()
    
    try:
        # Convert to datetime if string
        if str(df['date'].dtype) == 'object':
            date_series = pd.to_datetime(df['date'], errors='coerce')
        else:
            date_series = df['date']
        
        # Get the most recent date, excluding NaT values
        valid_dates = date_series.dropna()
        if valid_dates.empty:
            return datetime.now().date()
        
        last_date = valid_dates.max()
        if pd.isna(last_date):
            return datetime.now().date()
        
        return last_date.date()
        
    except Exception as e:
        logger.error(f"Error getting last available date: {e}")
        return datetime.now().date()

def get_rotation_data(df, rotation_index=0):
    """Get data for current rotation view"""
    if df.empty:
        return {
            'agencies': [],
            'clusters': [], 
            'sites': [],
            'current_focus': 'No Data',
            'current_agency': '',
            'current_cluster': '',
            'current_site': ''
        }
    
    try:
        # Get all unique values safely
        agencies = []
        if 'Agency' in df.columns:
            agencies = df['Agency'].dropna().unique().tolist()
        
        clusters = []
        if 'Cluster' in df.columns:
            clusters = df['Cluster'].dropna().unique().tolist()
        
        sites = []
        if 'Site' in df.columns:
            sites = df['Site'].dropna().unique().tolist()
        
        # For now, let's cycle through sites (since we want site-specific data)
        # Each site will show its agency and cluster info
        total_sites = len(sites)
        if total_sites == 0:
            return {
                'agencies': agencies, 
                'clusters': clusters, 
                'sites': sites, 
                'current_focus': 'No Sites Available',
                'current_agency': '',
                'current_cluster': '',
                'current_site': ''
            }
        
        # Get current site
        current_site_index = rotation_index % total_sites
        current_site = sites[current_site_index]
        
        # Find agency and cluster for this site safely
        current_agency = ''
        current_cluster = ''
        
        if len(df) > 0:
            site_data_mask = df['Site'] == current_site if 'Site' in df.columns else pd.Series([True] * len(df))
            site_data_df = df[site_data_mask]
            
            if len(site_data_df) > 0:
                if 'Agency' in site_data_df.columns:
                    agency_values = site_data_df['Agency'].dropna()
                    current_agency = agency_values.iloc[0] if len(agency_values) > 0 else ''
                
                if 'Cluster' in site_data_df.columns:
                    cluster_values = site_data_df['Cluster'].dropna()
                    current_cluster = cluster_values.iloc[0] if len(cluster_values) > 0 else ''
        
        return {
            'current_type': 'site',
            'current_site': current_site,
            'current_agency': current_agency,
            'current_cluster': current_cluster,
            'agencies': agencies,
            'clusters': clusters,
            'sites': sites,
            'current_focus': f"Site: {current_site}"
        }
        
    except Exception as e:
        logger.error(f"Error getting rotation data: {e}")
        return {
            'agencies': [],
            'clusters': [], 
            'sites': [],
            'current_focus': 'Error Loading',
            'current_agency': '',
            'current_cluster': '',
            'current_site': ''
        }

def calculate_site_metrics(df, site_name, last_date):
    """Calculate metrics for specific site on last available date"""
    if df.empty:
        return {
            'total_waste': 0,
            'total_trips': 0,
            'trips_by_hour': {},
            'daily_capacity': 0,
            'debug_info': 'No data available'
        }

    try:
        # Filter data for specific site and date
        if 'Site' in df.columns and len(df) > 0:
            site_mask = df['Site'] == site_name
            site_df = df[site_mask].copy()
        else:
            site_df = df.copy()
        
        debug_info = f"Site: {site_name}, Records found: {len(site_df)}"
        
        # Check if we have any data for this site
        if site_df.empty:
            return {
                'total_waste': 0,
                'total_trips': 0,
                'trips_by_hour': {},
                'daily_capacity': 0,
                'debug_info': f'{debug_info}, No site data found'
            }
        
        if 'date' in site_df.columns and len(site_df) > 0:
            # Convert date to datetime if needed
            if str(site_df['date'].dtype) == 'object':
                site_df['date'] = pd.to_datetime(site_df['date'], errors='coerce')
            
            # Filter for last available date
            if not site_df['date'].isna().all():
                site_df['date_only'] = site_df['date'].dt.date
                date_mask = site_df['date_only'] == last_date
                site_df = site_df[date_mask]
                debug_info += f", After date filter: {len(site_df)}"

        # Calculate total waste with debugging
        total_waste = 0
        if 'net_weight_calculated' in site_df.columns and len(site_df) > 0:
            # Convert to numeric, replacing non-numeric values with 0
            weight_series = pd.to_numeric(site_df['net_weight_calculated'], errors='coerce')
            weight_series = weight_series.fillna(0)  # Replace NaN with 0
            total_waste = weight_series.sum()
            debug_info += f", Net weights: {weight_series.tolist()}, Sum: {total_waste}"
        else:
            debug_info += ", No net_weight_calculated column"
        
        total_trips = len(site_df)  # Each ticket represents a trip
        
        # Calculate trips per 3-hour windows
        trips_by_hour_window = {}
        if 'date' in site_df.columns and len(site_df) > 0 and not site_df['date'].isna().all():
            site_df['hour'] = site_df['date'].dt.hour
            
            # Create 3-hour windows: 0-3, 3-6, 6-9, 9-12, 12-15, 15-18, 18-21, 21-24
            window_labels = ['0-3', '3-6', '6-9', '9-12', '12-15', '15-18', '18-21', '21-24']
            for i, label in enumerate(window_labels):
                start_hour = i * 3
                end_hour = (i + 1) * 3
                window_mask = (site_df['hour'] >= start_hour) & (site_df['hour'] < end_hour)
                trips_by_hour_window[label] = len(site_df[window_mask])
        
        # Calculate daily capacity (sum of unique machines' capacity)
        daily_capacity = 0
        if 'Total_capacity_per_day' in site_df.columns and 'Machines' in site_df.columns and len(site_df) > 0:
            # Group by unique machines and sum their capacities
            machine_capacity = site_df.groupby('Machines')['Total_capacity_per_day'].first().sum()
            daily_capacity = int(machine_capacity) if not pd.isna(machine_capacity) else 0
            debug_info += f", Daily capacity: {daily_capacity}"
        
        return {
            'total_waste': int(total_waste) if not pd.isna(total_waste) else 0,
            'total_trips': total_trips,
            'trips_by_hour': trips_by_hour_window,
            'daily_capacity': daily_capacity,
            'debug_info': debug_info
        }
        
    except Exception as e:
        logger.error(f"Error calculating site metrics for {site_name}: {e}")
        return {
            'total_waste': 0,
            'total_trips': 0,
            'trips_by_hour': {},
            'daily_capacity': 0,
            'debug_info': f'Error: {str(e)}'
        }



def create_animated_number_component(value, prefix="", suffix="", animation_class="counter-animation"):
    """Create an animated number component with counting effect"""
    # Ensure value is a valid number
    if not isinstance(value, (int, float)) or pd.isna(value):
        value = 0
    
    return html.Div([
        html.Span(prefix, className="number-prefix"),
        html.Span(
            str(int(value)),
            className=f"animated-number {animation_class}",
            **{"data-target": str(int(value))}
        ),
        html.Span(suffix, className="number-suffix")
    ], className="animated-number-container")

def create_trips_per_hour_chart(trips_by_hour_window, theme):
    """Create simple bar chart of trips per 3-hour window"""
    
    # Define 3-hour windows
    windows = ['0-3', '3-6', '6-9', '9-12', '12-15', '15-18', '18-21', '21-24']
    
    # Get counts for each window (0 if no data)
    counts = [trips_by_hour_window.get(window, 0) for window in windows]
    
    # If no data at all, show empty state
    if sum(counts) == 0:
        return html.Div(
            "No trips recorded for this site today",
            style={
                'textAlign': 'center',
                'color': '#999',
                'padding': '2rem',
                'height': '250px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': '1rem'
            }
        )
    
    # Create simple bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=windows,
            y=counts,
            marker_color='#3182CE',  # Simple blue color
            text=counts,  # Show count on top of each bar
            textposition='outside',
            hovertemplate='<b>%{x} Hours</b><br>Tickets: %{y}<extra></extra>'
        )
    ])
    
    # Simple layout
    fig.update_layout(
        title='Tickets by 3-Hour Time Window',
        title_font_size=14,
        title_x=0.5,  # Center title
        xaxis_title='Time Window (Hours)',
        yaxis_title='Number of Tickets',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
        font=dict(color='white', size=12),
        margin=dict(l=50, r=50, t=50, b=50),
        height=250,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=11),
            dtick=1  # Show integer ticks only
        )
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},  # Hide toolbar
        style={'height': '250px'}
    )

def create_trips_per_hour_chart_markers_only(trips_by_hour_window, theme):
    """Create simple scatter plot (markers only) of trips per 3-hour window"""
    
    windows = ['0-3', '3-6', '6-9', '9-12', '12-15', '15-18', '18-21', '21-24']
    counts = [trips_by_hour_window.get(window, 0) for window in windows]
    
    if sum(counts) == 0:
        return html.Div(
            "No trips recorded",
            style={
                'textAlign': 'center',
                'color': '#999',
                'padding': '2rem',
                'height': '240px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }
        )
    
    fig = go.Figure()
    
    # Add markers only (no connecting lines)
    fig.add_trace(go.Scatter(
        x=windows,
        y=counts,
        mode='markers+text',
        marker=dict(
            color='#3182CE',
            size=15,
            line=dict(color='white', width=2)
        ),
        text=counts,
        textposition='top center',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{x} Hours</b><br>Tickets: %{y}<extra></extra>',
        name='Tickets'
    ))
    
    fig.update_layout(
        title='Tickets by Time Window',
        title_font_size=14,
        title_x=0.5,
        xaxis_title='Time Window',
        yaxis_title='Tickets',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        margin=dict(l=40, r=40, t=40, b=40),
        height=240,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=10),
            dtick=1,
            range=[0, max(counts) + 1] if max(counts) > 0 else [0, 1]
        )
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '240px'}
    )

def get_enhanced_metric_cards_for_rotation(df, rotation_data, theme_styles):
    """Get enhanced metric cards with specific requirements - FIXED DAILY CAPACITY UNIT"""
    theme = theme_styles["theme"]
    
    try:
        # Get current site details safely
        current_site = rotation_data.get('current_site', 'Unknown')
        current_agency = rotation_data.get('current_agency', 'Unknown')
        current_cluster = rotation_data.get('current_cluster', 'Unknown')
        
        # Get last available date
        last_date = get_last_available_date(df)
        
        # Calculate site-specific metrics
        site_metrics = calculate_site_metrics(df, current_site, last_date)
        
        # Format waste amount in Indian numbering safely
        waste_amount = site_metrics.get('total_waste', 0)
        waste_formatted = format_indian_number(waste_amount) if waste_amount > 0 else "0"
        
        # Get debug info
        debug_info = site_metrics.get('debug_info', 'No debug info')
        
        # Get additional metrics safely
        total_tickets = 0
        machine_types = 0
        
        if not df.empty and 'Site' in df.columns:
            site_mask = df['Site'] == current_site
            site_data = df[site_mask]
            
            total_tickets = len(site_data)
            
            if 'Machines' in site_data.columns:
                machine_types = site_data['Machines'].nunique()

        return [
            {
                "icon": "🏢",
                "title": "",  # Remove title for Card 1
                "value": f"Agency: {current_agency}",
                "secondary_value": f"Cluster: {current_cluster}",
                "tertiary_value": f"Site: {current_site}",
                "unit": "",
                "status": "online",
                "icon_animation": "pulse-slow"
            },
            {
                "icon": "⚖️",
                "title": "Total Waste Remediated",
                "value": waste_formatted,
                "unit": "kgs",
                "sub_text": f"on {last_date.strftime('%d %b %Y')}",
                "status": "online",
                "animation_type": "counter",
                "raw_value": waste_amount,
                "icon_animation": "bounce-subtle"
            },
            {
                "icon": "🚛",
                "title": "Total Trips Done",
                "value": str(site_metrics.get('total_trips', 0)),
                "unit": "trips",
                "sub_text": f"on {last_date.strftime('%d %b %Y')}",
                "status": "online",
                "animation_type": "counter",
                "raw_value": site_metrics.get('total_trips', 0),
                "icon_animation": "move-truck"
            },
            {
                "icon": "📊",
                "title": "Trips Per 3-Hour Window",
                "status": "info",
                "chart_data": site_metrics.get('trips_by_hour', {}),
                "chart_type": "trips_histogram"
            },
            {
                "icon": "🎫",
                "title": "Active Tickets",
                "value": str(total_tickets),
                "unit": "total",
                "status": "info",
                "animation_type": "counter",
                "raw_value": total_tickets,
                "icon_animation": "flip"
            },
            {
                "icon": "🔧",
                "title": "Machine Types",
                "value": str(machine_types),
                "unit": "active",
                "status": "online",
                "icon_animation": "rotate"
            },
            {
                "icon": "🏭",
                "title": "Daily Capacity",
                "value": str(site_metrics.get('daily_capacity', 0)),
                "unit": "Metric tonnes per day",  # FIXED UNIT AS REQUESTED
                "status": "info",
                "animation_type": "counter",
                "raw_value": site_metrics.get('daily_capacity', 0),
                "icon_animation": "scale-pulse"
            },
            {
                "icon": "⏰",
                "title": "Next Update",
                "value": "15s",
                "unit": "auto-rotate",
                "status": "info",
                "icon_animation": "spin-slow"
            }
        ]
        
    except Exception as e:
        logger.error(f"Error creating enhanced metric cards: {e}")
        # Return fallback cards
        return [
            {
                "icon": "❌",
                "title": "Error",
                "value": "Loading Failed",
                "unit": "Please refresh",
                "status": "error"
            } for _ in range(8)
        ]

def create_enhanced_metric_cards_grid(metrics_data, theme_styles):
    """Create enhanced metric cards grid with animations"""
    cards = []
    theme = theme_styles["theme"]
    
    for i, metric in enumerate(metrics_data):
        try:
            status_class = f"status-{metric.get('status', 'info')}"
            icon_animation = metric.get('icon_animation', '')
            
            # Create chart if specified
            chart_element = None
            if metric.get('chart_data') and metric.get('chart_type') == 'trips_histogram':
                chart_element = create_trips_per_hour_chart_markers_only(metric['chart_data'], theme)
                        
            # Build card content based on card type
            if i == 0:  # Card 1: Agency, Cluster, Site info (enhanced format)
                card_content = [
                    html.Div(
                        metric["icon"],
                        className=f"metric-icon {icon_animation}",
                        style={'marginBottom': '1rem'}
                    ),
                    html.Div([
                        html.Div(metric.get("value", ""), className="agency-line"),
                        html.Div(metric.get("secondary_value", ""), className="cluster-line"),
                        html.Div(metric.get("tertiary_value", ""), className="site-line")
                    ], className="location-info-container"),
                    html.Div(
                        html.Span(
                            className=f"status-indicator {status_class}",
                            title=f"Status: {metric.get('status', 'info')}"
                        ) if metric.get('status') else "",
                        style={'marginTop': '1rem'}
                    )
                ]
            elif i == 1:  # Card 2: Total Waste with Debug info
                raw_value = metric.get('raw_value', 0)
                if not isinstance(raw_value, (int, float)) or pd.isna(raw_value):
                    raw_value = 0
                    
                card_content = [
                    html.Div(
                        metric["icon"],
                        className=f"metric-icon {icon_animation}"
                    ),
                    html.Div(
                        [
                            metric["title"],
                            html.Span(
                                className=f"status-indicator {status_class}",
                                title=f"Status: {metric.get('status', 'info')}"
                            ) if metric.get('status') else ""
                        ],
                        className="metric-title"
                    ),
                    html.Div(
                        create_animated_number_component(raw_value),
                        className="metric-value animated-value"
                    ),
                    html.Div([
                        html.Span(metric.get("unit", ""), className="unit-main"),
                        html.Br() if metric.get('sub_text') else "",
                        html.Span(metric.get('sub_text', ''), className="unit-sub")
                    ], className="metric-unit"),
                    # Add debug info display
                    html.Div(
                        metric.get('debug_text', ''),
                        className="debug-info",
                        style={
                            'fontSize': '0.7rem',
                            'color': theme.get('warning', '#ffc107'),
                            'marginTop': '0.5rem',
                            'padding': '0.25rem',
                            'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                            'borderRadius': '4px',
                            'wordBreak': 'break-word'
                        }
                    ) if metric.get('debug_text') else None
                ]
            elif metric.get('animation_type') == 'counter':  # Other animated counter cards
                raw_value = metric.get('raw_value', 0)
                if not isinstance(raw_value, (int, float)) or pd.isna(raw_value):
                    raw_value = 0
                    
                card_content = [
                    html.Div(
                        metric["icon"],
                        className=f"metric-icon {icon_animation}"
                    ),
                    html.Div(
                        [
                            metric["title"],
                            html.Span(
                                className=f"status-indicator {status_class}",
                                title=f"Status: {metric.get('status', 'info')}"
                            ) if metric.get('status') else ""
                        ],
                        className="metric-title"
                    ),
                    html.Div(
                        create_animated_number_component(raw_value),
                        className="metric-value animated-value"
                    ),
                    html.Div([
                        html.Span(metric.get("unit", ""), className="unit-main"),
                        html.Br() if metric.get('sub_text') else "",
                        html.Span(metric.get('sub_text', ''), className="unit-sub")
                    ], className="metric-unit")
                ]
            else:  # Regular cards
                card_content = [
                    html.Div(
                        metric["icon"],
                        className=f"metric-icon {icon_animation}"
                    ),
                    html.Div(
                        [
                            metric["title"],
                            html.Span(
                                className=f"status-indicator {status_class}",
                                title=f"Status: {metric.get('status', 'info')}"
                            ) if metric.get('status') else ""
                        ],
                        className="metric-title"
                    ),
                    html.Div(
                        metric.get("value", ""),
                        className="metric-value"
                    ),
                    html.Div(
                        metric.get("unit", ""),
                        className="metric-unit"
                    )
                ]
            
            # Add chart if available and not None
            if chart_element is not None:
                card_content.append(chart_element)
            
            card = html.Div(
                className="metric-card card-enhanced",
                children=[content for content in card_content if content is not None],
                id=f"metric-card-{i}"
            )
            cards.append(card)
            
        except Exception as e:
            logger.error(f"Error creating card {i}: {e}")
            # Create fallback card
            card = html.Div(
                className="metric-card",
                children=[
                    html.Div("❌", className="metric-icon"),
                    html.Div("Card Error", className="metric-title"),
                    html.Div(f"Card {i+1}", className="metric-value"),
                    html.Div("Error", className="metric-unit")
                ],
                id=f"metric-card-{i}"
            )
            cards.append(card)
    
    return html.Div(
        className="cards-grid",
        children=cards
    )

def create_responsive_logo(position, alt_text, css_class="responsive-logo"):
    """Create responsive logo component"""
    return html.Img(
        src=f"/assets/img/{position}.png",
        alt=alt_text,
        className=css_class,
        style={
            "height": "clamp(40px, 8vh, 60px)",
            "width": "auto",
            "objectFit": "contain",
            "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
            "transition": "all 0.3s ease",
            "cursor": "pointer"
        }
    )

def create_hero_section():
    """Create the hero section with logos and title"""
    return html.Div(
        className="hero-section",
        children=[
            html.Div(
                className="hero-content",
                children=[
                    # Left Logo
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "flexShrink": "0"
                        },
                        children=[
                            create_responsive_logo("left", "Left Organization Logo", "logo-left logo-animate")
                        ]
                    ),
                    
                    # Title Section
                    html.Div(
                        className="hero-title-section",
                        style={
                            "textAlign": "center",
                            "flex": "1",
                            "padding": "0 clamp(1rem, 3vw, 2rem)",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "height": "100%"
                        },
                        children=[
                            html.H1(
                                "Swaccha Andhra Corporation",
                                className="hero-title title-animate",
                                style={
                                    "margin": "0",
                                    "padding": "0",
                                    "fontSize": "clamp(1.5rem, 4vw, 2.5rem)",
                                    "fontWeight": "800",
                                    "lineHeight": "1.1",
                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)",
                                    "letterSpacing": "-0.5px"
                                }
                            ),
                            html.P(
                                "Real Time Legacy Waste Remediation Progress Tracker",
                                className="hero-subtitle subtitle-animate",
                                style={
                                    "margin": "0.25rem 0 0 0",
                                    "padding": "0",
                                    "fontSize": "clamp(0.8rem, 1.8vw, 1rem)",
                                    "fontWeight": "500",
                                    "lineHeight": "1.3",
                                    "opacity": "0.9",
                                    "textAlign": "center"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo  
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "flexShrink": "0"
                        },
                        children=[
                            create_responsive_logo("right", "Right Organization Logo", "logo-right logo-animate")
                        ]
                    )
                ]
            )
        ]
    )

def build_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """
    Build the enhanced auto-rotating public layout with animations
    """
    # Use existing theme system
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        className="public-layout enhanced-layout",
        # Apply theme CSS variables for compatibility
        style={
            "--primary-bg": theme_styles["theme"]["primary_bg"],
            "--secondary-bg": theme_styles["theme"]["secondary_bg"],
            "--accent-bg": theme_styles["theme"]["accent_bg"],
            "--card-bg": theme_styles["theme"]["card_bg"],
            "--text-primary": theme_styles["theme"]["text_primary"],
            "--text-secondary": theme_styles["theme"]["text_secondary"],
            "--brand-primary": theme_styles["theme"]["brand_primary"],
            "--border-light": theme_styles["theme"].get("border_light", theme_styles["theme"]["accent_bg"]),
            "--success": theme_styles["theme"]["success"],
            "--warning": theme_styles["theme"]["warning"],
            "--error": theme_styles["theme"]["error"],
            "--info": theme_styles["theme"]["info"]
        },
        children=[
            # Auto-rotation interval component (15 seconds)
            dcc.Interval(
                id='auto-rotation-interval',
                interval=15*1000,  # 15 seconds in milliseconds
                n_intervals=0
            ),
            
            # Store for triggering animations
            dcc.Store(id='animation-trigger', data=0),
            
            # Hover overlay banner (admin access)
            create_hover_overlay_banner(theme_name),
            
            # Main content area
            html.Div(
                className="main-content",
                children=[
                    # Hero section with logos and title
                    create_hero_section(),
                    
                    # Dynamic metric cards grid (will be updated by callback)
                    html.Div(
                        id="dynamic-cards-container",
                        className="cards-grid"
                    )
                ]
            )
        ]
    )

# Callback for auto-rotation with enhanced metrics
@callback(
    Output('dynamic-cards-container', 'children'),
    [Input('auto-rotation-interval', 'n_intervals'),
     Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_enhanced_rotating_cards(n_intervals, theme_name):
    """Update cards with enhanced metrics and animations"""
    try:
        logger.info(f"🔄 Enhanced rotation update #{n_intervals}")
        
        # Load CSV data
        df = load_csv_visualization_data()
        
        # Get current rotation data
        rotation_data = get_rotation_data(df, n_intervals)
        
        logger.info(f"📊 Focus: {rotation_data.get('current_focus', 'Unknown')}")
        logger.info(f"🏢 Agency: {rotation_data.get('current_agency', 'Unknown')}")
        logger.info(f"🗺️ Cluster: {rotation_data.get('current_cluster', 'Unknown')}")
        logger.info(f"📍 Site: {rotation_data.get('current_site', 'Unknown')}")
        
        # Debug: Print CSV data info
        if not df.empty:
            logger.info(f"📋 CSV Columns: {list(df.columns)}")
            logger.info(f"📊 CSV Shape: {df.shape}")
            if 'net_weight_calculated' in df.columns:
                weight_sample = df['net_weight_calculated'].head().tolist()
                logger.info(f"⚖️ Weight Sample: {weight_sample}")
                weight_sum = pd.to_numeric(df['net_weight_calculated'], errors='coerce').sum()
                logger.info(f"⚖️ Total Weight in CSV: {weight_sum}")
        
        # Get theme styles
        theme_styles = get_theme_styles(theme_name or 'dark')
        
        # Get enhanced metric cards for current rotation
        metrics_data = get_enhanced_metric_cards_for_rotation(df, rotation_data, theme_styles)
        
        # Log debug info from Card 2
        if len(metrics_data) > 1:
            card2_debug = metrics_data[1].get('debug_text', 'No debug info')
            logger.info(f"🐛 Card 2 Debug: {card2_debug}")
        
        # Create enhanced cards grid
        cards_grid = create_enhanced_metric_cards_grid(metrics_data, theme_styles)
        
        # Return the children of the cards grid
        return cards_grid.children
        
    except Exception as e:
        logger.error(f"❌ Error updating enhanced rotating cards: {e}")
        import traceback
        traceback.print_exc()
        
        # Return simple fallback cards
        try:
            fallback_cards = []
            for i in range(8):
                fallback_cards.append(
                    html.Div(
                        className="metric-card",
                        children=[
                            html.Div("⚠️", className="metric-icon"),
                            html.Div("Loading Error", className="metric-title"),
                            html.Div(f"Card {i+1}", className="metric-value"),
                            html.Div("Please refresh", className="metric-unit"),
                            html.Div(f"Error: {str(e)[:50]}...", className="debug-info") if i == 1 else None
                        ],
                        style={
                            "background": "rgba(255, 193, 7, 0.1)",
                            "border": "2px solid #ffc107",
                            "borderRadius": "8px",
                            "padding": "1rem",
                            "textAlign": "center"
                        }
                    )
                )
            return fallback_cards
            
        except:
            # Ultimate fallback
            return [html.Div("System Error - Please refresh page", 
                           style={'color': 'red', 'textAlign': 'center', 'padding': '2rem'})]

# Clientside callback for counter animations
clientside_callback(
    """
    function(children) {
        // Counter animation function
        function animateCounters() {
            const counters = document.querySelectorAll('.animated-number');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target') || counter.textContent.replace(/,/g, ''));
                if (isNaN(target) || target === 0) {
                    counter.textContent = '0';
                    return;
                }
                
                const duration = Math.min(2000, Math.max(1000, target * 2)); // Dynamic duration
                const increment = target / (duration / 16); // 60fps
                let current = 0;
                
                // Add loading class
                counter.classList.add('loading-number');
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString('en-IN');
                        counter.classList.remove('loading-number');
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString('en-IN');
                    }
                }, 16);
            });
        }
        
        // Trigger animations after DOM is updated
        if (children && children.length > 0) {
            setTimeout(animateCounters, 300);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('animation-trigger', 'data'),
    [Input('dynamic-cards-container', 'children')],
    prevent_initial_call=True
)

# Export functions
__all__ = [
    'build_public_layout',
    'load_csv_visualization_data',
    'get_rotation_data',
    'get_enhanced_metric_cards_for_rotation',
    'format_indian_number'
]