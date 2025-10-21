import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from data.database import Database
from utils.gamification import GamificationSystem
from utils.notifications import NotificationManager

# Page config
st.set_page_config(
    page_title="Gamificação - EcoSmart", 
    page_icon="🎮",
    layout="wide"
)

# Initialize systems
@st.cache_resource
def init_database():
    return Database()

@st.cache_resource
def init_gamification():
    return GamificationSystem()

@st.cache_resource  
def init_notifications():
    return NotificationManager()

db = init_database()
gamification = init_gamification()
notifications = init_notifications()

st.title("🎮 Sistema de Gamificação EcoSmart")
st.markdown("---")

# User authentication simulation
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Login section
if not st.session_state['current_user']:
    st.subheader("🔐 Login de Usuário")
    
    col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
    
    with col_login2:
        user_id = st.text_input("👤 ID do Usuário:", placeholder="Digite seu ID")
        user_type = st.selectbox("Tipo de Usuário:", ["Morador", "Colaborador", "Administrador"])
        
        if st.button("🚪 Entrar", use_container_width=True):
            if user_id:
                # Simulate user login
                user_data = db.get_user_data(user_id)
                if not user_data:
                    # Create new user
                    user_data = db.create_user(user_id, user_type)
                
                st.session_state['current_user'] = user_data
                st.success(f"✅ Bem-vindo, {user_data['name']}!")
                st.rerun()
            else:
                st.error("⚠️ Por favor, digite seu ID")
