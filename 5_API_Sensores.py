import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import requests
import plotly.express as px
import plotly.graph_objects as go
from data.database import Database

# Page config
st.set_page_config(
    page_title="API Sensores - EcoSmart",
    page_icon="📡",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    return Database()

db = init_database()

st.title("📡 API de Sensores IoT - Monitoramento em Tempo Real")
st.markdown("---")

# Sidebar for API configuration
st.sidebar.markdown("### ⚙️ Configuração da API")

api_endpoint = st.sidebar.text_input(
    "Endpoint da API:",
    value="http://localhost:8000/api/sensors"
)

api_key = st.sidebar.text_input(
    "Chave da API:",
    value="your-api-key-here",
    type="password"
)

auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (10s)", value=True)
simulation_mode = st.sidebar.checkbox("🎭 Modo Simulação", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Status da API")

# API status indicators
if simulation_mode:
    st.sidebar.success("✅ Modo Simulação Ativo")
    st.sidebar.info("📡 Sensores: 12/12 Online")
    st.sidebar.info("📶 Latência: 45ms")
else:
    st.sidebar.warning("⚠️ Conectando aos sensores reais...")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard Sensores",
    "📡 Dados em Tempo Real", 
    "🔧 Configuração API",
    "📈 Analytics"
])

with tab1:
    st.subheader("📊 Dashboard de Sensores IoT")
    
    # Get sensor data
    sensors_data = db.get_all_sensors()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_sensors = len(sensors_data)
    online_sensors = len([s for s in sensors_data if s['status'] == 'online'])
    offline_sensors = total_sensors - online_sensors
    avg_battery = sum([s['battery_level'] for s in sensors_data]) / total_sensors if sensors_data else 0
    
    with col1:
        st.metric("📡 Total de Sensores", total_sensors)
    
    with col2:
        st.metric("🟢 Online", online_sensors, delta=f"{(online_sensors/total_sensors)*100:.1f}%")
    
    with col3:
        st.metric("🔴 Offline", offline_sensors, delta=f"-{offline_sensors}")
    
    with col4:
        st.metric("🔋 Bateria Média", f"{avg_battery:.1f}%", delta="Normal")
    
    # Sensors status table
    st.markdown("### 📋 Status Detalhado dos Sensores")
    
    if sensors_data:
        sensors_df = pd.DataFrame(sensors_data)
        
        # Add visual status indicators
        sensors_df['Status Visual'] = sensors_df['status'].apply(
            lambda x: "🟢 Online" if x == 'online' else "🔴 Offline"
        )
        
        sensors_df['Nível'] = sensors_df['fill_level'].apply(
            lambda x: f"{x}%" + (" 🚨" if x >= 80 else " ⚠️" if x >= 60 else " ✅")
        )
        
        sensors_df['Bateria'] = sensors_df['battery_level'].apply(
            lambda x: f"{x}%" + (" 🪫" if x <= 20 else " 🔋")
        )
        
        # Display table
        display_df = sensors_df[['sensor_id', 'bin_id', 'Status Visual', 'Nível', 'Bateria', 'last_update']]
        display_df.columns = ['ID Sensor', 'ID Lixeira', 'Status', 'Nível', 'Bateria', 'Última Atualização']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Real-time charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Fill levels distribution
        if sensors_data:
            fill_levels = [s['fill_level'] for s in sensors_data]
            fig_fill = px.histogram(
                x=fill_levels,
                nbins=10,
                title="Distribuição dos Níveis de Enchimento",
                labels={'x': 'Nível (%)', 'y': 'Quantidade de Sensores'},
                color_discrete_sequence=['#2E7D32']
            )
            st.plotly_chart(fig_fill, use_container_width=True)
    
    with col_chart2:
        # Battery levels
        if sensors_data:
            battery_levels = [s['battery_level'] for s in sensors_data]
            fig_battery = px.box(
                y=battery_levels,
                title="Distribuição dos Níveis de Bateria",
                labels={'y': 'Bateria (%)'},
                color_discrete_sequence=['#FF9800']
            )
            st.plotly_chart(fig_battery, use_container_width=True)

