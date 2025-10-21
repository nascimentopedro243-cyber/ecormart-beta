import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from data.database import Database
from utils.route_optimizer import RouteOptimizer

# Page config
st.set_page_config(
    page_title="Dashboard Administrativo - EcoSmart",
    page_icon="📊",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    return Database()

@st.cache_resource
def init_route_optimizer():
    return RouteOptimizer()

db = init_database()
route_optimizer = init_route_optimizer()

st.title("📊 Dashboard Administrativo")
st.markdown("---")

# Auto-refresh functionality
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
if auto_refresh:
    time.sleep(1)  # Simulate real-time updates

# Sidebar filters
st.sidebar.markdown("### 🔧 Filtros")
selected_region = st.sidebar.selectbox(
    "Região:",
    ["Todas", "Centro", "Norte", "Sul", "Leste", "Oeste"]
)

selected_period = st.sidebar.selectbox(
    "Período:",
    ["Hoje", "Esta Semana", "Este Mês", "Últimos 3 Meses"]
)

# Main metrics row
col1, col2, col3, col4 = st.columns(4)

bins_data = db.get_all_bins()
total_bins = len(bins_data)
full_bins = len([b for b in bins_data if b['fill_level'] >= 80])
medium_bins = len([b for b in bins_data if 40 <= b['fill_level'] < 80])
empty_bins = total_bins - full_bins - medium_bins

with col1:
    st.metric(
        "🗑️ Total de Lixeiras",
        total_bins,
        delta=f"+{len([b for b in bins_data if b['status'] == 'active'])} ativas"
    )

with col2:
    st.metric(
        "🔴 Coleta Urgente",
        full_bins,
        delta=f"{round((full_bins/total_bins)*100, 1)}% do total"
    )

with col3:
    st.metric(
        "🟡 Nível Médio", 
        medium_bins,
        delta=f"{round((medium_bins/total_bins)*100, 1)}% do total"
    )

with col4:
    st.metric(
        "🟢 Vazias/Baixo",
        empty_bins,
        delta=f"{round((empty_bins/total_bins)*100, 1)}% do total"
    )

st.markdown("---")

# Real-time status grid
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🏠 Status das Lixeiras por Região")
    
    # Create bins status dataframe
    bins_df = pd.DataFrame(bins_data)
    
    # Status distribution chart
    fig_status = px.bar(
        x=['Vazio (0-40%)', 'Médio (40-80%)', 'Cheio (80-100%)'],
        y=[empty_bins, medium_bins, full_bins],
        color=['Vazio (0-40%)', 'Médio (40-80%)', 'Cheio (80-100%)'],
        color_discrete_map={
            'Vazio (0-40%)': '#4CAF50',
            'Médio (40-80%)': '#FF9800', 
            'Cheio (80-100%)': '#F44336'
        },
        title="Distribuição de Status das Lixeiras"
    )
    fig_status.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_status, use_container_width=True)

with col_right:
    st.subheader("⚡ Alertas em Tempo Real")
    
    # Critical alerts
    critical_bins = [b for b in bins_data if b['fill_level'] >= 90]
    
    if critical_bins:
        st.error(f"🚨 {len(critical_bins)} lixeiras críticas (>90%)")
        for bin_item in critical_bins[:5]:
            st.markdown(f"• **{bin_item['name']}** - {bin_item['fill_level']}% - {bin_item['location']}")
    
    # Maintenance alerts
    maintenance_bins = [b for b in bins_data if b['status'] == 'maintenance']
    if maintenance_bins:
        st.warning(f"🔧 {len(maintenance_bins)} lixeiras em manutenção")
    
    # Collection efficiency
    st.info(f"📈 Eficiência de coleta: 87%")
    st.success(f"♻️ Economia de combustível: 23%")

# Detailed bins table
st.markdown("---")
st.subheader("📋 Lista Detalhada de Lixeiras")

# Filter bins based on selection
filtered_bins = bins_data
if selected_region != "Todas":
    filtered_bins = [b for b in bins_data if selected_region.lower() in b['location'].lower()]