else:
    # Main gamification interface
    current_user = st.session_state['current_user']
    
    # Header with user info
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    
    with col_header1:
        st.subheader(f"👋 Olá, {current_user['name']}!")
        st.markdown(f"**Tipo:** {current_user['user_type']} | **Nível:** {current_user['level']} | **XP:** {current_user['experience']}")
    
    with col_header2:
        # QR Code simulation
        if st.button("📱 Simular QR Code", use_container_width=True):
            # Simulate QR code scan for waste disposal
            points_earned = gamification.process_waste_disposal(current_user['user_id'])
            if points_earned > 0:
                st.success(f"🎉 +{points_earned} pontos! Resíduo descartado corretamente!")
                
                # Update user data
                current_user['points'] += points_earned
                current_user['total_disposals'] += 1
                current_user['experience'] += points_earned
                
                # Check for level up
                new_level = gamification.check_level_up(current_user)
                if new_level > current_user['level']:
                    st.balloons()
                    st.success(f"🎊 LEVEL UP! Você subiu para o nível {new_level}!")
                    current_user['level'] = new_level
                
                # Update session state
                st.session_state['current_user'] = current_user
                db.update_user_data(current_user)
                
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Descarte inválido ou lixeira não encontrada")
    
    with col_header3:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state['current_user'] = None
            st.rerun()
    
    # Main dashboard
    st.markdown("---")
    
    # Points and achievements section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Pontos Totais",
            current_user['points'],
            delta=f"+{gamification.get_points_this_week(current_user['user_id'])}"
        )
    
    with col2:
        st.metric(
            "🏆 Nível Atual", 
            current_user['level'],
            delta=f"{current_user['experience']}/{gamification.get_xp_for_next_level(current_user['level'])} XP"
        )
    
    with col3:
        st.metric(
            "🗑️ Descartes Corretos",
            current_user['total_disposals'],
            delta=f"+{gamification.get_disposals_this_week(current_user['user_id'])}"
        )
    
    with col4:
        ranking_position = gamification.get_user_ranking_position(current_user['user_id'])
        st.metric(
            "🥇 Posição no Ranking",
            f"#{ranking_position}",
            delta=gamification.get_ranking_change(current_user['user_id'])
        )
    
    # Progress bars section
    st.markdown("### 📊 Seu Progresso")
    
    col_prog1, col_prog2 = st.columns(2)
    
    with col_prog1:
        # XP Progress to next level
        current_xp = current_user['experience']
        next_level_xp = gamification.get_xp_for_next_level(current_user['level'])
        progress_percentage = (current_xp % 1000) / 10  # Assuming 1000 XP per level
        
        st.markdown(f"**Progresso para Nível {current_user['level'] + 1}:**")
        st.progress(progress_percentage / 100)
        st.markdown(f"{current_xp % 1000}/1000 XP")
    
    with col_prog2:
        # Weekly goal progress
        weekly_disposals = gamification.get_disposals_this_week(current_user['user_id'])
        weekly_goal = 10  # Goal: 10 correct disposals per week
        
        st.markdown("**Meta Semanal (Descartes Corretos):**")
        st.progress(min(weekly_disposals / weekly_goal, 1.0))
        st.markdown(f"{weekly_disposals}/{weekly_goal} descartes")
    
    # Achievements section
    st.markdown("---")
    st.subheader("🏆 Conquistas e Badges")
    
    achievements = gamification.get_user_achievements(current_user['user_id'])
    
    if achievements:
        # Display achievements in columns
        achievement_cols = st.columns(len(achievements) if len(achievements) <= 4 else 4)
        
        for i, achievement in enumerate(achievements[:4]):
            with achievement_cols[i]:
                st.markdown(f"### {achievement['badge']}")
                st.markdown(f"**{achievement['title']}**")
                st.markdown(f"{achievement['description']}")
                st.markdown(f"*Conquistado em: {achievement['date']}*")
    else:
        st.info("🎯 Continue descartando corretamente para desbloquear conquistas!")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📈 Atividade Recente")
    
    recent_activity = gamification.get_user_recent_activity(current_user['user_id'])
    
    if recent_activity:
        for activity in recent_activity[:5]:
            timestamp = datetime.fromisoformat(activity['timestamp']).strftime("%d/%m %H:%M")
            st.markdown(f"🕐 **{timestamp}** - {activity['action']} (+{activity['points']} pontos)")
    else:
        st.info("Nenhuma atividade recente. Comece a descartar resíduos para ganhar pontos!")
    
    # Rewards section
    st.markdown("---")
    col_reward1, col_reward2 = st.columns([2, 1])
    
    with col_reward1:
        st.subheader("🎁 Loja de Recompensas")
        
        rewards = gamification.get_available_rewards()
        
        for reward in rewards:
            with st.expander(f"{reward['emoji']} {reward['name']} - {reward['cost']} pontos"):
                st.markdown(f"**Descrição:** {reward['description']}")
                st.markdown(f"**Validade:** {reward['validity']}")
                
                if current_user['points'] >= reward['cost']:
                    if st.button(f"🛒 Resgatar ({reward['cost']} pts)", key=f"reward_{reward['id']}"):
                        # Process reward redemption
                        success = gamification.redeem_reward(current_user['user_id'], reward['id'])
                        if success:
                            st.success(f"✅ {reward['name']} resgatado com sucesso!")
                            current_user['points'] -= reward['cost']
                            st.session_state['current_user'] = current_user
                            st.rerun()
                        else:
                            st.error("❌ Erro ao resgatar recompensa")
                else:
                    st.markdown(f"❌ Pontos insuficientes (faltam {reward['cost'] - current_user['points']})")
    
    with col_reward2:
        st.subheader("💎 Suas Recompensas")
        
        user_rewards = gamification.get_user_rewards(current_user['user_id'])
        
        if user_rewards:
            for reward in user_rewards[:5]:
                expiry_date = datetime.fromisoformat(reward['expiry_date']).strftime("%d/%m/%Y")
                st.markdown(f"🎁 **{reward['name']}**")
                st.markdown(f"Expira em: {expiry_date}")
                st.markdown("---")
        else:
            st.info("Você ainda não possui recompensas. Acumule pontos para resgatar!")

# Global ranking section
st.markdown("---")
st.subheader("🏅 Ranking Global")

ranking_data = gamification.get_global_ranking()