with tab2:
    st.subheader("📡 Dados em Tempo Real")
    
    # Real-time data simulation or API call
    if simulation_mode:
        st.info("🎭 Modo simulação ativo - dados são gerados automaticamente")
    else:
        st.warning("⚠️ Conectando aos sensores reais via API...")
    
    # Live data feed
    st.markdown("### 📊 Feed de Dados ao Vivo")
    
    # Create placeholder for real-time updates
    data_placeholder = st.empty()
    
    # Display real-time sensor data
    realtime_data = db.get_realtime_sensor_data()
    
    with data_placeholder.container():
        if realtime_data:
            for sensor in realtime_data[:6]:  # Show top 6 sensors
                col_sensor1, col_sensor2, col_sensor3, col_sensor4 = st.columns([2, 1, 1, 1])
                
                with col_sensor1:
                    status_emoji = "🟢" if sensor['status'] == 'online' else "🔴"
                    st.markdown(f"**{status_emoji} Sensor {sensor['sensor_id']}** - Lixeira {sensor['bin_id']}")
                
                with col_sensor2:
                    fill_color = "🔴" if sensor['fill_level'] >= 80 else "🟡" if sensor['fill_level'] >= 60 else "🟢"
                    st.markdown(f"{fill_color} **{sensor['fill_level']}%**")
                
                with col_sensor3:
                    battery_color = "🪫" if sensor['battery_level'] <= 20 else "🔋"
                    st.markdown(f"{battery_color} **{sensor['battery_level']}%**")
                
                with col_sensor4:
                    st.markdown(f"🕐 **{sensor['last_update']}**")
                
                st.markdown("---")
    
    # API payload examples
    st.markdown("### 📝 Exemplos de Payloads da API")
    
    col_payload1, col_payload2 = st.columns(2)
    
    with col_payload1:
        st.markdown("**📤 POST /api/sensors/data**")
        sample_payload = {
            "sensor_id": "SENS_001",
            "bin_id": "BIN_001",
            "fill_level": 75,
            "battery_level": 85,
            "temperature": 23.5,
            "humidity": 65,
            "timestamp": datetime.now().isoformat(),
            "gps_coordinates": [-23.5505, -46.6333]
        }
        st.json(sample_payload)
    
    with col_payload2:
        st.markdown("**📥 Resposta da API**")
        sample_response = {
            "status": "success",
            "message": "Dados recebidos com sucesso",
            "sensor_id": "SENS_001",
            "processed_at": datetime.now().isoformat(),
            "next_collection": "2024-10-07T10:30:00"
        }
        st.json(sample_response)

