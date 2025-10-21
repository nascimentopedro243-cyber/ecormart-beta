import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from data.database import Database

# Page config
st.set_page_config(
    page_title="Relatórios ESG - EcoSmart",
    page_icon="📊",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    return Database()

db = init_database()

st.title("📊 Relatórios ESG - Environmental, Social & Governance")
st.markdown("---")

# Sidebar filters
st.sidebar.markdown("### 🔧 Filtros de Relatório")

report_period = st.sidebar.selectbox(
    "Período:",
    ["Última Semana", "Último Mês", "Últimos 3 Meses", "Último Ano", "Personalizado"]
)

if report_period == "Personalizado":
    start_date = st.sidebar.date_input("Data Início:", datetime.now() - timedelta(days=30))
    end_date = st.sidebar.date_input("Data Fim:", datetime.now())

report_type = st.sidebar.selectbox(
    "Tipo de Relatório:",
    ["Completo", "Ambiental", "Social", "Governança"]
)

export_format = st.sidebar.selectbox(
    "Formato de Exportação:",
    ["PDF", "Excel", "CSV"]
)

# Get ESG data
esg_data = db.get_esg_data(period=report_period)

# Executive Summary
st.subheader("📋 Resumo Executivo ESG")

col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)

with col_summary1:
    st.metric(
        "♻️ Total Reciclado",
        f"{esg_data['total_recycled']:.1f}T",
        delta=f"+{esg_data['recycled_growth']:.1f}%"
    )

with col_summary2:
    st.metric(
        "🌿 Emissões Evitadas", 
        f"{esg_data['co2_avoided']:.1f}T CO₂",
        delta=f"+{esg_data['co2_growth']:.1f}%"
    )

with col_summary3:
    st.metric(
        "⛽ Economia Combustível",
        f"{esg_data['fuel_saved']:.1f}L",
        delta=f"+{esg_data['fuel_growth']:.1f}%"
    )

with col_summary4:
    st.metric(
        "👥 Usuários Engajados",
        esg_data['active_users'],
        delta=f"+{esg_data['user_growth']}"
    )

# Environmental Section
if report_type in ["Completo", "Ambiental"]:
    st.markdown("---")
    st.subheader("🌍 Indicadores Ambientais")
    
    col_env1, col_env2 = st.columns(2)
    
    with col_env1:
        # Waste composition chart
        waste_types = ['Reciclável', 'Orgânico', 'Comum', 'Eletrônico']
        waste_amounts = [esg_data['recyclable'], esg_data['organic'], 
                        esg_data['common'], esg_data['electronic']]
        
        fig_waste = px.pie(
            values=waste_amounts,
            names=waste_types,
            title="Composição dos Resíduos Coletados",
            color_discrete_map={
                'Reciclável': '#4CAF50',
                'Orgânico': '#8BC34A', 
                'Comum': '#FFC107',
                'Eletrônico': '#9C27B0'
            }
        )
        fig_waste.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_waste, use_container_width=True)
    
    with col_env2:
        # Monthly recycling trend
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        recycling_trend = esg_data['monthly_recycling']
        
        fig_trend = px.bar(
            x=months,
            y=recycling_trend,
            title="Tendência Mensal de Reciclagem (Toneladas)",
            color=recycling_trend,
            color_continuous_scale='Greens'
        )
        fig_trend.update_layout(showlegend=False)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Environmental KPIs table
    st.markdown("### 🌱 Indicadores de Sustentabilidade")
    
    env_kpis = pd.DataFrame({
        'Indicador': [
            'Taxa de Reciclagem (%)',
            'Redução de Aterro Sanitário (%)',
            'Economia de Água (L)',
            'Economia de Energia (kWh)', 
            'Redução de Emissões CO₂ (kg)',
            'Árvores Poupadas (unid.)',
            'Eficiência da Coleta (%)',
            'Tempo Médio de Coleta (min)'
        ],
        'Valor Atual': [
            f"{esg_data['recycling_rate']:.1f}%",
            f"{esg_data['landfill_reduction']:.1f}%",
            f"{esg_data['water_saved']:,.0f}L",
            f"{esg_data['energy_saved']:,.0f}kWh",
            f"{esg_data['co2_avoided']*1000:.0f}kg",
            f"{esg_data['trees_saved']:,.0f}",
            f"{esg_data['collection_efficiency']:.1f}%",
            f"{esg_data['avg_collection_time']:.1f}min"
        ],
        'Meta': [
            "85%", "70%", "50,000L", "25,000kWh",
            "15,000kg", "200", "90%", "45min"
        ],
        'Status': [
            "✅" if esg_data['recycling_rate'] >= 85 else "⚠️",
            "✅" if esg_data['landfill_reduction'] >= 70 else "⚠️", 
            "✅" if esg_data['water_saved'] >= 50000 else "⚠️",
            "✅" if esg_data['energy_saved'] >= 25000 else "⚠️",
            "✅" if esg_data['co2_avoided']*1000 >= 15000 else "⚠️",
            "✅" if esg_data['trees_saved'] >= 200 else "⚠️",
            "✅" if esg_data['collection_efficiency'] >= 90 else "⚠️",
            "✅" if esg_data['avg_collection_time'] <= 45 else "⚠️"
        ]
    })
    
    st.dataframe(env_kpis, use_container_width=True, hide_index=True)

