# layouts/public_layout.py
"""
Enhanced Auto-Rotating Public Landing Page Layout for Swaccha Andhra Corporation
Updated to use public_mini_processed_dates_fixed.csv data
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

def load_agency_data():
    """Load data from public_mini_processed_dates_fixed.csv"""
    try:
        csv_path = 'data/public_mini_processed_dates_fixed.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            logger.info(f"✅ Loaded {len(df)} records from agency data")
            
            # Convert date columns to datetime if needed
            date_columns = ['start_date', 'planned_end_date', 'expected_end_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Clean column names for easier access
            df.columns = df.columns.str.strip()
            
            return df
        else:
            logger.warning(f"CSV file not found at {csv_path}")
            return create_sample_agency_data()
    except Exception as e:
        logger.error(f"Error loading agency data: {e}")
        return create_sample_agency_data()

def create_sample_agency_data():
    """Create sample data matching CSV structure for testing"""
    agencies = ['Swaccha Andhra Corporation', 'Municipal Corp', 'Green Solutions']
    clusters = ['Nellore', 'Chittor', 'Tirupathi', 'GVMC', 'Kurnool']
    sites = ['Site A', 'Site B', 'Site C', 'Site D', 'Site E']
    machines = ['Excavator', 'Truck', 'Loader', 'Compactor']
    
    data = []
    base_date = datetime.now()
    
    for i in range(50):
        data.append({
            'Agency': np.random.choice(agencies),
            'Sub-contractor': f'Contractor {i%3 + 1}',
            'Cluster': np.random.choice(clusters),
            'Site': f'{np.random.choice(sites)} {i}',
            'Machine': np.random.choice(machines),
            'Daily_Capacity': np.random.uniform(10, 50),
            'start_date': base_date - timedelta(days=np.random.randint(0, 30)),
            'planned_end_date': base_date + timedelta(days=np.random.randint(30, 100)),
            'expected_end_date': base_date + timedelta(days=np.random.randint(30, 120)),
            'days_to_sept30': str(np.random.randint(50, 150)),
            'Quantity to be remediated in MT': np.random.randint(100, 1000),
            'Cumulative Quantity remediated till date in MT': np.random.randint(0, 500),
            'Active_site': np.random.choice(['yes', 'no']),
            'net_to_be_remediated_mt': np.random.randint(50, 500),
            'days_required': np.random.uniform(30, 120)
        })
    
    return pd.DataFrame(data)

def get_agency_rotation_data(df, rotation_index=0):
    """Get data for current agency rotation"""
    if df.empty:
        return {
            'agencies': [],
            'current_agency': 'No Data Available',
            'agency_data': pd.DataFrame()
        }
    
    try:
        # Get all unique agencies
        agencies = []
        if 'Agency' in df.columns:
            agencies = df['Agency'].dropna().unique().tolist()
        
        if not agencies:
            return {
                'agencies': [],
                'current_agency': 'No Agencies Found',
                'agency_data': pd.DataFrame()
            }
        
        # Get current agency based on rotation
        current_agency_index = rotation_index % len(agencies)
        current_agency = agencies[current_agency_index]
        
        # Filter data for current agency
        agency_data = df[df['Agency'] == current_agency].copy()
        
        return {
            'agencies': agencies,
            'current_agency': current_agency,
            'agency_data': agency_data
        }
        
    except Exception as e:
        logger.error(f"Error getting agency rotation data: {e}")
        return {
            'agencies': [],
            'current_agency': 'Error Loading',
            'agency_data': pd.DataFrame()
        }

def calculate_agency_metrics(agency_data):
    """Calculate all metrics for the current agency"""
    if agency_data.empty:
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'planned_not_started': 0,
            'sites_not_on_track': 0,
            'sites_on_track': 0,
            'cluster_completion': {},
            'critically_lagging': 0
        }
    
    try:
        today = datetime.now().date()
        sept_30 = datetime(2024, 9, 30).date()  # Assuming 2024, adjust as needed
        
        # Card 1: Clusters and Sites count
        clusters_count = agency_data['Cluster'].nunique() if 'Cluster' in agency_data.columns else 0
        sites_count = agency_data['Site'].nunique() if 'Site' in agency_data.columns else 0
        
        # Card 2: Active and Inactive sites
        active_sites = 0
        inactive_sites = 0
        if 'Active_site' in agency_data.columns:
            active_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'yes'])
            inactive_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'no'])
        
        # Card 3: Planned vs Deployed machines
        planned_machines = agency_data['Machine'].nunique() if 'Machine' in agency_data.columns else 0
        deployed_machines = 0
        if 'Machine' in agency_data.columns and 'Active_site' in agency_data.columns:
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            deployed_machines = active_data['Machine'].nunique() if not active_data.empty else 0
        
        # Card 4: Planned but not started sites
        planned_not_started = 0
        if 'start_date' in agency_data.columns and 'Active_site' in agency_data.columns:
            mask = (agency_data['start_date'].dt.date < today) & (agency_data['Active_site'].str.lower() == 'no')
            planned_not_started = len(agency_data[mask])
        
        # Card 5 & 6: Sites not on track / on track
        sites_not_on_track = 0
        sites_on_track = 0
        if 'Active_site' in agency_data.columns and 'expected_end_date' in agency_data.columns:
            active_sites_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_sites_data.empty:
                not_on_track_mask = active_sites_data['expected_end_date'].dt.date > sept_30
                sites_not_on_track = len(active_sites_data[not_on_track_mask])
                sites_on_track = len(active_sites_data[~not_on_track_mask])
        
        # Card 7: Cluster wise completion percentage
        cluster_completion = {}
        if all(col in agency_data.columns for col in ['Cluster', 'Cumulative Quantity remediated till date in MT', 'Quantity to be remediated in MT']):
            for cluster in agency_data['Cluster'].unique():
                cluster_data = agency_data[agency_data['Cluster'] == cluster]
                total_planned = cluster_data['Quantity to be remediated in MT'].sum()
                total_completed = cluster_data['Cumulative Quantity remediated till date in MT'].sum()
                completion_pct = (total_completed / total_planned * 100) if total_planned > 0 else 0
                cluster_completion[cluster] = round(completion_pct, 1)
        
        # Card 8: Critically lagging sites
        critically_lagging = 0
        if all(col in agency_data.columns for col in ['Active_site', 'days_required', 'days_to_sept30']):
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_data.empty:
                # Convert days_to_sept30 to numeric (it might be string)
                days_to_sept30_numeric = pd.to_numeric(active_data['days_to_sept30'], errors='coerce')
                critically_lagging_mask = active_data['days_required'] > days_to_sept30_numeric
                critically_lagging = len(active_data[critically_lagging_mask.fillna(False)])
        
        return {
            'clusters_count': clusters_count,
            'sites_count': sites_count,
            'active_sites': active_sites,
            'inactive_sites': inactive_sites,
            'planned_machines': planned_machines,
            'deployed_machines': deployed_machines,
            'planned_not_started': planned_not_started,
            'sites_not_on_track': sites_not_on_track,
            'sites_on_track': sites_on_track,
            'cluster_completion': cluster_completion,
            'critically_lagging': critically_lagging
        }
        
    except Exception as e:
        logger.error(f"Error calculating agency metrics: {e}")
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'planned_not_started': 0,
            'sites_not_on_track': 0,
            'sites_on_track': 0,
            'cluster_completion': {},
            'critically_lagging': 0
        }

def create_cluster_completion_chart(cluster_completion, theme):
    """Create a simple bar chart for cluster completion percentages"""
    if not cluster_completion:
        return html.Div(
            "No completion data available",
            style={
                'textAlign': 'center',
                'color': '#999',
                'padding': '1rem',
                'height': '200px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }
        )
    
    clusters = list(cluster_completion.keys())
    percentages = list(cluster_completion.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=clusters,
            y=percentages,
            marker_color='#28a745',
            text=[f'{p}%' for p in percentages],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Completion: %{y}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Cluster Completion %',
        title_font_size=12,
        title_x=0.5,
        xaxis_title='Clusters',
        yaxis_title='Completion %',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10),
        margin=dict(l=40, r=40, t=40, b=40),
        height=200,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(size=9),
            range=[0, 100]
        )
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '200px'}
    )

def create_agency_metric_cards(current_agency, metrics, theme_styles):
    """Create the 8 metric cards for the current agency"""
    cards = []
    
    # Card 1: Clusters and Sites count
    card1 = html.Div(
        className="metric-card agency-card",
        children=[
            html.Div("🗺️", className="metric-icon pulse-icon"),
            html.Div("Clusters & Sites", className="metric-title"),
            html.Div([
                html.Div([
                    html.Span("Clusters: ", className="metric-label"),
                    html.Span(str(metrics['clusters_count']), className="metric-number animate-counter")
                ], className="metric-line"),
                html.Hr(className="metric-divider"),
                html.Div([
                    html.Span("Sites: ", className="metric-label"),
                    html.Span(str(metrics['sites_count']), className="metric-number animate-counter")
                ], className="metric-line")
            ], className="stacked-metrics")
        ]
    )
    
    # Card 2: Active and Inactive sites
    card2 = html.Div(
        className="metric-card agency-card",
        children=[
            html.Div("🟢", className="metric-icon bounce-icon"),
            html.Div("Site Status", className="metric-title"),
            html.Div([
                html.Div([
                    html.Span("Active: ", className="metric-label"),
                    html.Span(str(metrics['active_sites']), className="metric-number animate-counter active-number")
                ], className="metric-line"),
                html.Hr(className="metric-divider"),
                html.Div([
                    html.Span("Inactive: ", className="metric-label"),
                    html.Span(str(metrics['inactive_sites']), className="metric-number animate-counter inactive-number")
                ], className="metric-line")
            ], className="stacked-metrics")
        ]
    )
    
    # Card 3: Planned vs Deployed machines
    card3 = html.Div(
        className="metric-card agency-card",
        children=[
            html.Div("🚛", className="metric-icon slide-icon"),
            html.Div("Machines", className="metric-title"),
            html.Div([
                html.Div([
                    html.Span("Planned: ", className="metric-label"),
                    html.Span(str(metrics['planned_machines']), className="metric-number animate-counter")
                ], className="metric-line"),
                html.Hr(className="metric-divider"),
                html.Div([
                    html.Span("Deployed: ", className="metric-label"),
                    html.Span(str(metrics['deployed_machines']), className="metric-number animate-counter deployed-number")
                ], className="metric-line")
            ], className="stacked-metrics")
        ]
    )
    
    # Card 4: Planned but not started sites
    card4 = html.Div(
        className="metric-card agency-card warning-card",
        children=[
            html.Div("⏳", className="metric-icon rotate-icon"),
            html.Div("Not Started", className="metric-title"),
            html.Div(str(metrics['planned_not_started']), className="metric-value large-number animate-counter"),
            html.Div("planned sites", className="metric-unit")
        ]
    )
    
    # Card 5: Sites not on track
    card5 = html.Div(
        className="metric-card agency-card danger-card",
        children=[
            html.Div("🔴", className="metric-icon shake-icon"),
            html.Div("Not On Track", className="metric-title"),
            html.Div(str(metrics['sites_not_on_track']), className="metric-value large-number animate-counter"),
            html.Div("sites behind", className="metric-unit")
        ]
    )
    
    # Card 6: Sites on track
    card6 = html.Div(
        className="metric-card agency-card success-card",
        children=[
            html.Div("✅", className="metric-icon glow-icon"),
            html.Div("On Track", className="metric-title"),
            html.Div(str(metrics['sites_on_track']), className="metric-value large-number animate-counter"),
            html.Div("sites", className="metric-unit")
        ]
    )
    
    # Card 7: Cluster completion chart
    card7 = html.Div(
        className="metric-card agency-card chart-card",
        children=[
            html.Div("📊", className="metric-icon pulse-icon"),
            html.Div("Completion %", className="metric-title"),
            create_cluster_completion_chart(metrics['cluster_completion'], theme_styles["theme"])
        ]
    )
    
    # Card 8: Critically lagging sites
    card8 = html.Div(
        className="metric-card agency-card critical-card",
        children=[
            html.Div("🚨", className="metric-icon blink-icon"),
            html.Div("Critical", className="metric-title"),
            html.Div(str(metrics['critically_lagging']), className="metric-value large-number animate-counter"),
            html.Div("lagging sites", className="metric-unit")
        ]
    )
    
    return [card1, card2, card3, card4, card5, card6, card7, card8]

def create_agency_header(current_agency):
    """Create the agency header with today's date"""
    today = datetime.now().strftime("%d %B %Y")
    
    return html.Div(
        className="agency-header fade-in",
        children=[
            html.H1(current_agency, className="agency-title animate-title"),
            html.P(f"Real-time Dashboard - {today}", className="agency-date animate-subtitle")
        ]
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
    Build the enhanced auto-rotating public layout with agency-specific metrics
    """
    # Use existing theme system
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        className="public-layout enhanced-layout agency-layout",
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
                    
                    # Agency header (will be updated by callback)
                    html.Div(id="agency-header-container"),
                    
                    # Dynamic metric cards grid (will be updated by callback)
                    html.Div(
                        id="dynamic-cards-container",
                        className="cards-grid agency-cards-grid"
                    )
                ]
            )
        ]
    )

# Callback for auto-rotation with agency metrics
@callback(
    [Output('agency-header-container', 'children'),
     Output('dynamic-cards-container', 'children')],
    [Input('auto-rotation-interval', 'n_intervals'),
     Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_agency_dashboard(n_intervals, theme_name):
    """Update dashboard with agency-specific metrics and animations"""
    try:
        logger.info(f"🔄 Agency rotation update #{n_intervals}")
        
        # Load agency data
        df = load_agency_data()
        
        # Get current rotation data
        rotation_data = get_agency_rotation_data(df, n_intervals)
        current_agency = rotation_data['current_agency']
        agency_data = rotation_data['agency_data']
        
        logger.info(f"🏢 Current Agency: {current_agency}")
        logger.info(f"📊 Agency Records: {len(agency_data)}")
        
        # Calculate metrics for current agency
        metrics = calculate_agency_metrics(agency_data)
        
        # Get theme styles
        theme_styles = get_theme_styles(theme_name or 'dark')
        
        # Create agency header
        header = create_agency_header(current_agency)
        
        # Create metric cards
        cards = create_agency_metric_cards(current_agency, metrics, theme_styles)
        
        logger.info(f"✅ Created {len(cards)} cards for {current_agency}")
        
        return header, cards
        
    except Exception as e:
        logger.error(f"❌ Error updating agency dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Return fallback content
        fallback_header = html.Div(
            "Error Loading Agency Data",
            className="agency-header",
            style={'color': 'red', 'textAlign': 'center', 'padding': '1rem'}
        )
        
        fallback_cards = []
        for i in range(8):
            fallback_cards.append(
                html.Div(
                    className="metric-card",
                    children=[
                        html.Div("⚠️", className="metric-icon"),
                        html.Div("Loading Error", className="metric-title"),
                        html.Div(f"Card {i+1}", className="metric-value"),
                        html.Div("Please refresh", className="metric-unit")
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
        
        return fallback_header, fallback_cards

# Clientside callback for counter animations
clientside_callback(
    """
    function(children) {
        // Counter animation function
        function animateCounters() {
            const counters = document.querySelectorAll('.animate-counter');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent || '0');
                if (isNaN(target) || target === 0) {
                    counter.textContent = '0';
                    return;
                }
                
                const duration = Math.min(2000, Math.max(800, target * 50));
                const increment = target / (duration / 16);
                let current = 0;
                
                counter.classList.add('counting');
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target;
                        counter.classList.remove('counting');
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current);
                    }
                }, 16);
            });
        }
        
        // Trigger animations after DOM is updated
        if (children && children.length > 0) {
            setTimeout(animateCounters, 400);
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
    'load_agency_data',
    'get_agency_rotation_data',
    'calculate_agency_metrics'
]