# Create detailed table
bins_table_data = []
for bin_item in filtered_bins:
    status_emoji = "🔴" if bin_item['fill_level'] >= 80 else "🟡" if bin_item['fill_level'] >= 40 else "🟢"
    collection_status = "Urgente" if bin_item['fill_level'] >= 80 else "Programada" if bin_item['fill_level'] >= 40 else "Não Necessária"
    
    bins_table_data.append({
        "Status": status_emoji,
        "ID": bin_item['id'],
        "Nome": bin_item['name'],
        "Localização": bin_item['location'],
        "Nível (%)": bin_item['fill_level'],
        "Tipo": bin_item['waste_type'],
        "Coleta": collection_status,
        "Última Coleta": bin_item.get('last_collection', 'N/A')
    })

if bins_table_data:
    bins_df_display = pd.DataFrame(bins_table_data)
    st.dataframe(bins_df_display, use_container_width=True, hide_index=True)

# Route optimization section
st.markdown("---")
st.subheader("🚛 Otimização de Rotas")

col_route1, col_route2 = st.columns([1, 1])

with col_route1:
    if st.button("🔄 Gerar Rota Otimizada", type="primary", use_container_width=True):
        with st.spinner("Calculando rota mais eficiente..."):
            time.sleep(2)  # Simulate processing
            
            # Get bins that need collection
            bins_for_collection = [b for b in bins_data if b['fill_level'] >= 80]
            
            if bins_for_collection:
                optimized_route = route_optimizer.calculate_optimal_route(bins_for_collection)
                
                st.success(f"✅ Rota otimizada gerada!")
                st.info(f"📍 {len(bins_for_collection)} lixeiras na rota")
                st.info(f"📏 Distância total: {optimized_route['total_distance']} km")
                st.info(f"⏱️ Tempo estimado: {optimized_route['estimated_time']} min")
                st.info(f"⛽ Economia de combustível: {optimized_route['fuel_savings']}%")
                
                # Store route in session state for map display
                st.session_state['current_route'] = optimized_route
            else:
                st.info("ℹ️ Não há lixeiras que necessitam coleta no momento.")

with col_route2:
    # Recent collections summary
    st.markdown("### 📊 Resumo de Coletas Recentes")
    
    collections_data = db.get_recent_collections()
    if collections_data:
        total_collected = sum([c['amount'] for c in collections_data])
        avg_efficiency = sum([c['efficiency'] for c in collections_data]) / len(collections_data)
        
        st.metric("Total Coletado (kg)", f"{total_collected:.1f}")
        st.metric("Eficiência Média", f"{avg_efficiency:.1f}%")
        
        # Quick stats
        for collection in collections_data[:3]:
            st.markdown(f"• {collection['date']} - {collection['amount']}kg - {collection['location']}")
    else:
        st.info("Nenhuma coleta recente registrada.")

# Performance indicators
st.markdown("---")
st.subheader("📈 Indicadores de Performance")

perf_col1, perf_col2 = st.columns(2)

with perf_col1:
    # Fill level trend over time
    dates = pd.date_range(start=datetime.now()-timedelta(days=7), end=datetime.now(), freq='D')
    fill_levels = [65, 70, 75, 68, 72, 78, 73]  # Simulated data
    
    fig_trend = px.line(
        x=dates,
        y=fill_levels,
        title="Tendência de Nível de Enchimento (7 dias)",
        labels={'x': 'Data', 'y': 'Nível Médio (%)'}
    )
    fig_trend.update_traces(line_color='#2E7D32')
    st.plotly_chart(fig_trend, use_container_width=True)

with perf_col2:
    # Waste type distribution
    waste_types = ['Reciclável', 'Orgânico', 'Comum']
    waste_amounts = [45, 35, 20]  # Simulated data
    
    fig_waste = px.pie(
        values=waste_amounts,
        names=waste_types,
        title="Distribuição por Tipo de Resíduo",
        color_discrete_map={
            'Reciclável': '#4CAF50',
            'Orgânico': '#8BC34A',
            'Comum': '#FFC107'
        }
    )
    st.plotly_chart(fig_waste, use_container_width=True)

# Auto-refresh timer
if auto_refresh:
    time.sleep(30)
    st.rerun()
