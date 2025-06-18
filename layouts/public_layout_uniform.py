# layouts/public_layout_uniform.py
"""
Updated layout with specific card content and uniform sizing - ENHANCED VERSION WITH NEW METRICS
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import numpy as np
from datetime import datetime, timedelta

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

# Initialize logger FIRST
logger = logging.getLogger(__name__)

# AGENCY NAMES MAPPING
AGENCY_NAMES = {
    'Zigma': 'Zigma Global Enviro Solutions Private Limited, Erode',
    'Saurashtra': 'Saurastra Enviro Pvt Ltd, Gujarat', 
    'Tharuni': 'Tharuni Associates, Guntur'
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
        total_quantity = np.random.randint(100, 1000)
        remediated_quantity = np.random.randint(0, int(total_quantity * 0.8))  # Max 80% completion
        
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
            'Quantity to be remediated in MT': total_quantity,
            'Cumulative Quantity remediated till date in MT': remediated_quantity,
            'Active_site': np.random.choice(['yes', 'no']),
            'net_to_be_remediated_mt': total_quantity - remediated_quantity,
            'days_required': np.random.uniform(30, 120)
        })
    
    df = pd.DataFrame(data)
    logger.info(f"📊 Created sample data with agencies: {list(df['Agency'].unique())}")
    return df


def calculate_cluster_completion_rates(agency_data):
    """Calculate completion rate for each cluster in the agency"""
    cluster_rates = []
    print("@@@@@@@@@@@@@@@@@@",agency_data.columns)
    if agency_data.empty or 'Cluster' not in agency_data.columns:
        return cluster_rates
    
    try:
        # Required columns
        required_cols = ['Agency','Cluster', 'Site', 'Quantity to be remediated in MT','Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for cluster calculation")
            return cluster_rates
        
        # Group by cluster and get unique sites within each cluster
        for cluster_name in agency_data['Cluster'].unique():
            cluster_data = agency_data[agency_data['Cluster'] == cluster_name]
            
            # Get unique sites in this cluster (to avoid double counting)
            unique_sites = cluster_data.drop_duplicates(subset=['Site'])
            
            # Calculate totals for this cluster
            total_to_remediate = unique_sites['Quantity to be remediated in MT'].sum()
            total_remediated = unique_sites['Cumulative Quantity remediated till date in MT'].sum()
            
            # Calculate completion percentage
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = round(completion_rate, 1)  # Round to 1 decimal
            else:
                completion_rate = 0
            
            cluster_rates.append({
                'cluster': cluster_name,
                'completion_rate': completion_rate,
                'total_to_remediate': total_to_remediate,
                'total_remediated': total_remediated
            })
        
        # Sort by completion rate (highest first)
        cluster_rates.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        logger.info(f"📊 Calculated completion rates for {len(cluster_rates)} clusters")
        for cluster in cluster_rates:
            logger.info(f"  {cluster['cluster']}: {cluster['completion_rate']}% ({cluster['total_remediated']}/{cluster['total_to_remediate']} MT)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating cluster completion rates: {e}")
        cluster_rates = []
    
    return cluster_rates

def create_cluster_progress_card(current_agency_display, agency_data):
    """Create Card 5: Cluster Progress with list of clusters and completion rates"""
    
    cluster_rates = calculate_cluster_completion_rates(agency_data)
    
    # Create cluster list items
    cluster_items = []
    
    if not cluster_rates:
        # No data available
        cluster_items.append(
            html.Div(
                "No cluster data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        for cluster_info in cluster_rates:
            cluster_name = cluster_info['cluster']
            completion_rate = cluster_info['completion_rate']
            
            # Color coding based on completion rate
            if completion_rate >= 75:
                color = "var(--success, #38A169)"
            elif completion_rate >= 50:
                color = "var(--warning, #DD6B20)"
            elif completion_rate >= 25:
                color = "var(--info, #3182CE)"
            else:
                color = "var(--error, #E53E3E)"
            
            cluster_items.append(
                html.Div(
                    className="cluster-progress-item",
                    children=[
                        html.Div(
                            f"{cluster_name}:",
                            className="cluster-name"
                        ),
                        html.Div(
                            f"{completion_rate}%",
                            className="cluster-percentage",
                            style={"color": color}
                        )
                    ]
                )
            )
    
    return html.Div(
        className="enhanced-metric-card cluster-progress-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("📈", className="card-icon"),
                    html.H3("Cluster Progress", className="card-title")
                ]
            ),
            
            # Cluster List Container
            html.Div(
                className="cluster-progress-content",
                children=[
                    # html.Div(
                    #     className="agency-label",
                    #     children=f"Agency: {current_agency_display.split(',')[0]}"  # Show short name
                    # ),
                    html.Div(
                        className="cluster-list",
                        children=cluster_items
                    )
                ]
            )
        ]
    )

def calculate_site_completion_rates(agency_data):
    """Calculate completion rate for each site in the agency"""
    site_rates = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return site_rates
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for site calculation")
            return site_rates
        
        # Group by site (each site should be unique anyway, but just in case)
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            total_to_remediate = site_data['Quantity to be remediated in MT'] if pd.notna(site_data['Quantity to be remediated in MT']) else 0
            total_remediated = site_data['Cumulative Quantity remediated till date in MT'] if pd.notna(site_data['Cumulative Quantity remediated till date in MT']) else 0
            
            # Calculate completion percentage
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = round(completion_rate, 1)  # Round to 1 decimal
            else:
                completion_rate = 0
            
            site_rates.append({
                'site': site_name,
                'cluster': cluster_name,
                'completion_rate': completion_rate,
                'total_to_remediate': total_to_remediate,
                'total_remediated': total_remediated
            })
        
        # Sort by completion rate (highest first) - DESCENDING ORDER
        site_rates.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        logger.info(f"📊 Calculated completion rates for {len(site_rates)} sites")
        for site in site_rates[:5]:  # Log top 5 for debugging
            logger.info(f"  {site['site']} ({site['cluster']}): {site['completion_rate']}% ({site['total_remediated']}/{site['total_to_remediate']} MT)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating site completion rates: {e}")
        site_rates = []
    
    return site_rates

def create_site_progress_card(current_agency_display, agency_data):
    """Create Card 6: Site Progress with list of sites and completion rates"""
    
    site_rates = calculate_site_completion_rates(agency_data)
    
    # Create site list items
    site_items = []
    
    if not site_rates:
        # No data available
        site_items.append(
            html.Div(
                "No site data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        # Limit to top 8 sites to fit in the card (can be scrollable)
        display_sites = site_rates[:8] if len(site_rates) > 8 else site_rates
        
        for site_info in display_sites:
            site_name = site_info['site']
            cluster_name = site_info['cluster']
            completion_rate = site_info['completion_rate']
            
            # Color coding based on completion rate (same as cluster card)
            if completion_rate >= 75:
                color = "var(--success, #38A169)"
            elif completion_rate >= 50:
                color = "var(--warning, #DD6B20)"
            elif completion_rate >= 25:
                color = "var(--info, #3182CE)"
            else:
                color = "var(--error, #E53E3E)"
            
            # Truncate long site names for display
            display_site_name = site_name if len(site_name) <= 20 else f"{site_name[:17]}..."
            
            site_items.append(
                html.Div(
                    className="site-progress-item",
                    children=[
                        html.Div(
                            className="site-info",
                            children=[
                                html.Div(
                                    f"{display_site_name}",
                                    className="site-name",
                                    title=site_name  # Full name on hover
                                ),
                                html.Div(
                                    f"({cluster_name})",
                                    className="site-cluster"
                                )
                            ]
                        ),
                        html.Div(
                            f"{completion_rate}%",
                            className="site-percentage",
                            style={"color": color}
                        )
                    ]
                )
            )
        
        # Add "and X more" if there are more sites
        if len(site_rates) > 8:
            remaining_count = len(site_rates) - 8
            site_items.append(
                html.Div(
                    f"... and {remaining_count} more sites",
                    className="more-sites-indicator",
                    style={
                        "textAlign": "center",
                        "color": "var(--text-secondary)",
                        "fontStyle": "italic",
                        "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
                        "padding": "clamp(0.5rem, 1vh, 0.75rem)"
                    }
                )
            )
    
    return html.Div(
        className="enhanced-metric-card site-progress-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("🏗️", className="card-icon"),
                    html.H3("Site Progress", className="card-title")
                ]
            ),
            
            # Site List Container
            html.Div(
                className="site-progress-content",
                children=[
                    # html.Div(
                    #     className="agency-label",
                    #     children=f"Agency: {current_agency_display.split(',')[0]}"  # Show short name
                    # ),
                    html.Div(
                        className="site-list",
                        children=site_items
                    )
                ]
            )
        ]
    )

# Update the create_specific_metric_cards function to use the new Card 5
def create_specific_metric_cards_updated(current_agency_display, metrics, theme_styles, agency_data):
    """Create all 8 cards with the updated Card 5"""
    cards = []
    
    # Card 1: Clusters and Total Sites
    card1 = create_dual_metric_card(
        icon="🗺️",
        title="Clusters & Sites",
        metric1_label="Clusters",
        metric1_value=metrics['clusters_count'],
        metric1_color="var(--info, #3182CE)",
        metric2_label="Total Sites",
        metric2_value=metrics['sites_count'],
        metric2_color="var(--brand-primary, #3182CE)"
    )
    cards.append(card1)
    
    # Card 2: Active Sites (green) and Inactive Sites (red)
    card2 = create_dual_metric_card(
        icon="🏭",
        title="Site Status",
        metric1_label="Active Sites",
        metric1_value=metrics['active_sites'],
        metric1_color="var(--success, #38A169)",
        metric2_label="Inactive Sites",
        metric2_value=metrics['inactive_sites'],
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card2)
    
    # Card 3: Sites Not on Track and Critical Sites
    card3 = create_dual_metric_card(
        icon="⚠️",
        title="Issues",
        metric1_label="Off Track",
        metric1_value=metrics['sites_not_on_track'],
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Critical",
        metric2_value=metrics['critically_lagging'],
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card3)
    
    # Card 4: Planned Machines and Deployed Machines
    card4 = create_dual_metric_card(
        icon="🚛",
        title="Machines",
        metric1_label="Planned",
        metric1_value=metrics['planned_machines'],
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Deployed",
        metric2_value=metrics['deployed_machines'],
        metric2_color="var(--success, #38A169)"
    )
    cards.append(card4)
    
    # Card 5: Cluster Progress (NEW LIST STYLE)
    card5 = create_cluster_progress_card(current_agency_display, agency_data)
    cards.append(card5)
    
    # Cards 6-8: Placeholders for now
    for i in range(6, 9):
        cards.append(create_empty_card(i))
    
    return cards


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
    """Calculate metrics for current agency including new cluster completion rate"""
    if agency_data.empty:
        return {
            'clusters_count': 0,
            'sites_count': 0,
            'active_sites': 0,
            'inactive_sites': 0,
            'planned_machines': 0,
            'deployed_machines': 0,
            'sites_not_on_track': 0,
            'critically_lagging': 0,
            'avg_cluster_completion': 0,
            'best_cluster_completion': 0,
            'total_capacity': 0,
            'avg_daily_capacity': 0,
            'total_planned_quantity': 0,
            'total_remediated_quantity': 0,
            'overall_completion_rate': 0,
            'remaining_quantity': 0
        }
    
    try:
        today = datetime.now().date()
        sept_30 = datetime(2024, 9, 30).date()
        
        # Original metrics
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
        
        # NEW METRICS - Card 5: Cluster Completion Rate
        avg_cluster_completion = 0
        best_cluster_completion = 0
        
        if all(col in agency_data.columns for col in ['Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
            cluster_metrics = agency_data.groupby('Cluster').agg({
                'Quantity to be remediated in MT': 'sum',
                'Cumulative Quantity remediated till date in MT': 'sum'
            }).reset_index()
            
            # Calculate completion rate for each cluster
            cluster_metrics['completion_rate'] = (
                cluster_metrics['Cumulative Quantity remediated till date in MT'] / 
                cluster_metrics['Quantity to be remediated in MT'] * 100
            ).fillna(0)
            
            # Round to 1 decimal place for display
            cluster_metrics['completion_rate'] = cluster_metrics['completion_rate'].round(1)
            
            avg_cluster_completion = cluster_metrics['completion_rate'].mean()
            best_cluster_completion = cluster_metrics['completion_rate'].max()
            
            # Round final values
            avg_cluster_completion = round(avg_cluster_completion, 1) if not pd.isna(avg_cluster_completion) else 0
            best_cluster_completion = round(best_cluster_completion, 1) if not pd.isna(best_cluster_completion) else 0
        
        # NEW METRICS - Card 6: Daily Capacity
        total_capacity = 0
        avg_daily_capacity = 0
        
        if 'Daily_Capacity' in agency_data.columns:
            total_capacity = agency_data['Daily_Capacity'].sum()
            avg_daily_capacity = agency_data['Daily_Capacity'].mean()
            
            total_capacity = round(total_capacity, 0)
            avg_daily_capacity = round(avg_daily_capacity, 1) if not pd.isna(avg_daily_capacity) else 0
        
        # NEW METRICS - Card 7: Overall Progress
        total_planned_quantity = 0
        total_remediated_quantity = 0
        overall_completion_rate = 0
        
        if all(col in agency_data.columns for col in ['Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']):
            total_planned_quantity = agency_data['Quantity to be remediated in MT'].sum()
            total_remediated_quantity = agency_data['Cumulative Quantity remediated till date in MT'].sum()
            
            if total_planned_quantity > 0:
                overall_completion_rate = (total_remediated_quantity / total_planned_quantity * 100)
                overall_completion_rate = round(overall_completion_rate, 1)
        
        # NEW METRICS - Card 8: Remaining Work
        remaining_quantity = total_planned_quantity - total_remediated_quantity
        remaining_quantity = max(0, remaining_quantity)  # Ensure non-negative
        
        return {
            'clusters_count': clusters_count,
            'sites_count': sites_count,
            'active_sites': active_sites,
            'inactive_sites': inactive_sites,
            'planned_machines': planned_machines,
            'deployed_machines': deployed_machines,
            'sites_not_on_track': sites_not_on_track,
            'critically_lagging': critically_lagging,
            'avg_cluster_completion': avg_cluster_completion,
            'best_cluster_completion': best_cluster_completion,
            'total_capacity': int(total_capacity),
            'avg_daily_capacity': avg_daily_capacity,
            'total_planned_quantity': int(total_planned_quantity),
            'total_remediated_quantity': int(total_remediated_quantity),
            'overall_completion_rate': overall_completion_rate,
            'remaining_quantity': int(remaining_quantity)
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
            'critically_lagging': 0,
            'avg_cluster_completion': 0,
            'best_cluster_completion': 0,
            'total_capacity': 0,
            'avg_daily_capacity': 0,
            'total_planned_quantity': 0,
            'total_remediated_quantity': 0,
            'overall_completion_rate': 0,
            'remaining_quantity': 0
        }

def create_dual_metric_card(icon, title, metric1_label, metric1_value, metric1_color, metric2_label, metric2_value, metric2_color):
    """Create a card with two metrics side by side with enhanced design and clean structure"""
    return html.Div(
        className="enhanced-metric-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div(icon, className="card-icon"),
                    html.H3(title, className="card-title")
                ]
            ),
            
            # Metrics Container
            html.Div(
                className="metrics-container",
                children=[
                    # First metric
                    html.Div(
                        className="metric-display primary",
                        children=[
                            html.Div(
                                str(metric1_value),
                                className="metric-number",
                                style={"color": metric1_color}
                            ),
                            html.Div(
                                metric1_label,
                                className="metric-label"
                            )
                        ]
                    ),
                    
                    # Visual Separator
                    html.Div(className="metrics-separator"),
                    
                    # Second metric
                    html.Div(
                        className="metric-display secondary",
                        children=[
                            html.Div(
                                str(metric2_value),
                                className="metric-number",
                                style={"color": metric2_color}
                            ),
                            html.Div(
                                metric2_label,
                                className="metric-label"
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
        className="enhanced-metric-card placeholder-card",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.Div("📊", className="card-icon placeholder-icon"),
                    html.H3(f"Card {card_number}", className="card-title placeholder-title")
                ]
            ),
            html.Div(
                className="placeholder-content",
                children=[
                    html.Div("Coming Soon", className="placeholder-text"),
                    html.Div("More metrics will be added here", className="placeholder-subtext")
                ]
            )
        ]
    )



# And update your callback function to pass agency_data:

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
    """Build the public layout with enhanced card structure"""
    theme_styles = get_theme_styles(theme_name)
    
    # DEBUG: Check if assets folder exists
    assets_path = "assets/css/uniform_cards.css"
    css_exists = os.path.exists(assets_path)
    logger.info(f"🔍 CSS Debug: uniform_cards.css exists at {assets_path}: {css_exists}")
    
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
            # Enhanced CSS Loading with timestamp to force refresh
            html.Link(
                rel="stylesheet",
                href=f"/assets/css/uniform_cards.css?v={int(datetime.now().timestamp())}"
            ),
            
            dcc.Interval(id='auto-rotation-interval', interval=15*1000, n_intervals=0),
            dcc.Store(id='current-theme', data=theme_name),
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

# Replace your existing create_specific_metric_cards function with this:

def create_specific_metric_cards(current_agency_display, metrics, theme_styles, agency_data=None):
    """Create all 8 cards including Cluster Progress (Card 5), Site Progress (Card 6), and Lagging Sites (Card 7)"""
    cards = []
    
    # Card 1: Clusters and Total Sites
    card1 = create_dual_metric_card(
        icon="🗺️",
        title="Clusters & Sites",
        metric1_label="Clusters",
        metric1_value=metrics['clusters_count'],
        metric1_color="var(--info, #3182CE)",
        metric2_label="Total Sites",
        metric2_value=metrics['sites_count'],
        metric2_color="var(--brand-primary, #3182CE)"
    )
    cards.append(card1)
    
    # Card 2: Active Sites (green) and Inactive Sites (red)
    card2 = create_dual_metric_card(
        icon="🏭",
        title="Site Status",
        metric1_label="Active Sites",
        metric1_value=metrics['active_sites'],
        metric1_color="var(--success, #38A169)",
        metric2_label="Inactive Sites",
        metric2_value=metrics['inactive_sites'],
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card2)
    
    # Card 3: Sites Not on Track and Critical Sites
    card3 = create_dual_metric_card(
        icon="⚠️",
        title="Issues",
        metric1_label="Off Track",
        metric1_value=metrics['sites_not_on_track'],
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Critical",
        metric2_value=metrics['critically_lagging'],
        metric2_color="var(--error, #E53E3E)"
    )
    cards.append(card3)
    
    # Card 4: Planned Machines and Deployed Machines
    card4 = create_dual_metric_card(
        icon="🚛",
        title="Machines",
        metric1_label="Planned",
        metric1_value=metrics['planned_machines'],
        metric1_color="var(--warning, #DD6B20)",
        metric2_label="Deployed",
        metric2_value=metrics['deployed_machines'],
        metric2_color="var(--success, #38A169)"
    )
    cards.append(card4)
    
    # Card 5: Cluster Progress (LIST STYLE)
    if agency_data is not None and not agency_data.empty:
        card5 = create_cluster_progress_card(current_agency_display, agency_data)
    else:
        card5 = create_empty_card(5)
    cards.append(card5)
    
    # Card 6: Site Progress (LIST STYLE)
    if agency_data is not None and not agency_data.empty:
        card6 = create_site_progress_card(current_agency_display, agency_data)
    else:
        card6 = create_empty_card(6)
    cards.append(card6)
    
    # Card 7: Lagging Sites (LIST STYLE) - NEW
    if agency_data is not None and not agency_data.empty:
        card7 = create_lagging_sites_card(current_agency_display, agency_data)
    else:
        card7 = create_empty_card(7)
    cards.append(card7)
    
    # Card 8: Placeholder for now
    if agency_data is not None and not agency_data.empty:
        card8 = create_performance_rankings_card(current_agency_display, agency_data)
    else:
        card8 = create_empty_card(8)
    cards.append(card8)
    
    return cards


@callback(
    [Output('agency-header-container', 'children'), Output('dynamic-cards-container', 'children')],
    [Input('auto-rotation-interval', 'n_intervals'), Input('current-theme', 'data')],
    prevent_initial_call=False
)
def update_agency_dashboard(n_intervals, theme_name):
    """Update dashboard with enhanced card layout including lagging sites analysis"""
    try:
        logger.info(f"🔄 Agency rotation update #{n_intervals}")
        
        df = load_agency_data()
        rotation_data = get_agency_rotation_data(df, n_intervals)
        current_agency_key = rotation_data['current_agency_key']
        current_agency_display = rotation_data['current_agency_display']
        agency_data = rotation_data['agency_data']
        
        logger.info(f"🏢 Displaying: {current_agency_display} (Records: {len(agency_data)})")
        
        # Calculate metrics and log lagging sites summary
        metrics = calculate_agency_metrics(agency_data)
        
        if not agency_data.empty:
            try:
                lagging_sites = calculate_lagging_sites(agency_data)
                logger.info(f"🚨 Lagging Sites Summary: {len(lagging_sites)} sites cannot complete before Sept 30, 2025")
            except Exception as lagging_error:
                logger.warning(f"⚠️ Could not calculate lagging sites: {lagging_error}")
        
        theme_styles = get_theme_styles(theme_name or 'dark')
        
        header = create_agency_header(current_agency_display)
        
        # Pass agency_data to create all progress cards
        cards = create_specific_metric_cards(current_agency_display, metrics, theme_styles, agency_data)
        
        logger.info(f"✅ Created {len(cards)} cards including performance rankings for {current_agency_display}")
        
        # Return exactly 2 values as expected by the callback outputs
        return header, cards
        
    except Exception as e:
        logger.error(f"❌ Error in dashboard update: {e}")
        import traceback
        traceback.print_exc()
        
        # Create fallback content - ALWAYS return exactly 2 values
        try:
            fallback_header = html.Div(
                "Error Loading Agency Data",
                className="agency-header",
                style={'color': 'red', 'textAlign': 'center', 'padding': '1rem'}
            )
            
            fallback_cards = []
            for i in range(8):
                fallback_cards.append(create_empty_card(i + 1))
            
            # Return exactly 2 values
            return fallback_header, fallback_cards
            
        except Exception as fallback_error:
            logger.error(f"❌ Error creating fallback content: {fallback_error}")
            
            # Ultimate fallback - simple HTML elements, exactly 2 values
            simple_header = html.Div("System Error", style={'color': 'red', 'padding': '1rem'})
            simple_cards = [html.Div("Loading...", style={'padding': '1rem'}) for _ in range(8)]
            
            # Return exactly 2 values
            return simple_header, simple_cards



def calculate_lagging_sites(agency_data):
    """Calculate sites that cannot be completed before September 30, 2025 based on days_required"""
    lagging_sites = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return lagging_sites
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'days_required']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for lagging sites calculation")
            return lagging_sites
        
        # Calculate days until September 30, 2025
        today = datetime.now().date()
        sept_30 = datetime(2025, 9, 30).date()
        days_until_sept30 = (sept_30 - today).days
        
        logger.info(f"📅 Days until Sept 30, 2025: {days_until_sept30}")
        
        # Process each site
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            days_required = site_data['days_required'] if pd.notna(site_data['days_required']) else None
            
            # Skip sites with blank/NULL days_required
            if days_required is None or days_required == '' or str(days_required).strip() == '':
                logger.debug(f"⏭️ Skipping {site_name} - days_required is blank/NULL")
                continue
            
            # Convert days_required to numeric if it's a string
            try:
                days_required = float(days_required)
                # Skip if days_required is 0 or negative
                if days_required <= 0:
                    logger.debug(f"⏭️ Skipping {site_name} - days_required is {days_required}")
                    continue
            except (ValueError, TypeError):
                logger.debug(f"⏭️ Skipping {site_name} - cannot convert days_required '{days_required}' to number")
                continue
            
            # Simple logic: if days_required > days_until_sept30, then it's lagging
            if days_required > days_until_sept30:
                days_overdue = days_required - days_until_sept30
                
                # Get additional details for display
                active_status = site_data.get('Active_site', 'unknown')
                
                lagging_sites.append({
                    'site': site_name,
                    'cluster': cluster_name,
                    'days_required': round(days_required, 1),
                    'days_until_sept30': days_until_sept30,
                    'days_overdue': round(days_overdue, 1),
                    'active_status': active_status.lower() if isinstance(active_status, str) else 'unknown'
                })
        
        # Sort by days_overdue (most critical first - highest overdue days)
        lagging_sites.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        logger.info(f"🚨 Found {len(lagging_sites)} lagging sites (cannot complete before Sept 30, 2025)")
        for site in lagging_sites[:3]:  # Log top 3 for debugging
            logger.info(f"  {site['site']} ({site['cluster']}): needs {site['days_required']} days, only {site['days_until_sept30']} available (overdue by {site['days_overdue']} days)")
        
    except Exception as e:
        logger.error(f"❌ Error calculating lagging sites: {e}")
        lagging_sites = []
    
    return lagging_sites

def create_lagging_sites_card(current_agency_display, agency_data):
    """Create Card 7: Lagging Sites with list of sites that can't complete before Sept 30, 2025"""
    
    lagging_sites = calculate_lagging_sites(agency_data)
    
    # Create lagging sites list items
    site_items = []
    
    if not lagging_sites:
        # No lagging sites - good news!
        site_items.append(
            html.Div(
                children=[
                    html.Div(
                        "🎉 All sites on track!",
                        style={
                            "textAlign": "center",
                            "color": "var(--success, #38A169)",
                            "fontWeight": "600",
                            "fontSize": "clamp(1rem, 2vh, 1.2rem)",
                            "padding": "1rem"
                        }
                    ),
                    html.Div(
                        "No sites are lagging behind schedule for October 2nd, 2025",
                        style={
                            "textAlign": "center",
                            "color": "var(--text-secondary)",
                            "fontStyle": "italic",
                            "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)"
                        }
                    )
                ]
            )
        )
    else:
        # Limit to top 8 lagging sites to fit in the card
        display_sites = lagging_sites[:8] if len(lagging_sites) > 8 else lagging_sites
        
        for site_info in display_sites:
            site_name = site_info['site']
            cluster_name = site_info['cluster']
            days_overdue = site_info['days_overdue']
            days_required = site_info['days_required']
            active_status = site_info['active_status']
            
            # Color coding based on severity (days overdue)
            if days_overdue >= 60:
                color = "var(--error, #E53E3E)"  # Critical - Red
                urgency_icon = "🔴"
            elif days_overdue >= 30:
                color = "var(--warning, #DD6B20)"  # High - Orange
                urgency_icon = "🟠"
            elif days_overdue >= 15:
                color = "#FFA500"  # Medium - Yellow/Orange
                urgency_icon = "🟡"
            else:
                color = "var(--info, #3182CE)"  # Low - Blue
                urgency_icon = "🔵"
            
            # Status indicator
            status_indicator = ""
            if active_status == 'yes':
                status_indicator = "🟢"  # Active
            elif active_status == 'no':
                status_indicator = "⚫"  # Inactive
            else:
                status_indicator = "❓"  # Unknown
            
            # Truncate long site names for display
            display_site_name = site_name if len(site_name) <= 18 else f"{site_name[:15]}..."
            
            site_items.append(
                html.Div(
                    className="lagging-site-item",
                    children=[
                        html.Div(
                            className="lagging-site-info",
                            children=[
                                html.Div(
                                    className="lagging-site-header",
                                    children=[
                                        html.Span(urgency_icon, className="urgency-icon"),
                                        html.Span(status_indicator, className="status-icon"),
                                        html.Div(
                                            f"{display_site_name}",
                                            className="lagging-site-name",
                                            title=f"{site_name} - needs {days_required} days"
                                        )
                                    ]
                                ),
                                html.Div(
                                    f"({cluster_name})",
                                    className="lagging-site-cluster"
                                )
                            ]
                        ),
                        html.Div(
                            f"+{days_overdue}d",
                            className="lagging-days-overdue",
                            style={"color": color},
                            title=f"{days_overdue} days overdue"
                        )
                    ]
                )
            )
        
        # Add "and X more" if there are more lagging sites
        if len(lagging_sites) > 8:
            remaining_count = len(lagging_sites) - 8
            site_items.append(
                html.Div(
                    f"... and {remaining_count} more lagging sites",
                    className="more-lagging-sites-indicator",
                    style={
                        "textAlign": "center",
                        "color": "var(--error, #E53E3E)",
                        "fontWeight": "600",
                        "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
                        "padding": "clamp(0.5rem, 1vh, 0.75rem)"
                    }
                )
            )
    
    # Calculate summary stats
    total_lagging = len(lagging_sites)
    
    return html.Div(
        className="enhanced-metric-card lagging-sites-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("🚨", className="card-icon"),
                    html.H3("Lagging Sites", className="card-title")
                ]
            ),
            
            # Lagging Sites List Container
            html.Div(
                className="lagging-sites-content",
                children=[
                    html.Div(
                        className="agency-label",
                        children="Sites at risk"
                    ),
                    html.Div(
                        className="lagging-sites-list",
                        children=site_items
                    )
                ]
            )
        ]
    )

