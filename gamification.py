import sqlite3
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from utils.notifications import NotificationManager

class GamificationSystem:
    def __init__(self, db_path: str = "ecosmart.db"):
        self.db_path = db_path
        self.notifications = NotificationManager(db_path)
        self.init_gamification_tables()
        self.populate_initial_data()
    
    def init_gamification_tables(self):
        """Initialize gamification-related tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                badge TEXT NOT NULL,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL,
                points_reward INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id),
                UNIQUE(user_id, achievement_id)
            )
        """)
        
        # Rewards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                emoji TEXT DEFAULT '🎁',
                cost INTEGER NOT NULL,
                validity TEXT DEFAULT '30 dias',
                category TEXT DEFAULT 'benefit',
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User rewards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                reward_id INTEGER NOT NULL,
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TEXT NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (reward_id) REFERENCES rewards(id)
            )
        """)
        
        # User activities table (for gamification tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                points_earned INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Weekly challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                target INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                challenge_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # User challenge progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_challenge_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                challenge_id INTEGER NOT NULL,
                progress INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES weekly_challenges(id),
                UNIQUE(user_id, challenge_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def populate_initial_data(self):
        """Populate initial achievements, rewards, and challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM achievements")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Initial achievements
        achievements = [
            ("Primeiro Descarte", "Realize seu primeiro descarte correto", "🌱", "disposal_count", 1, 50),
            ("Eco Warrior", "Realize 50 descartes corretos", "⚔️", "disposal_count", 50, 500),
            ("Reciclador Expert", "Descarte 25 materiais recicláveis", "♻️", "recyclable_count", 25, 300),
            ("Semana Verde", "Descarte corretamente todos os dias da semana", "🗓️", "weekly_streak", 7, 200),
            ("Nível 5", "Alcance o nível 5", "🏆", "level", 5, 1000),
            ("Consciente Orgânico", "Descarte 30 resíduos orgânicos", "🍃", "organic_count", 30, 400),
            ("Separador Master", "Use todos os tipos de lixeira", "🎯", "bin_types_used", 4, 600),
            ("Pontuador", "Acumule 1000 pontos", "💎", "total_points", 1000, 100),
            ("Streak Master", "Mantenha uma sequência de 30 dias", "🔥", "daily_streak", 30, 800),
            ("Embaixador Verde", "Convide 5 amigos para o app", "👥", "referrals", 5, 1500)
        ]
        
        cursor.executemany("""
            INSERT INTO achievements (title, description, badge, requirement_type, requirement_value, points_reward)
            VALUES (?, ?, ?, ?, ?, ?)
        """, achievements)
        
        # Initial rewards
        rewards = [
            ("Desconto Supermercado", "5% de desconto em compras", "🛒", 200, "30 dias", "discount"),
            ("Vale Transporte", "R$ 10 em vale transporte", "🚌", 300, "15 dias", "transport"),
            ("Desconto Farmácia", "10% de desconto em farmácias", "💊", 400, "30 dias", "health"),
            ("Cashback", "R$ 5 de volta no cartão", "💰", 500, "60 dias", "money"),
            ("Desconto Restaurante", "15% em restaurantes parceiros", "🍽️", 600, "30 dias", "food"),
            ("Vale Combustível", "R$ 20 em combustível", "⛽", 800, "45 dias", "fuel"),
            ("Desconto Academia", "1 mês grátis na academia", "💪", 1000, "30 dias", "fitness"),
            ("Ingresso Cinema", "1 ingresso de cinema grátis", "🎬", 1200, "60 dias", "entertainment"),
            ("Vale Livros", "R$ 30 em livros", "📚", 700, "90 dias", "education"),
            ("Plantio de Árvore", "Plante uma árvore em seu nome", "🌳", 1500, "Permanente", "environmental")
        ]
        
        cursor.executemany("""
            INSERT INTO rewards (name, description, emoji, cost, validity, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rewards)
        
        # Weekly challenges
        challenges = [
            ("Semana da Reciclagem", "Descarte 15 materiais recicláveis", 15, 300, "recyclable", "2024-10-07", "2024-10-13"),
            ("Desafio Orgânico", "Descarte 10 resíduos orgânicos", 10, 200, "organic", "2024-10-07", "2024-10-13"),
            ("Consistência Verde", "Descarte algo todos os dias", 7, 500, "daily", "2024-10-07", "2024-10-13"),
            ("Explorador de Lixeiras", "Use 3 tipos diferentes de lixeiras", 3, 250, "variety", "2024-10-07", "2024-10-13")
        ]
        
        cursor.executemany("""
            INSERT INTO weekly_challenges (title, description, target, reward, challenge_type, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, challenges)
        
        conn.commit()
        conn.close()
    
    def process_waste_disposal(self, user_id: str, bin_type: str = "comum", 
                             location: str | None = None) -> int:
        """Process a waste disposal and award points"""
        # Base points for correct disposal
        base_points = 10
        
        # Bonus points based on waste type
        type_bonuses = {
            'reciclavel': 5,
            'organico': 3,
            'comum': 0,
            'eletronico': 10
        }
        
        bonus_points = type_bonuses.get(bin_type, 0)
        total_points = base_points + bonus_points
        
        # Add random bonus (0-5 points)
        random_bonus = random.randint(0, 5)
        total_points += random_bonus
        
        # Record activity
        self._record_user_activity(user_id, "waste_disposal", total_points, {
            'bin_type': bin_type,
            'location': location,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update challenge progress
        self._update_challenge_progress(user_id, bin_type)
        
        # Check for achievements
        self._check_achievements(user_id)
        
        # Send notification
        self.notifications.send_points_notification(
            user_id, total_points, f"descarte correto ({bin_type})"
        )
        
        return total_points
    
    def _record_user_activity(self, user_id: str, activity_type: str, 
                             points: int, metadata: Dict[str, Any]):
        """Record user activity in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_activities (user_id, activity_type, points_earned, metadata)
            VALUES (?, ?, ?, ?)
        """, (user_id, activity_type, points, json.dumps(metadata)))
        
        conn.commit()
        conn.close()
    
    def get_points_this_week(self, user_id: str) -> int:
        """Get points earned this week"""
        week_start = datetime.now() - timedelta(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(points_earned)
            FROM user_activities
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, week_start.isoformat()))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result or 0
    
    def get_disposals_this_week(self, user_id: str) -> int:
        """Get number of disposals this week"""
        week_start = datetime.now() - timedelta(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM user_activities
            WHERE user_id = ? AND activity_type = 'waste_disposal' AND timestamp >= ?
        """, (user_id, week_start.isoformat()))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result
    
    def get_xp_for_next_level(self, current_level: int) -> int:
        """Calculate XP needed for next level"""
        return current_level * 1000  # 1000 XP per level
    
    def check_level_up(self, user_data: Dict[str, Any]) -> int:
        """Check if user should level up"""
        current_xp = user_data['experience']
        current_level = user_data['level']
        
        xp_for_next = self.get_xp_for_next_level(current_level)
        
        if current_xp >= xp_for_next:
            new_level = current_level + 1
            
            # Send level up notification
            self.notifications.send_level_up_notification(user_data['user_id'], new_level)
            
            return new_level
        
        return current_level
    
    def get_user_ranking_position(self, user_id: str) -> int:
        """Get user's position in global ranking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) + 1
            FROM users u1
            WHERE u1.points > (
                SELECT points FROM users WHERE user_id = ?
            )
        """, (user_id,))
        
        position = cursor.fetchone()[0]
        conn.close()
        
        return position
    
    def get_ranking_change(self, user_id: str) -> str:
        """Get ranking change (simplified simulation)"""
        # In a real implementation, this would track historical positions
        change = random.randint(-3, 5)
        if change > 0:
            return f"+{change}"
        elif change < 0:
            return str(change)
        return "0"
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's earned achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.title, a.description, a.badge, ua.earned_at
            FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.earned_at DESC
        """, (user_id,))
        
        achievements = []
        for row in cursor.fetchall():
            earned_date = datetime.fromisoformat(row[3]).strftime("%d/%m/%Y")
            achievements.append({
                'title': row[0],
                'description': row[1],
                'badge': row[2],
                'date': earned_date
            })
        
        conn.close()
        return achievements
    
    def get_user_recent_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's recent gamification activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT activity_type, points_earned, timestamp, metadata
            FROM user_activities
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (user_id,))
        
        activities = []
        for row in cursor.fetchall():
            metadata = json.loads(row[3]) if row[3] else {}
            
            action_map = {
                'waste_disposal': 'Descarte correto realizado',
                'level_up': 'Subiu de nível',
                'achievement': 'Conquista desbloqueada',
                'reward_redeemed': 'Recompensa resgatada'
            }
            
            activities.append({
                'action': action_map.get(row[0], row[0]),
                'points': row[1],
                'timestamp': row[2],
                'metadata': metadata
            })
        
        conn.close()
        return activities
    
    def get_available_rewards(self) -> List[Dict[str, Any]]:
        """Get available rewards for redemption"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, emoji, cost, validity, category
            FROM rewards
            WHERE available = TRUE
            ORDER BY cost ASC
        """)
        
        rewards = []
        for row in cursor.fetchall():
            rewards.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'emoji': row[3],
                'cost': row[4],
                'validity': row[5],
                'category': row[6]
            })
        
        conn.close()
        return rewards
    
    def redeem_reward(self, user_id: str, reward_id: int) -> bool:
        """Redeem a reward for the user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get reward info
            cursor.execute("""
                SELECT name, cost, validity
                FROM rewards
                WHERE id = ? AND available = TRUE
            """, (reward_id,))
            
            reward = cursor.fetchone()
            if not reward:
                conn.close()
                return False
            
            # Check user points
            cursor.execute("""
                SELECT points FROM users WHERE user_id = ?
            """, (user_id,))
            
            user_points = cursor.fetchone()[0]
            
            if user_points < reward[1]:  # Not enough points
                conn.close()
                return False
            
            # Calculate expiry date
            expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Record redemption
            cursor.execute("""
                INSERT INTO user_rewards (user_id, reward_id, expiry_date)
                VALUES (?, ?, ?)
            """, (user_id, reward_id, expiry_date))
            
            # Record activity
            cursor.execute("""
                INSERT INTO user_activities (user_id, activity_type, points_earned, metadata)
                VALUES (?, 'reward_redeemed', ?, ?)
            """, (user_id, -reward[1], json.dumps({'reward_name': reward[0], 'reward_id': reward_id})))
            
            conn.commit()
            conn.close()
            
            # Send notification
            self.notifications.send_reward_notification(user_id, {
                'name': reward[0],
                'validity': reward[2]
            })
            
            return True
            
        except Exception as e:
            print(f"Error redeeming reward: {e}")
            return False
    
    def get_user_rewards(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's redeemed rewards"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.name, r.emoji, ur.expiry_date, ur.used
            FROM user_rewards ur
            JOIN rewards r ON ur.reward_id = r.id
            WHERE ur.user_id = ? AND ur.expiry_date >= date('now')
            ORDER BY ur.redeemed_at DESC
        """, (user_id,))
        
        rewards = []
        for row in cursor.fetchall():
            rewards.append({
                'name': row[0],
                'emoji': row[1],
                'expiry_date': row[2],
                'used': bool(row[3])
            })
        
        conn.close()
        return rewards
    
    def get_global_ranking(self) -> List[Dict[str, Any]]:
        """Get global user ranking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, points, level, total_disposals
            FROM users
            ORDER BY points DESC, level DESC
            LIMIT 50
        """)
        
        ranking = []
        for row in cursor.fetchall():
            ranking.append({
                'name': row[0],
                'points': row[1],
                'level': row[2],
                'total_disposals': row[3]
            })
        
        conn.close()
        return ranking
    
    def get_weekly_challenges(self) -> List[Dict[str, Any]]:
        """Get current weekly challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT id, title, description, target, reward, challenge_type
            FROM weekly_challenges
            WHERE active = TRUE AND start_date <= ? AND end_date >= ?
        """, (today, today))
        
        challenges = []
        for row in cursor.fetchall():
            # Get user's progress (if any)
            cursor.execute("""
                SELECT progress
                FROM user_challenge_progress
                WHERE challenge_id = ? AND user_id = ?
            """, (row[0], "current_user"))  # Simplified for demo
            
            progress_row = cursor.fetchone()
            progress = progress_row[0] if progress_row else 0
            
            challenges.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'target': row[3],
                'reward': row[4],
                'challenge_type': row[5],
                'progress': progress
            })
        
        conn.close()
        return challenges
    
    def _update_challenge_progress(self, user_id: str, bin_type: str):
        """Update user progress on weekly challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get active challenges
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT id, challenge_type, target
            FROM weekly_challenges
            WHERE active = TRUE AND start_date <= ? AND end_date >= ?
        """, (today, today))
        
        challenges = cursor.fetchall()
        
        for challenge_id, challenge_type, target in challenges:
            should_increment = False
            
            # Check if this disposal applies to the challenge
            if challenge_type == "recyclable" and bin_type == "reciclavel":
                should_increment = True
            elif challenge_type == "organic" and bin_type == "organico":
                should_increment = True
            elif challenge_type == "daily":
                should_increment = True
            elif challenge_type == "variety":
                should_increment = True
            
            if should_increment:
                # Update or create progress record
                cursor.execute("""
                    INSERT OR IGNORE INTO user_challenge_progress (user_id, challenge_id, progress)
                    VALUES (?, ?, 0)
                """, (user_id, challenge_id))
                
                cursor.execute("""
                    UPDATE user_challenge_progress
                    SET progress = progress + 1
                    WHERE user_id = ? AND challenge_id = ? AND progress < ?
                """, (user_id, challenge_id, target))
                
                # Check if challenge is completed
                cursor.execute("""
                    SELECT progress FROM user_challenge_progress
                    WHERE user_id = ? AND challenge_id = ?
                """, (user_id, challenge_id))
                
                current_progress = cursor.fetchone()[0]
                
                if current_progress >= target:
                    cursor.execute("""
                        UPDATE user_challenge_progress
                        SET completed = TRUE, completed_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND challenge_id = ?
                    """, (user_id, challenge_id))
                    
                    # Award challenge points (handled elsewhere)
        
        conn.commit()
        conn.close()
    
    def _check_achievements(self, user_id: str):
        """Check and award new achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user stats
        cursor.execute("""
            SELECT COUNT(*) as total_disposals,
                   SUM(CASE WHEN JSON_EXTRACT(metadata, '$.bin_type') = 'reciclavel' THEN 1 ELSE 0 END) as recyclable_count,
                   SUM(CASE WHEN JSON_EXTRACT(metadata, '$.bin_type') = 'organico' THEN 1 ELSE 0 END) as organic_count
            FROM user_activities
            WHERE user_id = ? AND activity_type = 'waste_disposal'
        """, (user_id,))
        
        stats = cursor.fetchone()
        total_disposals, recyclable_count, organic_count = stats or (0, 0, 0)
        
        # Get user level and points
        cursor.execute("""
            SELECT level, points FROM users WHERE user_id = ?
        """, (user_id,))
        
        user_stats = cursor.fetchone()
        if not user_stats:
            conn.close()
            return
        
        level, points = user_stats
        
        # Check against achievements
        cursor.execute("""
            SELECT id, title, description, badge, requirement_type, requirement_value, points_reward
            FROM achievements
            WHERE id NOT IN (
                SELECT achievement_id FROM user_achievements WHERE user_id = ?
            )
        """, (user_id,))
        
        available_achievements = cursor.fetchall()
        
        for achievement in available_achievements:
            achievement_id, title, description, badge, req_type, req_value, points_reward = achievement
            
            earned = False
            
            if req_type == "disposal_count" and total_disposals >= req_value:
                earned = True
            elif req_type == "recyclable_count" and recyclable_count >= req_value:
                earned = True
            elif req_type == "organic_count" and organic_count >= req_value:
                earned = True
            elif req_type == "level" and level >= req_value:
                earned = True
            elif req_type == "total_points" and points >= req_value:
                earned = True
            
            if earned:
                # Award achievement
                cursor.execute("""
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (?, ?)
                """, (user_id, achievement_id))
                
                # Record activity
                cursor.execute("""
                    INSERT INTO user_activities (user_id, activity_type, points_earned, metadata)
                    VALUES (?, 'achievement', ?, ?)
                """, (user_id, points_reward, json.dumps({
                    'achievement_title': title,
                    'achievement_id': achievement_id
                })))
                
                # Send notification
                self.notifications.send_achievement_notification(user_id, {
                    'title': title,
                    'description': description,
                    'badge': badge,
                    'points_reward': points_reward
                })
        
        conn.commit()
        conn.close()