# Social Section
if report_type in ["Completo", "Social"]:
    st.markdown("---")
    st.subheader("👥 Indicadores Sociais")
    
    col_social1, col_social2 = st.columns(2)
    
    with col_social1:
        # User engagement by region
        regions = ['Centro', 'Norte', 'Sul', 'Leste', 'Oeste']
        engagement = esg_data['regional_engagement']
        
        fig_engagement = px.bar(
            x=regions,
            y=engagement,
            title="Engajamento de Usuários por Região",
            color=engagement,
            color_continuous_scale='Blues',
            labels={'x': 'Região', 'y': 'Usuários Ativos'}
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    with col_social2:
        # Education and awareness metrics
        education_metrics = {
            'Workshops Realizados': esg_data['workshops'],
            'Pessoas Capacitadas': esg_data['people_trained'],
            'Material Educativo Distribuído': esg_data['materials_distributed'],
            'Campanhas de Conscientização': esg_data['awareness_campaigns']
        }
        
        st.markdown("### 📚 Educação e Conscientização")
        for metric, value in education_metrics.items():
            st.metric(metric, value)
    
    # Social impact table
    st.markdown("### 🤝 Impacto Social")
    
    social_impact = pd.DataFrame({
        'Aspecto Social': [
            'Geração de Empregos Diretos',
            'Geração de Empregos Indiretos', 
            'Famílias Beneficiadas',
            'Cooperativas Parceiras',
            'Investimento em Educação Ambiental (R$)',
            'Horas de Treinamento',
            'Projetos Sociais Apoiados',
            'Participação Comunitária (%)'
        ],
        'Resultado': [
            f"{esg_data['direct_jobs']} pessoas",
            f"{esg_data['indirect_jobs']} pessoas",
            f"{esg_data['families_benefited']} famílias", 
            f"{esg_data['partner_cooperatives']} cooperativas",
            f"R$ {esg_data['education_investment']:,.2f}",
            f"{esg_data['training_hours']}h",
            f"{esg_data['social_projects']} projetos",
            f"{esg_data['community_participation']:.1f}%"
        ],
        'Impacto': [
            "Redução do desemprego",
            "Economia local aquecida",
            "Melhoria da qualidade de vida",
            "Fortalecimento da cadeia de reciclagem", 
            "Consciência ambiental",
            "Capacitação profissional",
            "Desenvolvimento comunitário",
            "Engajamento cidadão"
        ]
    })
    
    st.dataframe(social_impact, use_container_width=True, hide_index=True)

# Governance Section  
if report_type in ["Completo", "Governança"]:
    st.markdown("---")
    st.subheader("🏛️ Indicadores de Governança")
    
    col_gov1, col_gov2 = st.columns(2)
    
    with col_gov1:
        # Compliance metrics
        st.markdown("### ⚖️ Conformidade e Compliance")
        
        compliance_data = {
            'Licenças Ambientais': {'status': 'Válidas', 'count': esg_data['env_licenses']},
            'Auditorias Realizadas': {'status': 'Completas', 'count': esg_data['audits']},
            'Não Conformidades': {'status': 'Resolvidas', 'count': esg_data['non_conformities']},
            'Treinamentos Compliance': {'status': 'Realizados', 'count': esg_data['compliance_training']},
        }
        
        for item, data in compliance_data.items():
            st.markdown(f"**{item}:** {data['count']} - {data['status']}")
    
    with col_gov2:
        # Financial transparency
        st.markdown("### 💰 Transparência Financeira")
        
        financial_data = {
            'Investimento Total (R$)': f"R$ {esg_data['total_investment']:,.2f}",
            'Economia Operacional (R$)': f"R$ {esg_data['operational_savings']:,.2f}",
            'ROI Ambiental': f"{esg_data['environmental_roi']:.1f}%",
            'Custo por Tonelada': f"R$ {esg_data['cost_per_ton']:.2f}"
        }
        
        for metric, value in financial_data.items():
            st.markdown(f"**{metric}:** {value}")
    
    # Governance KPIs
    st.markdown("### 📊 KPIs de Governança")
    
    governance_kpis = pd.DataFrame({
        'Área': ['Transparência', 'Compliance', 'Ética', 'Gestão de Riscos', 'Stakeholder'],
        'Indicador': [
            'Relatórios Publicados',
            'Auditorias Aprovadas', 
            'Código de Ética Atualizado',
            'Riscos Identificados/Mitigados',
            'Satisfação dos Stakeholders'
        ],
        'Meta': ['12/ano', '100%', 'Anual', '95%', '>8.0'],
        'Atual': [
            f"{esg_data['reports_published']}/12",
            f"{esg_data['audit_approval']:.1f}%",
            "✅ Atualizado",
            f"{esg_data['risk_mitigation']:.1f}%", 
            f"{esg_data['stakeholder_satisfaction']:.1f}"
        ],
        'Status': [
            "🟢" if esg_data['reports_published'] >= 10 else "🟡",
            "🟢" if esg_data['audit_approval'] >= 95 else "🟡",
            "🟢",
            "🟢" if esg_data['risk_mitigation'] >= 90 else "🟡",
            "🟢" if esg_data['stakeholder_satisfaction'] >= 8.0 else "🟡"
        ]
    })
    
    st.dataframe(governance_kpis, use_container_width=True, hide_index=True)

# Comparative Analysis
st.markdown("---")
st.subheader("📈 Análise Comparativa e Benchmarking")

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    # Year-over-year comparison
    comparison_data = {
        'Métrica': [
            'Total Reciclado (T)',
            'CO₂ Evitado (T)',
            'Usuários Ativos', 
            'Eficiência Coleta (%)',
            'Investimento ESG (R$)'
        ],
        '2023': [1.8, 4.2, 180, 82, 150000],
        '2024': [2.3, 5.1, 247, 87, 180000],
        'Variação (%)': ['+27.8%', '+21.4%', '+37.2%', '+6.1%', '+20.0%']
    }
    
    comp_df = pd.DataFrame(comparison_data)
    st.markdown("### 📊 Comparação Anual")
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

with col_comp2:
    # Benchmark against industry
    benchmark_categories = ['Reciclagem', 'Eficiência', 'Engajamento', 'Sustentabilidade']
    ecosmart_scores = [87, 85, 92, 89]
    industry_avg = [75, 78, 68, 72]
    
    fig_benchmark = go.Figure()
    fig_benchmark.add_trace(go.Bar(
        name='EcoSmart',
        x=benchmark_categories,
        y=ecosmart_scores,
        marker_color='#2E7D32'
    ))
    fig_benchmark.add_trace(go.Bar(
        name='Média do Setor',
        x=benchmark_categories, 
        y=industry_avg,
        marker_color='#FFC107'
    ))
    
    fig_benchmark.update_layout(
        title='Benchmark vs Média do Setor (%)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_benchmark, use_container_width=True)

# Goals and targets
st.markdown("---")
st.subheader("🎯 Metas e Objetivos 2025")

goals_col1, goals_col2 = st.columns(2)

with goals_col1:
    st.markdown("### 🌍 Metas Ambientais")
    goals_env = [
        "♻️ Aumentar taxa de reciclagem para 90%",
        "🌱 Reduzir emissões CO₂ em 30%", 
        "💧 Economizar 75,000L de água",
        "⚡ Reduzir consumo energético em 25%",
        "🌳 Contribuir para o plantio de 500 árvores"
    ]
    for goal in goals_env:
        st.markdown(f"• {goal}")

with goals_col2:
    st.markdown("### 👥 Metas Sociais")
    goals_social = [
        "🎓 Capacitar 500 pessoas em sustentabilidade",
        "🏢 Criar 50 novos empregos diretos",
        "🤝 Estabelecer 15 parcerias comunitárias",
        "📚 Realizar 24 workshops educativos",
        "👨‍👩‍👧‍👦 Beneficiar 1,000 famílias"
    ]
    for goal in goals_social:
        st.markdown(f"• {goal}")

# Report export section
st.markdown("---")
col_export1, col_export2, col_export3 = st.columns([2, 1, 1])

with col_export1:
    st.subheader("📤 Exportar Relatório")
    st.markdown("Gere relatórios profissionais para apresentações e prestação de contas.")

with col_export2:
    if st.button("📊 Gerar Relatório Completo", use_container_width=True):
        with st.spinner("Gerando relatório..."):
            # Simulate report generation
            report_data = db.generate_esg_report(esg_data)
            st.success("✅ Relatório gerado com sucesso!")
            
            # Simulate download
            report_buffer = io.StringIO()
            report_buffer.write("Relatório ESG EcoSmart - Dados fictícios para demonstração")
            st.download_button(
                label="⬇️ Download PDF",
                data=report_buffer.getvalue(),
                file_name=f"relatorio_esg_ecosmart_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

with col_export3:
    if st.button("📈 Dashboard Executivo", use_container_width=True):
        st.info("🎯 Dashboard executivo será aberto em nova aba")
        st.balloons()

# Footer with certifications
st.markdown("---")
st.markdown("### 🏆 Certificações e Reconhecimentos")

cert_cols = st.columns(4)
certifications = [
    "🌟 ISO 14001 - Gestão Ambiental",
    "♻️ Certificação ABRELPE",
    "🏅 Prêmio Sustentabilidade 2024",
    "🌍 Pacto Global ONU"
]

for i, cert in enumerate(certifications):
    with cert_cols[i]:
        st.info(cert)

st.markdown(f"---\n*Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - EcoSmart Platform*")