with tab3:
    st.subheader("🔧 Configuração e Testes da API")
    
    # API endpoints documentation
    st.markdown("### 📋 Endpoints Disponíveis")
    
    endpoints = [
        {
            "method": "POST",
            "endpoint": "/api/sensors/data",
            "description": "Receber dados dos sensores IoT",
            "params": "sensor_id, bin_id, fill_level, battery_level, coordinates"
        },
        {
            "method": "GET", 
            "endpoint": "/api/sensors/status",
            "description": "Obter status de todos os sensores",
            "params": "None"
        },
        {
            "method": "GET",
            "endpoint": "/api/sensors/{sensor_id}",
            "description": "Obter dados de um sensor específico", 
            "params": "sensor_id"
        },
        {
            "method": "POST",
            "endpoint": "/api/alerts/create",
            "description": "Criar alerta de manutenção",
            "params": "sensor_id, alert_type, priority"
        }
    ]
    
    endpoints_df = pd.DataFrame(endpoints)
    st.dataframe(endpoints_df, use_container_width=True, hide_index=True)
    
    # API test section
    st.markdown("---")
    st.markdown("### 🧪 Teste da API")
    
    col_test1, col_test2 = st.columns([1, 1])
    
    with col_test1:
        st.markdown("**Testar Envio de Dados**")
        
        test_sensor_id = st.text_input("ID do Sensor:", value="SENS_TEST")
        test_bin_id = st.text_input("ID da Lixeira:", value="BIN_TEST")
        test_fill_level = st.slider("Nível de Enchimento (%):", 0, 100, 50)
        test_battery_level = st.slider("Nível de Bateria (%):", 0, 100, 80)
        
        if st.button("📡 Enviar Dados de Teste"):
            with st.spinner("Enviando dados..."):
                # Simulate API call
                time.sleep(1)
                
                test_data = {
                    "sensor_id": test_sensor_id,
                    "bin_id": test_bin_id, 
                    "fill_level": test_fill_level,
                    "battery_level": test_battery_level,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save test data to database
                db.save_sensor_data(test_data)
                
                st.success("✅ Dados enviados com sucesso!")
                st.json(test_data)
    
    with col_test2:
        st.markdown("**Status da Conectividade**")
        
        # Connection status
        if simulation_mode:
            st.success("🔗 Conexão: Simulação Ativa")
            st.info("📊 Taxa de Sucesso: 100%")
            st.info("⚡ Latência Média: 45ms")
            st.info("📡 Sensores Conectados: 12/12")
        else:
            st.warning("⚠️ Testando conexão real...")
            
        # Recent API calls log
        st.markdown("**📋 Log de Chamadas Recentes**")
        
        api_logs = db.get_api_logs()
        
        for log in api_logs[:5]:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime("%H:%M:%S")
            status_emoji = "✅" if log['status'] == 'success' else "❌"
            st.markdown(f"🕐 **{timestamp}** {status_emoji} {log['endpoint']} - {log['response_time']}ms")

with tab4:
    st.subheader("📈 Analytics e Histórico")
    
    # Historical data analysis
    col_analytics1, col_analytics2 = st.columns(2)
    
    with col_analytics1:
        # Data reception trends
        st.markdown("### 📊 Tendência de Recepção de Dados")
        
        # Generate sample time series data
        hours = pd.date_range(start=datetime.now()-timedelta(hours=24), end=datetime.now(), freq='H')
        data_received = [45 + i % 20 + (i // 6) * 5 for i in range(len(hours))]
        
        fig_trends = px.line(
            x=hours,
            y=data_received,
            title="Dados Recebidos (últimas 24h)",
            labels={'x': 'Hora', 'y': 'Mensagens/Hora'},
            line_shape='spline'
        )
        fig_trends.update_traces(line_color='#2E7D32')
        st.plotly_chart(fig_trends, use_container_width=True)
    
    with col_analytics2:
        # Sensor reliability
        st.markdown("### 🔧 Confiabilidade dos Sensores")
        
        sensor_ids = [f"SENS_{i:03d}" for i in range(1, 13)]
        uptime_percentages = [95 + (i % 5) for i in range(12)]
        
        fig_reliability = px.bar(
            x=sensor_ids,
            y=uptime_percentages,
            title="Uptime por Sensor (%)",
            labels={'x': 'Sensor ID', 'y': 'Uptime (%)'},
            color=uptime_percentages,
            color_continuous_scale='RdYlGn'
        )
        fig_reliability.update_layout(showlegend=False)
        st.plotly_chart(fig_reliability, use_container_width=True)
    
    # Data quality metrics
    st.markdown("---")
    st.markdown("### 📊 Métricas de Qualidade dos Dados")
    
    quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)
    
    with quality_col1:
        st.metric(
            "📈 Taxa de Sucesso",
            "98.5%",
            delta="+0.2%"
        )
    
    with quality_col2:
        st.metric(
            "⚡ Latência Média", 
            "42ms",
            delta="-3ms"
        )
    
    with quality_col3:
        st.metric(
            "🔄 Mensagens/Hora",
            "1,247",
            delta="+156"
        )
    
    with quality_col4:
        st.metric(
            "❌ Taxa de Erro",
            "1.5%",
            delta="-0.3%"
        )
    
    # Error analysis
    st.markdown("### 🚨 Análise de Erros e Alertas")
    
    error_types = ['Timeout', 'Bateria Baixa', 'Sensor Offline', 'Dados Inválidos', 'GPS Falha']
    error_counts = [12, 8, 5, 3, 2]
    
    fig_errors = px.pie(
        values=error_counts,
        names=error_types,
        title="Distribuição de Tipos de Erro",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_errors, use_container_width=True)
    
    # Data export section
    st.markdown("---")
    col_export1, col_export2 = st.columns([2, 1])
    
    with col_export1:
        st.markdown("### 📤 Exportar Dados Históricos")
        
        export_period = st.selectbox(
            "Período de Exportação:",
            ["Última Hora", "Últimas 24 Horas", "Última Semana", "Último Mês"]
        )
        
        export_format = st.selectbox(
            "Formato:",
            ["CSV", "JSON", "Excel"]
        )
    
    with col_export2:
        st.markdown("### ")
        st.markdown("### ")
        
        if st.button("📊 Exportar Dados", use_container_width=True):
            with st.spinner("Gerando arquivo..."):
                time.sleep(2)
                
                # Generate sample export data
                export_data = db.get_sensor_data_export(period=export_period)
                
                if export_format == "CSV":
                    csv_data = pd.DataFrame(export_data).to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                st.success("✅ Arquivo gerado com sucesso!")

# Auto-refresh mechanism
if auto_refresh:
    time.sleep(10)
    # Update sensor data in background
    db.update_sensor_data_realtime()
    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"*Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Sistema EcoSmart IoT*")