def calculate_performance_rankings(agency_data):
    """Calculate performance rankings for sites based on completion rate and timeline performance"""
    performance_sites = []
    
    if agency_data.empty or 'Site' not in agency_data.columns:
        return performance_sites
    
    try:
        # Required columns
        required_cols = ['Site', 'Cluster', 'Quantity to be remediated in MT', 'Cumulative Quantity remediated till date in MT']
        if not all(col in agency_data.columns for col in required_cols):
            logger.warning(f"Missing required columns for performance rankings calculation")
            return performance_sites
        
        # Calculate days until September 30, 2025
        today = datetime.now().date()
        sept_30 = datetime(2025, 9, 30).date()
        days_until_sept30 = (sept_30 - today).days
        
        # Process each site
        for site_name in agency_data['Site'].unique():
            site_data = agency_data[agency_data['Site'] == site_name].iloc[0]  # Take first record for this site
            
            # Get site details
            cluster_name = site_data['Cluster'] if 'Cluster' in site_data and pd.notna(site_data['Cluster']) else 'Unknown'
            total_to_remediate = site_data.get('Quantity to be remediated in MT', 0)
            total_remediated = site_data.get('Cumulative Quantity remediated till date in MT', 0)
            days_required = site_data.get('days_required', 0)
            active_status = site_data.get('Active_site', 'unknown')
            
            # Skip sites with no meaningful data
            if pd.isna(total_to_remediate) or total_to_remediate <= 0:
                continue
                
            # Calculate completion rate
            completion_rate = 0
            if total_to_remediate > 0:
                completion_rate = (total_remediated / total_to_remediate) * 100
                completion_rate = max(0, min(100, completion_rate))  # Clamp between 0-100
            
            # Calculate timeline performance (days ahead/behind)
            timeline_performance = 0
            days_ahead_behind = 0
            
            if pd.notna(days_required) and days_required > 0:
                try:
                    days_required_float = float(days_required)
                    days_ahead_behind = days_until_sept30 - days_required_float
                    
                    # Timeline performance score (0-100 scale)
                    if days_ahead_behind >= 0:
                        # Ahead of schedule - bonus points
                        timeline_performance = min(100, 50 + (days_ahead_behind / 2))
                    else:
                        # Behind schedule - penalty
                        timeline_performance = max(0, 50 + (days_ahead_behind / 2))
                        
                except (ValueError, TypeError):
                    timeline_performance = 50  # Neutral score if can't calculate
            else:
                timeline_performance = 50  # Neutral score for missing data
            
            # Calculate composite performance score
            # 60% weight on completion rate, 40% weight on timeline performance
            composite_score = (completion_rate * 0.6) + (timeline_performance * 0.4)
            
            # Only include sites with meaningful performance (>5% completion or active)
            is_active = str(active_status).lower() == 'yes'
            has_progress = completion_rate > 5
            
            if has_progress or is_active:
                performance_sites.append({
                    'site': site_name,
                    'cluster': cluster_name,
                    'completion_rate': round(completion_rate, 1),
                    'days_ahead_behind': round(days_ahead_behind, 1),
                    'timeline_performance': round(timeline_performance, 1),
                    'composite_score': round(composite_score, 1),
                    'active_status': active_status,
                    'total_to_remediate': total_to_remediate,
                    'total_remediated': total_remediated
                })
        
        # Sort by composite score (highest first - best performers)
        performance_sites.sort(key=lambda x: x['composite_score'], reverse=True)
        
        logger.info(f"🏆 Calculated performance rankings for {len(performance_sites)} sites")
        for i, site in enumerate(performance_sites[:3]):  # Log top 3 for debugging
            rank = i + 1
            logger.info(f"  #{rank}: {site['site']} ({site['cluster']}) - Score: {site['composite_score']}, Completion: {site['completion_rate']}%, Timeline: {site['days_ahead_behind']}d")
        
    except Exception as e:
        logger.error(f"❌ Error calculating performance rankings: {e}")
        performance_sites = []
    
    return performance_sites

