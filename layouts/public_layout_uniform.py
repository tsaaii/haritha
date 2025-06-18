# layouts/public_layout_uniform.py
"""
Updated layout with specific card content and uniform sizing
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import numpy as np

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

# Initialize logger FIRST
logger = logging.getLogger(__name__)

# AGENCY NAMES MAPPING
AGENCY_NAMES = {
    'Zigma': 'Zigma Global Enviro Solutions Private Limited, Erode',
    'Saurashtra': 'Saurastra Enviro Pvt Ltd, Gujarat', 
    'Tharuni': 'Tharuni Associates, Guntur',
    'Swaccha Andhra Corporation': 'Swaccha Andhra Corporation',
    'Municipal Corp': 'Municipal Corporation Services',
    'Green Solutions': 'Green Solutions Environmental Services'
}

def get_display_agency_name(agency_key):
    """Get the full display name for an agency"""
    if not agency_key:
        return "Unknown Agency"
        
    # Try exact match first
    if agency_key in AGENCY_NAMES:
        return AGENCY_NAMES[agency_key]
    
    # Try partial match (case insensitive)
    agency_key_lower = agency_key.lower()
    for key, full_name in AGENCY_NAMES.items():
        if key.lower() in agency_key_lower or agency_key_lower in key.lower():
            return full_name
    
    # If no match found, return the original key with warning
    logger.warning(f"⚠️ No agency mapping found for: '{agency_key}'")
    return f"{agency_key} (Unmapped)"

def load_agency_data():
    """Load data from CSV with agency configuration logging"""
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
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Log agency mappings
            if 'Agency' in df.columns:
                unique_agencies = df['Agency'].dropna().unique()
                logger.info(f"📋 Found {len(unique_agencies)} agencies in data:")
                
                for agency in unique_agencies:
                    display_name = get_display_agency_name(agency)
                    if "(Unmapped)" in display_name:
                        status = "⚠️ UNMAPPED"
                    else:
                        status = "✅ MAPPED"
                    logger.info(f"  {status}: '{agency}' → '{display_name}'")
            
            return df
        else:
            logger.warning(f"📄 CSV file not found at {csv_path}, creating sample data")
            return create_sample_agency_data()
    except Exception as e:
        logger.error(f"❌ Error loading agency data: {e}")
        return create_sample_agency_data()

def create_sample_agency_data():
    """Create sample data using configured agency keys"""
    agency_keys = list(AGENCY_NAMES.keys())
    clusters = ['Nellore', 'Chittor', 'Tirupathi', 'GVMC', 'Kurnool', 'Erode', 'Guntur', 'Gujarat']
    sites = ['Site A', 'Site B', 'Site C', 'Site D', 'Site E']
    machines = ['Excavator', 'Truck', 'Loader', 'Compactor']
    
    data = []
    base_date = datetime.now()
    
    for i in range(60):
        agency_key = np.random.choice(agency_keys)
        
        data.append({
            'Agency': agency_key,
            'Sub-contractor': f'Contractor {i%5 + 1}',
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
    
    df = pd.DataFrame(data)
    logger.info(f"📊 Created sample data with agencies: {list(df['Agency'].unique())}")
    return df

def get_agency_rotation_data(df, rotation_index=0):
    """Get agency rotation data with display name mapping"""
    if df.empty:
        return {
            'agencies': [],
            'current_agency_key': 'No Data Available',
            'current_agency_display': 'No Data Available',
            'agency_data': pd.DataFrame()
        }
    
    try:
        # Get unique agency keys from data
        agency_keys = []
        if 'Agency' in df.columns:
            agency_keys = df['Agency'].dropna().unique().tolist()
        
        if not agency_keys:
            return {
                'agencies': [],
                'current_agency_key': 'No Agencies Found',
                'current_agency_display': 'No Agencies Found',
                'agency_data': pd.DataFrame()
            }
        
        # Get current agency for rotation
        current_agency_index = rotation_index % len(agency_keys)
        current_agency_key = agency_keys[current_agency_index]
        current_agency_display = get_display_agency_name(current_agency_key)
        
        # Filter data for current agency
        agency_data = df[df['Agency'] == current_agency_key].copy()
        
        # Log rotation with mapping status
        if "(Unmapped)" in current_agency_display:
            mapping_status = "⚠️"
        else:
            mapping_status = "✅"
        logger.info(f"🔄 Rotation #{rotation_index}: {mapping_status} '{current_agency_key}' → '{current_agency_display}'")
        
        return {
            'agencies': agency_keys,
            'current_agency_key': current_agency_key,
            'current_agency_display': current_agency_display,
            'agency_data': agency_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error in agency rotation: {e}")
        return {
            'agencies': [],
            'current_agency_key': 'Error Loading',
            'current_agency_display': 'Error Loading Data',
            'agency_data': pd.DataFrame()
        }

def calculate_agency_metrics(agency_data):
    """Calculate metrics for current agency"""
    if agency_data.empty:
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'sites_not_on_track': 0,
            'critically_lagging': 0
        }
    
    try:
        today = datetime.now().date()
        sept_30 = datetime(2024, 9, 30).date()
        
        # Calculate all metrics
        clusters_count = agency_data['Cluster'].nunique() if 'Cluster' in agency_data.columns else 0
        sites_count = agency_data['Site'].nunique() if 'Site' in agency_data.columns else 0
        
        active_sites = 0
        inactive_sites = 0
        if 'Active_site' in agency_data.columns:
            active_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'yes'])
            inactive_sites = len(agency_data[agency_data['Active_site'].str.lower() == 'no'])
        
        planned_machines = agency_data['Machine'].nunique() if 'Machine' in agency_data.columns else 0
        deployed_machines = 0
        if 'Machine' in agency_data.columns and 'Active_site' in agency_data.columns:
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            deployed_machines = active_data['Machine'].nunique() if not active_data.empty else 0
        
        sites_not_on_track = 0
        if 'Active_site' in agency_data.columns and 'expected_end_date' in agency_data.columns:
            active_sites_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_sites_data.empty:
                not_on_track_mask = active_sites_data['expected_end_date'].dt.date > sept_30
                sites_not_on_track = len(active_sites_data[not_on_track_mask])
        
        critically_lagging = 0
        if all(col in agency_data.columns for col in ['Active_site', 'days_required', 'days_to_sept30']):
            active_data = agency_data[agency_data['Active_site'].str.lower() == 'yes']
            if not active_data.empty:
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
            'sites_not_on_track': sites_not_on_track,
            'critically_lagging': critically_lagging
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating metrics: {e}")
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'sites_not_on_track': 0,
            'critically_lagging': 0
        }

def create_dual_metric_card(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color):
    """Create a card with two metrics side by side with perfect alignment"""
    return html.Div(
        className="metric-card",
        children=[
            html.Div(icon, className="metric-icon"),
            html.Div(title, className="metric-title"),
            html.Div(
                className="dual-metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-group",
                        children=[
                            html.Div(
                                metric1_value,
                                className="metric-value",
                                style={"color": metric1_color}
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-unit"
                            )
                        ]
                    ),
                    # Divider - Let CSS handle the styling
                    html.Div(
                        style={
                            "width": "1px",
                            "height": "100%",
                            "background": "linear-gradient(to bottom, transparent, rgba(255,255,255,0.3), transparent)",
                            "flexShrink": "0"
                        }
                    ),
                    # Second metric
                    html.Div(
                        className="metric-group",
                        children=[
                            html.Div(
                                metric2_value,
                                className="metric-value",
                                style={"color": metric2_color}
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-unit"
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_empty_card(card_number):
    """Create an empty placeholder card with consistent structure"""
    return html.Div(
        className="metric-card",
        style={
            "opacity": "0.5",
            "border": "2px dashed rgba(255, 255, 255, 0.3)"
        },
        children=[
            html.Div(
                "📊",
                className="metric-icon",
                style={"opacity": "0.6"}
            ),
            html.Div(
                f"Card {card_number}",
                className="metric-title"
            ),
            html.Div(
                "Coming Soon",
                className="metric-value",
                style={
                    "fontSize": "clamp(1rem, 2.5vh, 1.3rem)",
                    "opacity": "0.7",
                    "fontStyle": "italic",
                    "margin": "1rem 0"
                }
            ),
            html.Div(
                "placeholder",
                className="metric-unit",
                style={"opacity": "0.6"}
            )
        ]
    )

def create_specific_metric_cards(current_agency_display, metrics, theme_styles):
    """Create the specific 8 cards as requested"""
    cards = []
    
    # Card 1: Clusters and Total Sites
    card1 = create_dual_metric_card(
        icon="🗺️",
        title="Clusters & Sites",
        metric1_label="Clusters",
        metric1_value=str(metrics['clusters_count']),
        metric1_color="var(--info, #3182CE)",
        metric2_label="Total Sites",
        metric2_value=str(metrics['sites_count']),
        metric2_color="var(--brand-primary, #3182CE)"
    )
    cards.append(card1)
    
    # Card 2: Active Sites (green) and Inactive Sites (red)
    card2 = create_dual_metric_card(
        icon="🏭",
        title="Site Status",
        metric1_label="Active Sites",
        metric1_value=str(metrics['active_sites']),
        metric1_color="var(--success, #38A169)",
        metric2_label="Inactive Sites",
        metric2_value=str(metrics['inactive_sites']),
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card2)
    
    # Card 3: Planned Machines and Deployed Machines
    card3 = create_dual_metric_card(
        icon="🚛",
        title="Machines",
        metric1_label="Planned",
        metric1_value=str(metrics['planned_machines']),
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Deployed",
        metric2_value=str(metrics['deployed_machines']),
        metric2_color="var(--success, #38A169)"
    )
    cards.append(card3)
    
    # Card 4: Sites Not on Track and Critical Sites - IMPROVED ALIGNMENT
    card4 = create_dual_metric_card(
        icon="⚠️",
        title="Issues",
        metric1_label="Not on Track",
        metric1_value=str(metrics['sites_not_on_track']),
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Critical",
        metric2_value=str(metrics['critically_lagging']),
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card4)
    
    # Cards 5-8: Empty placeholders
    for i in range(5, 9):
        cards.append(create_empty_card(i))
    
    return cards

def create_agency_header(current_agency_display):
    """Create agency header with full display name"""
    today = datetime.now().strftime("%d %B %Y")
    
    return html.Div(
        className="agency-header",
        children=[
            html.H1(current_agency_display, className="agency-title"),
            html.P(f"Real-time Dashboard - {today}", className="agency-date")
        ]
    )

def create_hero_section():
    """Create hero section with main system title"""
    return html.Div(
        className="hero-section",
        children=[
            html.Div(
                className="hero-content",
                children=[
                    # Left Logo
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "justifyContent": "center", "height": "100%", "flexShrink": "0"},
                        children=[
                            html.Img(
                                src="/assets/img/left.png",
                                alt="Left Organization Logo",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(40px, 8vh, 60px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            )
                        ]
                    ),
                    
                    # Title Section
                    html.Div(
                        className="hero-title-section",
                        style={
                            "textAlign": "center", "flex": "1", "padding": "0 clamp(1rem, 3vw, 2rem)",
                            "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center", "height": "100%"
                        },
                        children=[
                            html.H1(
                                "Swaccha Andhra Corporation",
                                className="hero-title",
                                style={
                                    "margin": "0", "padding": "0", "fontSize": "clamp(1.5rem, 4vw, 2.5rem)",
                                    "fontWeight": "800", "lineHeight": "1.1", "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)", "letterSpacing": "-0.5px"
                                }
                            ),
                            html.P(
                                "Real Time Legacy Waste Remediation Progress Tracker",
                                className="hero-subtitle",
                                style={
                                    "margin": "0.25rem 0 0 0", "padding": "0", "fontSize": "clamp(0.8rem, 1.8vw, 1rem)",
                                    "fontWeight": "500", "lineHeight": "1.3", "opacity": "0.9", "textAlign": "center"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "justifyContent": "center", "height": "100%", "flexShrink": "0"},
                        children=[
                            html.Img(
                                src="/assets/img/right.png",
                                alt="Right Organization Logo",
                                className="responsive-logo",
                                style={
                                    "height": "clamp(40px, 8vh, 60px)",
                                    "width": "auto",
                                    "objectFit": "contain",
                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))",
                                    "transition": "all 0.3s ease"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def build_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """Build the public layout with specific card structure"""
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        className="public-layout",
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
            dcc.Interval(id='auto-rotation-interval', interval=15*1000, n_intervals=0),
            create_hover_overlay_banner(theme_name),
            html.Div(
                className="main-content",
                children=[
                    create_hero_section(),
                    html.Div(id="agency-header-container"),
                    html.Div(id="dynamic-cards-container", className="cards-grid")
                ]
            )
        ]
    )

@callback(
    [Output('agency-header-container', 'children'), Output('dynamic-cards-container', 'children')],
    [Input('auto-rotation-interval', 'n_intervals'), Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_agency_dashboard(n_intervals, theme_name):
    """Update dashboard with specific card layout"""
    try:
        logger.info(f"🔄 Agency rotation update #{n_intervals}")
        
        df = load_agency_data()
        rotation_data = get_agency_rotation_data(df, n_intervals)
        current_agency_key = rotation_data['current_agency_key']
        current_agency_display = rotation_data['current_agency_display']
        agency_data = rotation_data['agency_data']
        
        logger.info(f"🏢 Displaying: {current_agency_display} (Records: {len(agency_data)})")
        
        metrics = calculate_agency_metrics(agency_data)
        theme_styles = get_theme_styles(theme_name or 'dark')
        
        header = create_agency_header(current_agency_display)
        cards = create_specific_metric_cards(current_agency_display, metrics, theme_styles)
        
        logger.info(f"✅ Created {len(cards)} specific cards for {current_agency_display}")
        
        return header, cards
        
    except Exception as e:
        logger.error(f"❌ Error in dashboard update: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error state
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
                        html.Div("Error", className="metric-title"),
                        html.Div("--", className="metric-value"),
                        html.Div(f"card {i+1}", className="metric-unit")
                    ]
                )
            )
        
        return fallback_header, fallback_cards

# Export functions
__all__ = [
    'build_public_layout',
    'load_agency_data',
    'get_agency_rotation_data',
    'calculate_agency_metrics',
    'create_specific_metric_cards',
    'get_display_agency_name',
    'AGENCY_NAMES'
]