col_rank1, col_rank2 = st.columns([2, 1])

with col_rank1:
    # Top 10 ranking table
    if ranking_data:
        ranking_df = pd.DataFrame(ranking_data[:10])
        
        # Add medals for top 3
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        ranking_df['Posição'] = [f"{medals[i]} {i+1}º" for i in range(len(ranking_df))]
        ranking_df = ranking_df[['Posição', 'name', 'points', 'level', 'total_disposals']]
        ranking_df.columns = ['Posição', 'Usuário', 'Pontos', 'Nível', 'Descartes']
        
        # Highlight current user
        if st.session_state['current_user']:
            current_user_id = st.session_state['current_user']['user_id']
            for idx, row in ranking_df.iterrows():
                if row['Usuário'] == st.session_state['current_user']['name']:
                    st.markdown(f"**Sua posição atual: {row['Posição']}**")
                    break
        
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    else:
        st.info("Ranking não disponível no momento")

with col_rank2:
    # Ranking statistics
    if ranking_data:
        st.markdown("### 📊 Estatísticas")
        
        total_users = len(ranking_data)
        total_points = sum([u['points'] for u in ranking_data])
        total_disposals = sum([u['total_disposals'] for u in ranking_data])
        
        st.metric("👥 Total de Usuários", total_users)
        st.metric("🎯 Total de Pontos", f"{total_points:,}")
        st.metric("🗑️ Total de Descartes", f"{total_disposals:,}")
        
        # Top performer
        if ranking_data:
            top_user = ranking_data[0]
            st.markdown("### 🏆 Líder do Mês")
            st.info(f"👑 {top_user['name']}\n{top_user['points']} pontos")

# Charts section
st.markdown("---")
st.subheader("📈 Análise de Performance")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Points evolution chart (simulated data)
    if st.session_state['current_user']:
        current_user = st.session_state['current_user']
        dates = pd.date_range(start=datetime.now()-timedelta(days=30), end=datetime.now(), freq='D')
        points_evolution = [current_user['points'] - (30-i)*10 for i in range(len(dates))]  # Simulated growth
        
        fig_points = px.line(
            x=dates,
            y=points_evolution,
            title="Evolução dos Pontos (30 dias)",
            labels={'x': 'Data', 'y': 'Pontos Acumulados'}
        )
        fig_points.update_traces(line_color='#2E7D32')
        st.plotly_chart(fig_points, use_container_width=True)

with chart_col2:
    # Weekly activity chart
    week_days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    weekly_disposals = [2, 3, 1, 4, 2, 1, 0]  # Simulated data
    
    fig_weekly = px.bar(
        x=week_days,
        y=weekly_disposals,
        title="Descartes por Dia da Semana",
        labels={'x': 'Dia', 'y': 'Número de Descartes'},
        color=weekly_disposals,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_weekly, use_container_width=True)

# Tips and challenges section
st.markdown("---")
col_tips1, col_tips2 = st.columns(2)

with col_tips1:
    st.subheader("💡 Dicas Sustentáveis")
    
    tips = [
        "🌱 Separe corretamente os resíduos recicláveis",
        "♻️ Reutilize materiais sempre que possível", 
        "🍃 Prefira produtos com menos embalagem",
        "🌍 Descarte eletrônicos em pontos especializados",
        "💚 Use sacolas reutilizáveis para compras"
    ]
    
    for tip in tips:
        st.markdown(f"• {tip}")

with col_tips2:
    st.subheader("🎯 Desafios da Semana")
    
    challenges = gamification.get_weekly_challenges()
    
    for challenge in challenges:
        progress = challenge.get('progress', 0)
        target = challenge.get('target', 100)
        
        st.markdown(f"**{challenge['title']}**")
        st.markdown(f"{challenge['description']}")
        st.progress(progress / target)
        st.markdown(f"Progresso: {progress}/{target} - Recompensa: {challenge['reward']} pontos")
        st.markdown("---")
