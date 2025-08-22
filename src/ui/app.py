"""SCANA-AI Streamlit Dashboard."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import tempfile
import sys
from typing import Dict, Any, List

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Optional imports with fallbacks
try:
    from src.core.services.analysis_service import AnalysisService
    HAS_ANALYSIS_SERVICE = True
except ImportError:
    HAS_ANALYSIS_SERVICE = False
    print("Analysis service not available. Some features will be disabled.")

try:
    from src.core.vendor_analysis import VendorRiskProfile, analyze_vendor_trends, generate_vendor_summary
    HAS_VENDOR_ANALYSIS = True
except ImportError:
    HAS_VENDOR_ANALYSIS = False
    print("Vendor analysis not available. Some features will be disabled.")

# Constants
TEMP_DIR = tempfile.gettempdir()
DATA_FILE = os.path.join(TEMP_DIR, "scana_delivery_data.json")
API_PORT = os.getenv("SCANA_API_PORT", "8088")  # Get port from environment variable
API_URL = f"http://127.0.0.1:{API_PORT}"
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "delivery_data.csv")

def build_sidebar():
    """Build sidebar navigation."""
    st.sidebar.title("SCANA-AI")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Analysis Dashboard", "🔄 Live Monitoring", "⚙️ Settings"]
    )
    
    # Date range
    st.sidebar.subheader("Date Range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start = st.sidebar.date_input("Start Date", start_date)
    end = st.sidebar.date_input("End Date", end_date)
    
    # Industry filter
    industry = st.sidebar.selectbox(
        "Industry",
        ["Food", "Pharma", "Retail", "BFSI", "Logistics"]
    )
    
    return page, start, end, industry

def show_landing_page():
    """Display the landing page."""
    st.markdown("""
    # 🚀 SCANA-AI: Smart Contract Analysis & Network Automation
    
    ### Transforming Industry Service Contract Management with AI
    """)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Time Saved", "85%", "vs manual review")
    with col2:
        st.metric("Error Reduction", "95%", "in compliance checks")
    with col3:
        st.metric("Cost Savings", "40%", "in operations")
    with col4:
        st.metric("Risk Mitigation", "75%", "improved detection")
    
    st.markdown("---")
    
    # Upload sections
    col1, col2 = st.columns(2)
    with col1:
        # Update to accept both PDF and TXT files
        uploaded_contract = st.file_uploader(
            "📄 Upload Contract (PDF/TXT)",
            type=['pdf', 'txt'],
            help="Upload a service contract to analyze SLA terms"
        )
        
        # Add industry selection for the contract
        if uploaded_contract:
            industry_for_contract = st.selectbox(
                "Select Industry for Contract",
                ["Food & Beverage", "Pharma", "Retail", "Logistics", "BFSI"]
            )
            
            # Save contract with industry prefix and remove existing files
            if st.button("Save Contract"):
                # Create directory if it doesn't exist
                contract_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "contracts")
                os.makedirs(contract_dir, exist_ok=True)
                
                # Remove existing contract files for this industry
                for file in os.listdir(contract_dir):
                    if file.startswith(f"{industry_for_contract.lower().replace(' & ', '_').replace(' ', '_')}_"):
                        os.remove(os.path.join(contract_dir, file))
                
                # Save the new contract file
                file_extension = uploaded_contract.name.split('.')[-1]
                new_filename = f"{industry_for_contract.lower().replace(' & ', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
                with open(os.path.join(contract_dir, new_filename), "wb") as f:
                    f.write(uploaded_contract.getbuffer())
                st.success(f"✅ Contract for {industry_for_contract} saved successfully")
    
    with col2:
        # Update to handle industry-specific delivery logs
        uploaded_log = st.file_uploader(
            "📊 Upload Delivery Log (CSV)",
            type=['csv'],
            help="Upload delivery performance data"
        )
        
        # Add industry selection for the delivery log
        if uploaded_log:
            industry_for_log = st.selectbox(
                "Select Industry for Delivery Log",
                ["Food & Beverage", "Pharma", "Retail", "Logistics", "BFSI"]
            )
            
            # Save delivery log with industry prefix and remove existing files
            if st.button("Save Delivery Log"):
                # Create directory if it doesn't exist
                logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "logs")
                os.makedirs(logs_dir, exist_ok=True)
                
                # Remove existing delivery log files for this industry
                for file in os.listdir(logs_dir):
                    if file.startswith(f"{industry_for_log.lower().replace(' & ', '_').replace(' ', '_')}_delivery_log"):
                        os.remove(os.path.join(logs_dir, file))
                
                # Save the new delivery log file
                new_filename = f"{industry_for_log.lower().replace(' & ', '_').replace(' ', '_')}_delivery_log.csv"
                with open(os.path.join(logs_dir, new_filename), "wb") as f:
                    f.write(uploaded_log.getbuffer())
                st.success(f"✅ Delivery log for {industry_for_log} saved successfully")
        if uploaded_log:
            st.success("✅ Delivery log uploaded successfully")
    
    # Process files if uploaded
    if uploaded_contract and uploaded_log:
        with st.spinner("🔍 Analyzing documents..."):
            try:
                # Initialize analysis service
                analysis_service = AnalysisService()
                
                # Analyze contract
                contract_analysis = analysis_service.analyze_contract(uploaded_contract)
                if 'error' in contract_analysis:
                    st.error(contract_analysis['error'])
                    return
                
                # Process delivery log
                delivery_log = pd.read_csv(uploaded_log)
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs([
                    "📊 Risk Dashboard",
                    "📋 Contract Analysis",
                    "🔍 Delivery Analysis"
                ])
                
                with tab1:
                    display_risk_dashboard(delivery_log)
                
                with tab2:
                    display_contract_analysis(contract_analysis)
                
                with tab3:
                    display_delivery_analysis(delivery_log)
                
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")

def display_risk_dashboard(df: pd.DataFrame):
    """Display vendor risk dashboard."""
    st.subheader("📊 Vendor Risk Analysis")
    
    # Risk metrics
    for vendor in df['vendor_name'].unique():
        vendor_data = df[df['vendor_name'] == vendor]
        risk_profile = VendorRiskProfile(vendor_data)
        risk_category, risk_emoji = risk_profile.get_risk_category()
        
        with st.expander(f"{risk_emoji} {vendor} - {risk_category}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Risk Score", f"{risk_profile.get_risk_score():.1f}")
                st.metric("Temperature Risk", 
                         f"{risk_profile.calculate_temperature_risk():.1f}%")
            
            with col2:
                st.metric("Quality Risk",
                         f"{risk_profile.calculate_quality_risk():.1f}%")
                st.metric("Timing Risk",
                         f"{risk_profile.calculate_timing_risk():.1f}%")
            
        # Recommendations
        st.markdown("#### 📝 Recommendations")
        recommendations = risk_profile.get_improvement_recommendations()
        if recommendations:
            for rec in recommendations:
                st.warning(
                    f"**{rec['category']}** ({rec['risk_level']})\n\n"
                    f"{rec['recommendation']}\n\n"
                    f"*Impact: {rec['impact']}*"
                )
        else:
            st.success("✅ No immediate recommendations needed")

def display_contract_analysis(analysis: Dict[str, Any]):
    """Display contract analysis results."""
    st.subheader("📋 Contract Analysis")
    
    # SLA terms
    st.markdown("### 📝 Extracted SLA Clauses")
    
    # Check if we have the new format with 'clauses' key or old format with 'sla_terms'
    if 'clauses' in analysis:
        clauses = analysis['clauses']
    elif 'sla_terms' in analysis:
        clauses = analysis['sla_terms']
    else:
        clauses = []
        
    # Define icons for different clause types
    icons = {
        "delivery_time": "🕒",
        "temperature_range": "🌡️",
        "quality_standard": "✅",
        "penalty": "⚠️"
    }
    
    # Display each clause in an expander
    for clause in clauses:
        # Get icon for clause type or default to 📄
        icon = icons.get(clause['type'], "📄")
        
        # Format the title with proper capitalization
        title = clause['type'].replace('_', ' ').title()
        
        with st.expander(f"{icon} {title}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Description:**")
                st.markdown(clause['description'])
            
            with col2:
                st.markdown("**Expected Value:**")
                st.markdown(f"**{clause['expected_value']}**")
    
    # Document info
    if 'metadata' in analysis:
        st.markdown("### 📄 Document Information")
        st.json(analysis['metadata'])

def load_delivery_data():
    """Load delivery data from file."""
    try:
        # First try loading from API data file
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                df = pd.DataFrame(data)
        # If no API data, load from default CSV
        elif os.path.exists(DEFAULT_DATA_PATH):
            df = pd.read_csv(DEFAULT_DATA_PATH)
        else:
            return pd.DataFrame()

        # Convert dates and times with error handling
        if 'delivery_date' in df.columns:
            try:
                df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')
            except Exception as e:
                print(f"Error converting delivery_date: {str(e)}")
                df['delivery_date'] = pd.NaT

        if 'delivery_time' in df.columns:
            try:
                # First ensure the time format is correct (HH:MM)
                def format_time(t):
                    try:
                        if pd.isna(t):
                            return None
                        # Handle various time formats
                        if isinstance(t, str):
                            if ':' not in t:
                                # If just hours, add minutes
                                t = f"{t}:00"
                            # Take only HH:MM part if seconds are included
                            t = ':'.join(t.split(':')[:2])
                        return t
                    except:
                        return None

                df['delivery_time'] = df['delivery_time'].apply(format_time)
                # Convert to datetime first
                temp_datetime = pd.to_datetime(df['delivery_time'], format='%H:%M', errors='coerce')
                # Then extract time component
                df['delivery_time'] = temp_datetime.dt.time.astype(str)
            except Exception as e:
                print(f"Error converting delivery_time: {str(e)}")
                df['delivery_time'] = None
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def display_delivery_analysis(df: pd.DataFrame):
    """Display delivery data analysis."""
    st.subheader("🔍 Delivery Performance")
    
    try:
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Ensure delivery_date is datetime
        if 'delivery_date' in df.columns:
            df['delivery_date'] = pd.to_datetime(df['delivery_date'])
        
        # Calculate compliance metrics
        temp_min, temp_max = 2.0, 8.0  # Temperature thresholds
        quality_min = 85  # Quality threshold
        
        # Add compliance flags
        if 'delivery_temperature' in df.columns:
            df['temp_compliant'] = (df['delivery_temperature'] >= temp_min) & (df['delivery_temperature'] <= temp_max)
            temp_compliance_rate = df['temp_compliant'].mean() * 100
        else:
            temp_compliance_rate = 0
            
        if 'product_quality_score' in df.columns:
            df['quality_compliant'] = df['product_quality_score'] >= quality_min
            quality_compliance_rate = df['quality_compliant'].mean() * 100
        else:
            quality_compliance_rate = 0
            
        # Add delivery time compliance if we have expected delivery time
        if 'expected_delivery_time' in df.columns and 'actual_delivery_time' in df.columns:
            # This is simplified - in real app would need proper time comparison
            df['time_compliant'] = df['expected_delivery_time'] == df['actual_delivery_time']
            time_compliance_rate = df['time_compliant'].mean() * 100
        else:
            time_compliance_rate = 100  # Default if we can't calculate
        
        # Calculate FSSAI compliance (food safety)
        if 'fssai_compliant' in df.columns:
            fssai_compliance_rate = df['fssai_compliant'].mean() * 100
        else:
            fssai_compliance_rate = 100  # Default if we can't calculate
        
        # Summary metrics - first row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Deliveries",
                len(df)
            )
        
        with col2:
            avg_temp = df['delivery_temperature'].mean() if 'delivery_temperature' in df.columns else 0
            st.metric(
                "Avg Temperature",
                f"{avg_temp:.1f}°C"
            )
        
        with col3:
            avg_quality = df['product_quality_score'].mean() if 'product_quality_score' in df.columns else 0
            st.metric(
                "Avg Quality Score",
                f"{avg_quality:.1f}"
            )
            
        with col4:
            # Add refresh button
            refresh = st.button("🔄 Refresh Data")
            if refresh:
                st.rerun()
            # Overall compliance rate (average of all compliance types)
            overall_compliance = (temp_compliance_rate + quality_compliance_rate + time_compliance_rate + fssai_compliance_rate) / 4
            st.metric(
                "Overall Compliance",
                f"{overall_compliance:.1f}%"
            )
        
        # Compliance metrics - second row
        st.markdown("### 📊 Compliance Rates")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp_delta = temp_compliance_rate - 95 if temp_compliance_rate <= 100 else 0  # Compare to 95% target
            st.metric(
                "Temperature Compliance",
                f"{temp_compliance_rate:.1f}%",
                f"{temp_delta:.1f}%",
                delta_color="normal" if temp_delta >= 0 else "inverse"
            )
        
        with col2:
            quality_delta = quality_compliance_rate - 95 if quality_compliance_rate <= 100 else 0
            st.metric(
                "Quality Compliance",
                f"{quality_compliance_rate:.1f}%",
                f"{quality_delta:.1f}%",
                delta_color="normal" if quality_delta >= 0 else "inverse"
            )
        
        with col3:
            time_delta = time_compliance_rate - 95 if time_compliance_rate <= 100 else 0
            st.metric(
                "Delivery Time Compliance",
                f"{time_compliance_rate:.1f}%",
                f"{time_delta:.1f}%",
                delta_color="normal" if time_delta >= 0 else "inverse"
            )
            
        with col4:
            fssai_delta = fssai_compliance_rate - 100 if fssai_compliance_rate <= 100 else 0
            st.metric(
                "FSSAI Compliance",
                f"{fssai_compliance_rate:.1f}%",
                f"{fssai_delta:.1f}%",
                delta_color="normal" if fssai_delta >= 0 else "inverse"
            )
        
        # Performance Summary Table
        st.markdown("### 📋 Vendor Performance Summary")
        
        # Create summary dataframe
        if 'vendor_name' in df.columns:
            summary_df = df.groupby('vendor_name').agg({
                'delivery_temperature': lambda x: ((x >= temp_min) & (x <= temp_max)).mean() * 100,  # Temperature compliance %
                'product_quality_score': lambda x: (x >= quality_min).mean() * 100,  # Quality compliance %
                'temp_compliant': 'mean',  # For risk score calculation
                'quality_compliant': 'mean'  # For risk score calculation
            }).round(2)
            
            # Calculate risk score (0-100, higher is better)
            summary_df['risk_score'] = (summary_df['temp_compliant'] * 50 + summary_df['quality_compliant'] * 50) * 100
            
            # Add region column (mock data for demo)
            summary_df['region'] = 'north_india'  # In real app, this would come from the data
            
            # Add category column (mock data for demo)
            summary_df['category'] = 'general'  # In real app, this would come from the data
            
            # Add delivery performance (mock data for demo)
            summary_df['delivery_performance'] = 100  # In real app, this would be calculated
            
            # Add FSSAI compliance (mock data for demo)
            summary_df['fssai_compliance'] = 'Review Required'  # In real app, this would come from the data
            
            # Prepare display columns
            display_df = summary_df.reset_index()
            display_df = display_df[['vendor_name', 'category', 'region', 'risk_score', 
                                    'delivery_temperature', 'product_quality_score', 
                                    'delivery_performance', 'fssai_compliance']]
            
            # Rename columns for display
            display_df.columns = ['Vendor Name', 'Category', 'Region', 'Risk Score', 
                                'Temperature Compliance %', 'Quality Score', 
                                'Delivery Performance %', 'FSSAI Compliance']
            
            # Display the table with conditional formatting
            st.dataframe(
                display_df,
                column_config={
                    "Risk Score": st.column_config.NumberColumn(
                        "Risk Score",
                        format="%.2f",
                        help="Risk score (0-100, higher is better)"
                    ),
                    "Temperature Compliance %": st.column_config.ProgressColumn(
                        "Temperature Compliance %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Quality Score": st.column_config.ProgressColumn(
                        "Quality Score",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Delivery Performance %": st.column_config.ProgressColumn(
                        "Delivery Performance %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Temperature trend
        if 'delivery_temperature' in df.columns:
            st.subheader("Temperature Trend")
            temp_fig = px.line(
                df,
                x='delivery_date',
                y='delivery_temperature',
                color='vendor_name' if 'vendor_name' in df.columns else None,
                title="Delivery Temperature Over Time"
            )
            temp_fig.add_hline(y=temp_min, line_dash="dash", line_color="red", annotation_text="Min Temp")
            temp_fig.add_hline(y=temp_max, line_dash="dash", line_color="red", annotation_text="Max Temp")
            st.plotly_chart(temp_fig, use_container_width=True)
        
        # Quality trend
        if 'product_quality_score' in df.columns:
            st.subheader("Quality Score Trend")
            quality_fig = px.line(
                df,
                x='delivery_date',
                y='product_quality_score',
                color='vendor_name' if 'vendor_name' in df.columns else None,
                title="Quality Score Over Time"
            )
            quality_fig.add_hline(y=quality_min, line_dash="dash", line_color="red", annotation_text="Min Quality")
            st.plotly_chart(quality_fig, use_container_width=True)
        
        # Delivery status breakdown
        if 'delivery_status' in df.columns:
            st.subheader("Delivery Status Breakdown")
            status_counts = df['delivery_status'].value_counts()
            status_fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Delivery Status Distribution"
            )
            st.plotly_chart(status_fig, use_container_width=True)
        
        # Flagged Anomalies
        st.subheader("⚠️ Flagged Anomalies")
        
        # Create anomalies dataframe
        anomalies = []
        
        # Temperature violations
        if 'delivery_temperature' in df.columns:
            temp_violations = df[~df['temp_compliant']]
            if not temp_violations.empty:
                for _, row in temp_violations.iterrows():
                    anomalies.append({
                        "vendor": row.get('vendor_name', 'Unknown'),
                        "date": row.get('delivery_date', 'Unknown'),
                        "type": "Temperature",
                        "value": f"{row['delivery_temperature']:.1f}°C",
                        "threshold": f"{temp_min:.1f}°C - {temp_max:.1f}°C",
                        "severity": "High" if abs(row['delivery_temperature'] - ((temp_min + temp_max)/2)) > 3 else "Medium"
                    })
        
        # Quality violations
        if 'product_quality_score' in df.columns:
            quality_violations = df[~df['quality_compliant']]
            if not quality_violations.empty:
                for _, row in quality_violations.iterrows():
                    anomalies.append({
                        "vendor": row.get('vendor_name', 'Unknown'),
                        "date": row.get('delivery_date', 'Unknown'),
                        "type": "Quality",
                        "value": f"{row['product_quality_score']:.1f}",
                        "threshold": f">= {quality_min}",
                        "severity": "High" if row['product_quality_score'] < 70 else "Medium"
                    })
        
        # Display anomalies
        if anomalies:
            anomalies_df = pd.DataFrame(anomalies)
            st.dataframe(
                anomalies_df,
                column_config={
                    "severity": st.column_config.SelectboxColumn(
                        "Severity",
                        options=["Low", "Medium", "High"],
                        required=True,
                    ),
                },
                use_container_width=True
            )
        else:
            st.success("No anomalies detected in the current data")
        
        # Risk heatmap
        if ('vendor_name' in df.columns and 
            'delivery_temperature' in df.columns and 
            'product_quality_score' in df.columns):
            
            st.subheader("Risk Heatmap")
            risk_data = df.groupby('vendor_name').agg({
                'delivery_temperature': lambda x: ((x < temp_min) | (x > temp_max)).mean(),
                'product_quality_score': lambda x: (x < quality_min).mean()
            }).round(2)
            
            if not risk_data.empty:
                fig = go.Figure(data=go.Heatmap(
                    z=risk_data.values,
                    x=['Temperature', 'Quality'],
                    y=risk_data.index,
                    colorscale='RdYlGn_r'
                ))
                fig.update_layout(title="Vendor Risk Analysis")
                st.plotly_chart(fig, use_container_width=True)
        
        # Cluster plot for vendor performance
        if ('vendor_name' in df.columns and 
            'delivery_temperature' in df.columns and 
            'product_quality_score' in df.columns):
            
            st.subheader("Vendor Performance Clusters")
            
            # Aggregate data by vendor
            vendor_perf = df.groupby('vendor_name').agg({
                'delivery_temperature': lambda x: ((x >= temp_min) & (x <= temp_max)).mean(),  # Temperature compliance
                'product_quality_score': lambda x: (x >= quality_min).mean(),  # Quality compliance
            }).reset_index()
            
            # Create scatter plot
            fig = px.scatter(
                vendor_perf,
                x='delivery_temperature',
                y='product_quality_score',
                text='vendor_name',
                size=[20] * len(vendor_perf),  # Consistent size
                color='vendor_name',
                title="Vendor Performance Clusters",
                labels={
                    'delivery_temperature': 'Temperature Compliance Rate',
                    'product_quality_score': 'Quality Compliance Rate'
                }
            )
            
            # Update layout
            fig.update_layout(
                xaxis=dict(tickformat='.0%'),
                yaxis=dict(tickformat='.0%')
            )
            
            # Add quadrant lines
            fig.add_hline(y=0.8, line_dash="dash", line_color="gray")
            fig.add_vline(x=0.8, line_dash="dash", line_color="gray")
            
            # Add annotations for quadrants
            fig.add_annotation(x=0.4, y=0.4, text="High Risk", showarrow=False, font=dict(color="red"))
            fig.add_annotation(x=0.4, y=0.9, text="Quality Issues", showarrow=False, font=dict(color="orange"))
            fig.add_annotation(x=0.9, y=0.4, text="Temperature Issues", showarrow=False, font=dict(color="orange"))
            fig.add_annotation(x=0.9, y=0.9, text="Low Risk", showarrow=False, font=dict(color="green"))
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table with export
        st.subheader("Delivery Data")
        st.dataframe(df)
        
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "delivery_analysis.csv",
                "text/csv"
            )
            
    except Exception as e:
        st.error(f"Error analyzing delivery data: {str(e)}")
        st.error("Please check that your data contains the required columns and valid values.")
        import traceback
        st.error(traceback.format_exc())

def display_live_monitoring():
    """Display live monitoring dashboard."""
    st.subheader("🔄 Live Monitoring")
    
    # Add filters and refresh button
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        industry_filter = st.selectbox(
            "Industry",
            ["All", "Food & Beverage", "Pharma", "Retail", "Logistics", "BFSI"]
        )
    
    with col2:
        vendor_filter = st.text_input("Vendor Name")
    
    with col3:
        date_filter = st.date_input("Date", datetime.now())
    
    with col4:
        # Add refresh button
        refresh = st.button("🔄 Refresh Data")
        if refresh:
            st.rerun()
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "API Status",
            "Connected",
            "Online"
        )
    
    with col2:
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Ensure data is a list
                    if isinstance(data, dict):
                        data = [data]
                    df = pd.DataFrame(data)
                    vendor_count = len(df['vendor_name'].unique()) if not df.empty else 0
            else:
                vendor_count = 0
            
            st.metric(
                "Active Vendors",
                vendor_count
            )
        except Exception as e:
            st.metric(
                "Active Vendors",
                "Error"
            )
            print(f"Error counting vendors: {str(e)}")
    
    with col3:
        st.metric(
            "Last Update",
            datetime.now().strftime("%H:%M:%S")
        )
    
    # Live data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list
                if isinstance(data, dict):
                    data = [data]
                df = pd.DataFrame(data)
                
                if not df.empty:
                    # Convert dates with error handling
                    try:
                        df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')
                    except Exception as e:
                        print(f"Error converting dates: {str(e)}")
                        df['delivery_date'] = pd.NaT
                    
                    # Apply filters
                    if industry_filter != "All":
                        df = df[df['industry'] == industry_filter]
                    
                    if vendor_filter:
                        df = df[df['vendor_name'].str.contains(vendor_filter, case=False, na=False)]
                    
                    if date_filter:
                        df = df[df['delivery_date'].dt.date == date_filter]
                    
                    # Show filter status
                    if industry_filter != "All" or vendor_filter or date_filter != datetime.now().date():
                        st.info(f"Showing filtered data: {len(df)} records found")
                    
                    # Live feed
                    st.subheader("Live Feed")
                    st.dataframe(df.tail(10))
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        try:
                            fig = px.line(
                                df.tail(50),
                                x='delivery_date',
                                y='delivery_temperature',
                                title="Temperature Trend"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating temperature chart: {str(e)}")
                    
                    with col2:
                        try:
                            fig = px.line(
                                df.tail(50),
                                x='delivery_date',
                                y='product_quality_score',
                                title="Quality Score Trend"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating quality chart: {str(e)}")
                else:
                    st.info("No delivery data available yet.")
        else:
            st.info("Waiting for delivery data...")
            
    except Exception as e:
        st.error(f"Error loading live data: {str(e)}")
        print(f"Detailed error: {str(e)}")  # For debugging

def display_settings():
    """Display settings page."""
    st.subheader("⚙️ Settings")
            
    # Temperature settings
    st.markdown("### 🌡️ Temperature Thresholds")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Minimum Temperature (°C)", value=2.0, step=0.5)
    with col2:
        st.number_input("Maximum Temperature (°C)", value=8.0, step=0.5)
            
    # Quality settings
    st.markdown("### ⭐ Quality Thresholds")
    st.slider("Minimum Quality Score", min_value=0, max_value=100, value=85)
    
    # Alert settings
    st.markdown("### 🔔 Alert Settings")
    st.checkbox("Enable Email Alerts", value=True)
    st.checkbox("Enable SMS Alerts")
    st.checkbox("Enable Webhook Alerts")
    
    # Save button
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

def main():
    """Main function."""
    # Set page config
    st.set_page_config(
        page_title="SCANA-AI Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Get navigation and filters
    page, start_date, end_date, industry = build_sidebar()
    
    # Display selected page
    if page == "🏠 Home":
        show_landing_page()
    elif page == "📊 Analysis Dashboard":
        try:
            # Load data
            df = load_delivery_data()
            
            if not df.empty:
                # Filter by date
                df['delivery_date'] = pd.to_datetime(df['delivery_date'])
                mask = (
                    (df['delivery_date'].dt.date >= start_date) &
                    (df['delivery_date'].dt.date <= end_date)
                )
                df = df[mask]
                display_delivery_analysis(df)
            else:
                st.info("No data available for analysis.")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    elif page == "🔄 Live Monitoring":
        display_live_monitoring()
    else:  # Settings
        display_settings()

if __name__ == "__main__":
    main()