def create_performance_rankings_card(current_agency_display, agency_data):
    """Create Card 8: Performance Rankings with list of top performing sites"""
    
    performance_sites = calculate_performance_rankings(agency_data)
    
    # Create performance rankings list items
    ranking_items = []
    
    if not performance_sites:
        # No performance data available
        ranking_items.append(
            html.Div(
                "No performance data available",
                style={
                    "textAlign": "center",
                    "color": "var(--text-secondary)",
                    "fontStyle": "italic",
                    "padding": "1rem"
                }
            )
        )
    else:
        # Limit to top 8 performers to fit in the card
        display_sites = performance_sites[:8] if len(performance_sites) > 8 else performance_sites
        
        for i, site_info in enumerate(display_sites):
            rank = i + 1
            site_name = site_info['site']
            cluster_name = site_info['cluster']
            completion_rate = site_info['completion_rate']
            days_ahead_behind = site_info['days_ahead_behind']
            composite_score = site_info['composite_score']
            active_status = site_info['active_status']
            
            # Medal/ranking icons
            if rank == 1:
                rank_icon = "🥇"
                rank_color = "#FFD700"  # Gold
            elif rank == 2:
                rank_icon = "🥈"
                rank_color = "#C0C0C0"  # Silver
            elif rank == 3:
                rank_icon = "🥉"
                rank_color = "#CD7F32"  # Bronze
            else:
                rank_icon = "🏅"
                rank_color = "var(--info, #3182CE)"  # Blue
            
            # Timeline indicator
            if days_ahead_behind > 0:
                timeline_text = f"{abs(days_ahead_behind)}d ahead"
                timeline_color = "var(--success, #38A169)"
                timeline_icon = "⚡"
            elif days_ahead_behind < 0:
                timeline_text = f"{abs(days_ahead_behind)}d behind"
                timeline_color = "var(--warning, #DD6B20)"
                timeline_icon = "⏰"
            else:
                timeline_text = "on schedule"
                timeline_color = "var(--info, #3182CE)"
                timeline_icon = "🎯"
            
            # Active status indicator
            status_indicator = "🟢" if str(active_status).lower() == 'yes' else "⚫"
            
            # Truncate long site names
            display_site_name = site_name if len(site_name) <= 16 else f"{site_name[:13]}..."
            
            ranking_items.append(
                html.Div(
                    className="performance-ranking-item",
                    children=[
                        html.Div(
                            className="ranking-info",
                            children=[
                                html.Div(
                                    className="ranking-header",
                                    children=[
                                        html.Span(rank_icon, className="rank-icon", style={"color": rank_color}),
                                        html.Span(status_indicator, className="status-icon"),
                                        html.Div(
                                            f"{display_site_name}",
                                            className="ranking-site-name",
                                            title=f"#{rank}: {site_name} - Score: {composite_score}"
                                        )
                                    ]
                                ),
                                html.Div(
                                    f"({cluster_name})",
                                    className="ranking-site-cluster"
                                )
                            ]
                        ),
                        html.Div(
                            className="performance-metrics",
                            children=[
                                html.Div(
                                    f"{completion_rate}%",
                                    className="completion-metric",
                                    style={"color": "var(--success, #38A169)" if completion_rate >= 50 else "var(--warning, #DD6B20)"},
                                    title=f"{completion_rate}% complete"
                                ),
                                html.Div(
                                    f"{timeline_icon}{abs(days_ahead_behind)}d" if days_ahead_behind != 0 else "🎯",
                                    className="timeline-metric",
                                    style={"color": timeline_color},
                                    title=timeline_text
                                )
                            ]
                        )
                    ]
                )
            )
        
        # Add summary if there are more sites
        if len(performance_sites) > 8:
            remaining_count = len(performance_sites) - 8
            ranking_items.append(
                html.Div(
                    f"... and {remaining_count} more performing sites",
                    className="more-rankings-indicator",
                    style={
                        "textAlign": "center",
                        "color": "var(--text-secondary)",
                        "fontStyle": "italic",
                        "fontSize": "clamp(0.8rem, 1.5vh, 0.95rem)",
                        "padding": "clamp(0.5rem, 1vh, 0.75rem)"
                    }
                )
            )
    
    # Calculate summary stats
    total_ranked = len(performance_sites)
    avg_score = sum(site['composite_score'] for site in performance_sites) / len(performance_sites) if performance_sites else 0
    
    return html.Div(
        className="enhanced-metric-card performance-rankings-card",
        children=[
            # Card Header
            html.Div(
                className="card-header",
                children=[
                    html.Div("🏆", className="card-icon"),
                    html.H3("Top Performers", className="card-title")
                ]
            ),
            
            # Performance Rankings List Container
            html.Div(
                className="performance-rankings-content",
                children=[
                    html.Div(
                        className="performance-rankings-list",
                        children=ranking_items
                    )
                ]
            )
        ]
    )


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