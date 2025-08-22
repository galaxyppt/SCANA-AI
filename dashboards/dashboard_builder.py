"""Dashboard builder for SCANA-AI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta

from config import SUPPORTED_INDUSTRIES
from utils.sla_templates import get_sla_template

def build_industry_filter() -> str:
    """Build industry selection filter."""
    return st.sidebar.selectbox(
        "Select Industry",
        options=SUPPORTED_INDUSTRIES,
        index=0
    )

def build_date_filter() -> tuple:
    """Build date range filter."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start = st.date_input("Start Date", start_date)
    with col2:
        end = st.date_input("End Date", end_date)
    
    return start, end

def build_sla_summary(data: pd.DataFrame, industry: str) -> None:
    """Build SLA compliance summary."""
    st.subheader("SLA Compliance Summary")
    
    # Get industry template
    template = get_sla_template(industry)
    
    # Calculate compliance metrics
    total_deliveries = len(data)
    temp_violations = len(data[data['temperature_status'] == 'Violation'])
    time_violations = len(data[data['time_status'] == 'Violation'])
    quality_violations = len(data[data['quality_status'] == 'Violation'])
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Deliveries",
            total_deliveries,
            delta=None
        )
    with col2:
        st.metric(
            "Temperature Compliance",
            f"{((total_deliveries - temp_violations) / total_deliveries * 100):.1f}%",
            delta="-" if temp_violations > 0 else None
        )
    with col3:
        st.metric(
            "Time Compliance",
            f"{((total_deliveries - time_violations) / total_deliveries * 100):.1f}%",
            delta="-" if time_violations > 0 else None
        )
    with col4:
        st.metric(
            "Quality Compliance",
            f"{((total_deliveries - quality_violations) / total_deliveries * 100):.1f}%",
            delta="-" if quality_violations > 0 else None
        )

def build_risk_heatmap(data: pd.DataFrame) -> None:
    """Build vendor risk heatmap."""
    st.subheader("Vendor Risk Heatmap")
    
    # Prepare data for heatmap
    risk_data = data.groupby('vendor_name').agg({
        'temperature_status': lambda x: (x == 'Violation').mean(),
        'time_status': lambda x: (x == 'Violation').mean(),
        'quality_status': lambda x: (x == 'Violation').mean()
    }).round(2)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=risk_data.values,
        x=['Temperature', 'Time', 'Quality'],
        y=risk_data.index,
        colorscale='RdYlGn_r'
    ))
    
    fig.update_layout(
        title="Vendor Risk Analysis",
        xaxis_title="Risk Category",
        yaxis_title="Vendor",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def build_trend_analysis(data: pd.DataFrame) -> None:
    """Build trend analysis charts."""
    st.subheader("Trend Analysis")
    
    # Prepare daily aggregates
    daily_data = data.groupby(['delivery_date', 'vendor_name']).agg({
        'delivery_temperature': 'mean',
        'product_quality_score': 'mean'
    }).reset_index()
    
    # Temperature trend
    fig1 = px.line(
        daily_data,
        x='delivery_date',
        y='delivery_temperature',
        color='vendor_name',
        title="Temperature Trend"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Quality trend
    fig2 = px.line(
        daily_data,
        x='delivery_date',
        y='product_quality_score',
        color='vendor_name',
        title="Quality Score Trend"
    )
    st.plotly_chart(fig2, use_container_width=True)

def add_export_button(data: pd.DataFrame) -> None:
    """Add export to CSV button."""
    if st.button("Export to CSV"):
        # Convert to CSV
        csv = data.to_csv(index=False)
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"scana_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def build_dashboard(data: pd.DataFrame) -> None:
    """Build main dashboard."""
    st.title("SCANA-AI Dashboard")
    
    # Add filters
    industry = build_industry_filter()
    start_date, end_date = build_date_filter()
    
    # Filter data
    filtered_data = data[
        (data['delivery_date'] >= pd.Timestamp(start_date)) &
        (data['delivery_date'] <= pd.Timestamp(end_date))
    ]
    
    # Build dashboard components
    build_sla_summary(filtered_data, industry)
    build_risk_heatmap(filtered_data)
    build_trend_analysis(filtered_data)
    
    # Add export button
    add_export_button(filtered_data) 