import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import time
import random
from data.database import Database
from utils.route_optimizer import RouteOptimizer

# Page config
st.set_page_config(
    page_title="Mapa GPS - EcoSmart",
    page_icon="🗺️",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_database():
    return Database()

@st.cache_resource  
def init_route_optimizer():
    return RouteOptimizer()

db = init_database()
route_optimizer = init_route_optimizer()

st.title("🗺️ Mapa GPS - Rastreamento em Tempo Real")
st.markdown("---")

# Sidebar controls
st.sidebar.markdown("### 🎛️ Controles do Mapa")

# Map view options
map_style = st.sidebar.selectbox(
    "Estilo do Mapa:",
    ["OpenStreetMap", "Satellite", "Terrain"]
)

# Filter options
show_empty = st.sidebar.checkbox("🟢 Mostrar lixeiras vazias", value=True)
show_medium = st.sidebar.checkbox("🟡 Mostrar lixeiras médias", value=True)  
show_full = st.sidebar.checkbox("🔴 Mostrar lixeiras cheias", value=True)
show_truck = st.sidebar.checkbox("🚛 Mostrar caminhão", value=True)
show_route = st.sidebar.checkbox("🛣️ Mostrar rota otimizada", value=False)

# Real-time tracking toggle
real_time = st.sidebar.checkbox("⚡ Rastreamento em tempo real", value=True)

# Get current data
bins_data = db.get_all_bins()
truck_location = db.get_truck_location()

# Main map area
col1, col2 = st.columns([3, 1])

with col1:
    # Create base map centered on São Paulo
    center_lat, center_lon = -23.5505, -46.6333
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=12,
        tiles='OpenStreetMap' if map_style == 'OpenStreetMap' else 'Stamen Terrain'
    )
    
    # Add bins to map
    for bin_item in bins_data:
        lat, lon = bin_item['coordinates']
        fill_level = bin_item['fill_level']
        
        # Determine color and show/hide based on filters
        if fill_level >= 80:
            color = 'red'
            icon = 'exclamation-sign'
            if not show_full:
                continue
        elif fill_level >= 40:
            color = 'orange'  
            icon = 'warning-sign'
            if not show_medium:
                continue
        else:
            color = 'green'
            icon = 'ok-sign'
            if not show_empty:
                continue
        
        # Create popup content
        popup_content = f"""
        <b>{bin_item['name']}</b><br>
        📍 {bin_item['location']}<br>
        📊 Nível: {fill_level}%<br>
        🗑️ Tipo: {bin_item['waste_type']}<br>
        📅 Última coleta: {bin_item.get('last_collection', 'N/A')}<br>
        🔋 Bateria: {bin_item.get('battery_level', 85)}%
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{bin_item['name']} - {fill_level}%",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        ).add_to(m)
    
    # Add truck location if enabled
    if show_truck and truck_location:
        truck_popup = f"""
        <b>🚛 Caminhão de Coleta</b><br>
        📍 Localização atual<br>
        🕐 Atualizado: {datetime.now().strftime('%H:%M:%S')}<br>
        ⛽ Combustível: {truck_location.get('fuel_level', 78)}%<br>
        👨‍💼 Operador: {truck_location.get('driver', 'João Silva')}
        """
        
        folium.Marker(
            location=truck_location['coordinates'],
            popup=folium.Popup(truck_popup, max_width=300),
            tooltip="Caminhão de Coleta",
            icon=folium.Icon(color='blue', icon='road', prefix='fa')
        ).add_to(m)
    
    # Add optimized route if available and enabled
    if show_route and 'current_route' in st.session_state:
        route_data = st.session_state['current_route']
        
        # Draw route line
        route_coordinates = route_data.get('coordinates', [])
        if route_coordinates:
            folium.PolyLine(
                locations=route_coordinates,
                weight=4,
                color='blue',
                opacity=0.8,
                tooltip="Rota Otimizada"
            ).add_to(m)
            
            # Add route markers
            for i, coord in enumerate(route_coordinates):
                folium.CircleMarker(
                    location=coord,
                    radius=8,
                    popup=f"Parada {i+1}",
                    color='blue',
                    fillColor='lightblue',
                    fillOpacity=0.7
                ).add_to(m)
    
    # Display map
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])

with col2:
    st.subheader("📊 Estatísticas do Mapa")
    
    # Real-time statistics
    total_bins = len(bins_data)
    full_bins = len([b for b in bins_data if b['fill_level'] >= 80])
    medium_bins = len([b for b in bins_data if 40 <= b['fill_level'] < 80])
    empty_bins = total_bins - full_bins - medium_bins
    
    st.metric("Total Lixeiras", total_bins)
    st.metric("🔴 Urgente", full_bins) 
    st.metric("🟡 Médio", medium_bins)
    st.metric("🟢 Vazio", empty_bins)
    
    st.markdown("---")
    
    # Truck information
    if truck_location:
        st.subheader("🚛 Status do Caminhão")
        st.info(f"📍 Lat: {truck_location['coordinates'][0]:.4f}")
        st.info(f"📍 Lon: {truck_location['coordinates'][1]:.4f}")
        st.info(f"⛽ Combustível: {truck_location.get('fuel_level', 78)}%")
        st.info(f"🏃 Velocidade: {truck_location.get('speed', 25)} km/h")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Ações Rápidas")
    
    if st.button("🔄 Atualizar Localização", use_container_width=True):
        # Simulate location update
        with st.spinner("Atualizando..."):
            time.sleep(1)
        st.success("✅ Localização atualizada!")
        st.rerun()
    
    if st.button("🎯 Centrar no Caminhão", use_container_width=True):
        if truck_location:
            st.info("🎯 Mapa centralizado no caminhão")
        else:
            st.warning("⚠️ Caminhão não localizado")
    
    if st.button("📍 Gerar Nova Rota", use_container_width=True):
        with st.spinner("Calculando rota..."):
            time.sleep(2)
            
            # Get bins that need collection
            priority_bins = [b for b in bins_data if b['fill_level'] >= 80]
            
            if priority_bins:
                # Generate optimized route
                optimized_route = route_optimizer.calculate_optimal_route(priority_bins)
                st.session_state['current_route'] = optimized_route
                
                st.success("✅ Nova rota gerada!")
                st.info(f"📍 {len(priority_bins)} paradas")
                st.info(f"📏 {optimized_route['total_distance']} km")
                st.rerun()
            else:
                st.info("ℹ️ Nenhuma lixeira necessita coleta")

# Route details section
if show_route and 'current_route' in st.session_state:
    st.markdown("---")
    st.subheader("🛣️ Detalhes da Rota Otimizada")
    
    route_data = st.session_state['current_route']
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    
    with col_r1:
        st.metric("📏 Distância Total", f"{route_data['total_distance']} km")
    
    with col_r2:
        st.metric("⏱️ Tempo Estimado", f"{route_data['estimated_time']} min")
    
    with col_r3:
        st.metric("⛽ Economia Combustível", f"{route_data['fuel_savings']}%")
    
    with col_r4:
        st.metric("📍 Número de Paradas", len(route_data.get('stops', [])))
    
    # Route stops table
    if 'stops' in route_data:
        st.markdown("### 📋 Paradas da Rota")
        
        stops_data = []
        for i, stop in enumerate(route_data['stops']):
            stops_data.append({
                "Ordem": i + 1,
                "Lixeira": stop['name'],
                "Localização": stop['location'],
                "Nível": f"{stop['fill_level']}%",
                "Tipo": stop['waste_type'],
                "Tempo Est.": f"{stop.get('estimated_time', 5)} min"
            })
        
        if stops_data:
            stops_df = pd.DataFrame(stops_data)
            st.dataframe(stops_df, use_container_width=True, hide_index=True)

# Real-time updates section
st.markdown("---")
col_time1, col_time2 = st.columns([2, 1])

with col_time1:
    st.subheader("⚡ Atualizações em Tempo Real")
    
    # Recent location updates
    recent_updates = [
        f"🚛 Caminhão chegou na Rua das Flores, 123",
        f"🗑️ Lixeira #15 enchimento 85% - coleta necessária", 
        f"✅ Coleta realizada na Av. Paulista, 456",
        f"🔋 Lixeira #8 bateria em 15% - manutenção necessária",
        f"📍 Nova rota otimizada calculada - economia 12%"
    ]
    
    for update in recent_updates:
        st.markdown(f"• {update}")

with col_time2:
    st.markdown("### ⏰ Status Atual")
    st.markdown(f"🕐 **{datetime.now().strftime('%H:%M:%S')}**")
    
    if real_time:
        st.success("✅ Rastreamento ativo")
    else:
        st.warning("⏸️ Rastreamento pausado")

# Auto-refresh mechanism
if real_time:
    time.sleep(2)
    # Simulate random updates to truck location
    if truck_location:
        # Small random movement
        lat_offset = random.uniform(-0.001, 0.001)
        lon_offset = random.uniform(-0.001, 0.001)
        
        # Update truck position in database
        db.update_truck_location(
            truck_location['coordinates'][0] + lat_offset,
            truck_location['coordinates'][1] + lon_offset
        )
    
    st.rerun()
