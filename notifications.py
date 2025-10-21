import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

class NotificationManager:
    def __init__(self, db_path: str = "ecosmart.db"):
        self.db_path = db_path
        self.init_notifications_table()
    
    def init_notifications_table(self):
        """Initialize notifications table in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                data TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def send_notification(self, user_id: str, title: str, message: str, 
                         notification_type: str = "info", data: Dict | None = None, 
                         expires_hours: int = 24) -> bool:
        """Send a notification to a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            data_json = json.dumps(data) if data else None
            
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, notification_type, expires_at, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, title, message, notification_type, expires_at, data_json))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: str, limit: int = 10, 
                             only_unread: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, title, message, notification_type, is_read, created_at, data
            FROM notifications
            WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        params = [user_id]
        
        if only_unread:
            query += " AND is_read = FALSE"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(str(limit))
        
        cursor.execute(query, params)
        
        notifications = []
        for row in cursor.fetchall():
            data = json.loads(row[6]) if row[6] else {}
            notifications.append({
                'id': row[0],
                'title': row[1],
                'message': row[2],
                'type': row[3],
                'is_read': bool(row[4]),
                'created_at': row[5],
                'data': data
            })
        
        conn.close()
        return notifications
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE notifications
                SET is_read = TRUE
                WHERE id = ?
            """, (notification_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = ? AND is_read = FALSE 
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """, (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def send_points_notification(self, user_id: str, points: int, action: str) -> bool:
        """Send notification when user earns points"""
        title = "🎉 Pontos Ganhos!"
        message = f"Você ganhou {points} pontos por {action}!"
        
        data = {
            'points_earned': points,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="success",
            data=data,
            expires_hours=48
        )
    
    def send_level_up_notification(self, user_id: str, new_level: int) -> bool:
        """Send notification when user levels up"""
        title = "🎊 Level Up!"
        message = f"Parabéns! Você subiu para o nível {new_level}!"
        
        data = {
            'new_level': new_level,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="success",
            data=data,
            expires_hours=72
        )
    
    def send_achievement_notification(self, user_id: str, achievement: Dict[str, Any]) -> bool:
        """Send notification when user unlocks an achievement"""
        title = f"🏆 Nova Conquista: {achievement['title']}"
        message = f"Você desbloqueou: {achievement['description']}"
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="achievement",
            data=achievement,
            expires_hours=168  # 1 week
        )
    
    def send_reward_notification(self, user_id: str, reward: Dict[str, Any]) -> bool:
        """Send notification when user redeems a reward"""
        title = f"🎁 Recompensa Resgatada!"
        message = f"Você resgatou: {reward['name']}"
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="info",
            data=reward,
            expires_hours=240  # 10 days
        )
    
    def send_maintenance_alert(self, user_id: str, bin_id: str, issue: str) -> bool:
        """Send maintenance alert to administrators"""
        title = "🔧 Alerta de Manutenção"
        message = f"Lixeira {bin_id} necessita manutenção: {issue}"
        
        data = {
            'bin_id': bin_id,
            'issue': issue,
            'priority': 'medium',
            'timestamp': datetime.now().isoformat()
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="warning",
            data=data,
            expires_hours=24
        )
    
    def send_collection_alert(self, user_id: str, bin_id: str, fill_level: int) -> bool:
        """Send collection needed alert"""
        title = "🚛 Coleta Necessária"
        message = f"Lixeira {bin_id} está {fill_level}% cheia e necessita coleta"
        
        data = {
            'bin_id': bin_id,
            'fill_level': fill_level,
            'priority': 'high' if fill_level >= 90 else 'medium',
            'timestamp': datetime.now().isoformat()
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="urgent" if fill_level >= 90 else "warning",
            data=data,
            expires_hours=6
        )
    
    def send_weekly_summary(self, user_id: str, stats: Dict[str, Any]) -> bool:
        """Send weekly summary notification"""
        title = "📊 Resumo Semanal"
        message = f"Esta semana: {stats['disposals']} descartes, {stats['points']} pontos ganhos!"
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="info",
            data=stats,
            expires_hours=168
        )
    
    def send_challenge_notification(self, user_id: str, challenge: Dict[str, Any]) -> bool:
        """Send notification about new challenge"""
        title = "🎯 Novo Desafio!"
        message = f"{challenge['title']} - {challenge['reward']} pontos"
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="challenge",
            data=challenge,
            expires_hours=168
        )
    
    def cleanup_expired_notifications(self):
        """Remove expired notifications from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM notifications
            WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get overall notification statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total notifications
        cursor.execute("SELECT COUNT(*) FROM notifications")
        total = cursor.fetchone()[0]
        
        # Unread notifications
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = FALSE")
        unread = cursor.fetchone()[0]
        
        # Notifications by type
        cursor.execute("""
            SELECT notification_type, COUNT(*)
            FROM notifications
            GROUP BY notification_type
        """)
        
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_notifications': total,
            'unread_notifications': unread,
            'read_rate': ((total - unread) / total * 100) if total > 0 else 0,
            'notifications_by_type': by_type
        }
    
    def simulate_push_notification(self, user_id: str, title: str, message: str) -> Dict[str, Any]:
        """Simulate sending a push notification (for demo purposes)"""
        # In a real implementation, this would integrate with push notification services
        # like Firebase Cloud Messaging, Apple Push Notification service, etc.
        
        notification_payload = {
            'to': user_id,
            'title': title,
            'body': message,
            'data': {
                'timestamp': datetime.now().isoformat(),
                'app': 'EcoSmart',
                'type': 'gamification'
            }
        }
        
        # Simulate successful delivery
        return {
            'status': 'sent',
            'message_id': f"msg_{random.randint(1000, 9999)}",
            'delivered_at': datetime.now().isoformat(),
            'payload': notification_payload
        }
