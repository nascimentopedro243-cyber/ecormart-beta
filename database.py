import sqlite3
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class Database:
    def __init__(self, db_path: str = "ecosmart.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                coordinates TEXT NOT NULL,
                fill_level INTEGER DEFAULT 0,
                battery_level INTEGER DEFAULT 100,
                waste_type TEXT DEFAULT 'comum',
                status TEXT DEFAULT 'active',
                last_collection TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sensors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id TEXT PRIMARY KEY,
                bin_id TEXT NOT NULL,
                fill_level INTEGER DEFAULT 0,
                battery_level INTEGER DEFAULT 100,
                temperature REAL DEFAULT 20.0,
                humidity INTEGER DEFAULT 50,
                status TEXT DEFAULT 'online',
                last_update TEXT,
                coordinates TEXT,
                FOREIGN KEY (bin_id) REFERENCES bins(id)
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                user_type TEXT DEFAULT 'morador',
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                total_disposals INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bin_id TEXT NOT NULL,
                amount REAL NOT NULL,
                collection_date TEXT NOT NULL,
                efficiency REAL DEFAULT 85.0,
                location TEXT,
                waste_type TEXT,
                FOREIGN KEY (bin_id) REFERENCES bins(id)
            )
        """)
        
        # Activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                activity_type TEXT DEFAULT 'general'
            )
        """)
        
        # Truck location table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS truck_location (
                id INTEGER PRIMARY KEY,
                coordinates TEXT NOT NULL,
                fuel_level INTEGER DEFAULT 75,
                speed INTEGER DEFAULT 25,
                driver TEXT DEFAULT 'João Silva',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time INTEGER NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample data for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM bins")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample bins data
        bins_data = [
            ("BIN_001", "Lixeira Condomínio A", "Rua das Flores, 123", "[-23.5505, -46.6333]", 85, 90, "comum", "active", "2024-10-05"),
            ("BIN_002", "Lixeira Reciclável B", "Av. Paulista, 456", "[-23.5615, -46.6565]", 45, 85, "reciclavel", "active", "2024-10-06"),
            ("BIN_003", "Lixeira Orgânica C", "Rua Verde, 789", "[-23.5425, -46.6123]", 92, 75, "organico", "active", "2024-10-04"),
            ("BIN_004", "Lixeira Shopping D", "Av. Faria Lima, 321", "[-23.5735, -46.6890]", 15, 95, "comum", "active", "2024-10-06"),
            ("BIN_005", "Lixeira Parque E", "Rua do Parque, 654", "[-23.5345, -46.6445]", 78, 80, "reciclavel", "active", "2024-10-05"),
            ("BIN_006", "Lixeira Empresa F", "Av. Industrial, 987", "[-23.5455, -46.6767]", 25, 70, "comum", "active", "2024-10-06"),
            ("BIN_007", "Lixeira Escola G", "Rua da Educação, 147", "[-23.5665, -46.6234]", 88, 88, "comum", "maintenance", "2024-10-03"),
            ("BIN_008", "Lixeira Hospital H", "Av. Saúde, 258", "[-23.5555, -46.6678]", 35, 92, "comum", "active", "2024-10-06"),
            ("BIN_009", "Lixeira Mercado I", "Rua Comercial, 369", "[-23.5365, -46.6556]", 67, 65, "organico", "active", "2024-10-05"),
            ("BIN_010", "Lixeira Praça J", "Praça Central, 741", "[-23.5285, -46.6389]", 95, 40, "reciclavel", "active", "2024-10-04"),
            ("BIN_011", "Lixeira Residencial K", "Rua Tranquila, 852", "[-23.5775, -46.6123]", 12, 95, "comum", "active", "2024-10-06"),
            ("BIN_012", "Lixeira Terminal L", "Av. Transporte, 963", "[-23.5125, -46.6445]", 82, 78, "comum", "active", "2024-10-05")
        ]
        
        cursor.executemany("""
            INSERT INTO bins (id, name, location, coordinates, fill_level, battery_level, waste_type, status, last_collection)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, bins_data)
        
        # Sample sensors data
        sensors_data = []
        for i, (bin_id, _, _, coords, fill, battery, _, status, _) in enumerate(bins_data):
            sensor_id = f"SENS_{i+1:03d}"
            temp = round(random.uniform(18, 28), 1)
            humidity = random.randint(40, 80)
            last_update = (datetime.now() - timedelta(minutes=random.randint(1, 30))).strftime("%H:%M:%S")
            sensor_status = "online" if status == "active" else "offline"
            
            sensors_data.append((sensor_id, bin_id, fill, battery, temp, humidity, sensor_status, last_update, coords))
        
        cursor.executemany("""
            INSERT INTO sensors (sensor_id, bin_id, fill_level, battery_level, temperature, humidity, status, last_update, coordinates)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sensors_data)
        
        # Sample users data
        users_data = [
            ("user_001", "Maria Silva", "morador", 1250, 3, 1250, 45),
            ("user_002", "João Santos", "colaborador", 890, 2, 890, 32),
            ("user_003", "Ana Costa", "morador", 2100, 4, 2100, 78),
            ("user_004", "Pedro Lima", "administrador", 450, 1, 450, 18),
            ("user_005", "Lucia Oliveira", "morador", 1650, 3, 1650, 62),
        ]
        
        cursor.executemany("""
            INSERT INTO users (user_id, name, user_type, points, level, experience, total_disposals)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, users_data)
        
        # Sample collections data
        collections_data = [
            ("BIN_001", 25.5, "2024-10-05", 87.2, "Rua das Flores, 123", "comum"),
            ("BIN_002", 15.8, "2024-10-06", 91.5, "Av. Paulista, 456", "reciclavel"),
            ("BIN_003", 30.2, "2024-10-04", 85.8, "Rua Verde, 789", "organico"),
            ("BIN_005", 22.1, "2024-10-05", 88.9, "Rua do Parque, 654", "reciclavel"),
            ("BIN_007", 28.7, "2024-10-03", 82.3, "Rua da Educação, 147", "comum"),
        ]
        
        cursor.executemany("""
            INSERT INTO collections (bin_id, amount, collection_date, efficiency, location, waste_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, collections_data)
        
        # Sample activities
        activities = [
            ("Lixeira BIN_001 atingiu 85% de capacidade", "alert"),
            ("Coleta realizada na Av. Paulista com sucesso", "collection"),
            ("Novo usuário registrado no sistema", "user"),
            ("Sensor SENS_007 necessita manutenção", "maintenance"),
            ("Rota otimizada gerou economia de 15%", "optimization"),
        ]
        
        for activity, activity_type in activities:
            timestamp = (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat()
            cursor.execute("""
                INSERT INTO activities (timestamp, message, activity_type)
                VALUES (?, ?, ?)
            """, (timestamp, activity, activity_type))
        
        # Initial truck location
        cursor.execute("""
            INSERT INTO truck_location (id, coordinates, fuel_level, speed, driver)
            VALUES (1, ?, 78, 25, 'João Silva')
        """, (json.dumps([-23.5505, -46.6333]),))
        
        # Sample API logs
        api_logs = [
            ("/api/sensors/data", "success", 45),
            ("/api/sensors/status", "success", 32),
            ("/api/alerts/create", "success", 28),
            ("/api/sensors/data", "error", 156),
            ("/api/sensors/SENS_001", "success", 38),
        ]
        
        for endpoint, status, response_time in api_logs:
            timestamp = (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
            cursor.execute("""
                INSERT INTO api_logs (timestamp, endpoint, status, response_time)
                VALUES (?, ?, ?, ?)
            """, (timestamp, endpoint, status, response_time))
        
        conn.commit()
        conn.close()
    
    def get_all_bins(self) -> List[Dict[str, Any]]:
        """Get all bins with their current status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, location, coordinates, fill_level, battery_level, 
                   waste_type, status, last_collection
            FROM bins
        """)
        
        bins = []
        for row in cursor.fetchall():
            bins.append({
                'id': row[0],
                'name': row[1],
                'location': row[2],
                'coordinates': json.loads(row[3]),
                'fill_level': row[4],
                'battery_level': row[5],
                'waste_type': row[6],
                'status': row[7],
                'last_collection': row[8]
            })
        
        conn.close()
        return bins
    
    def get_bins_summary(self) -> Dict[str, Any]:
        """Get summary statistics for bins"""
        bins = self.get_all_bins()
        
        total = len(bins)
        full = len([b for b in bins if b['fill_level'] >= 80])
        medium = len([b for b in bins if 40 <= b['fill_level'] < 80])
        empty = total - full - medium
        
        return {
            'total': total,
            'full': full,
            'medium': medium,
            'empty': empty,
            'avg_fill_level': sum([b['fill_level'] for b in bins]) / total if total > 0 else 0
        }
    
    def get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent system activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, message, activity_type
            FROM activities
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'timestamp': row[0],
                'message': row[1],
                'activity_type': row[2]
            })
        
        conn.close()
        return activities
    
    def get_truck_location(self) -> Dict[str, Any] | None:
        """Get current truck location and status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT coordinates, fuel_level, speed, driver
            FROM truck_location
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'coordinates': json.loads(row[0]),
                'fuel_level': row[1],
                'speed': row[2],
                'driver': row[3]
            }
        return None
    
    def update_truck_location(self, lat: float, lon: float):
        """Update truck GPS coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_coords = json.dumps([lat, lon])
        cursor.execute("""
            UPDATE truck_location
            SET coordinates = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (new_coords,))
        
        conn.commit()
        conn.close()
    
    def get_all_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensor data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sensor_id, bin_id, fill_level, battery_level, temperature,
                   humidity, status, last_update
            FROM sensors
        """)
        
        sensors = []
        for row in cursor.fetchall():
            sensors.append({
                'sensor_id': row[0],
                'bin_id': row[1],
                'fill_level': row[2],
                'battery_level': row[3],
                'temperature': row[4],
                'humidity': row[5],
                'status': row[6],
                'last_update': row[7]
            })
        
        conn.close()
        return sensors
    
    def get_realtime_sensor_data(self) -> List[Dict[str, Any]]:
        """Get real-time sensor data with slight variations"""
        sensors = self.get_all_sensors()
        
        # Simulate small changes in data
        for sensor in sensors:
            # Small random variations
            sensor['fill_level'] = max(0, min(100, sensor['fill_level'] + random.randint(-2, 3)))
            sensor['battery_level'] = max(0, min(100, sensor['battery_level'] + random.randint(-1, 1)))
            sensor['last_update'] = datetime.now().strftime("%H:%M:%S")
        
        return sensors
    
    def update_sensor_data_realtime(self):
        """Update sensor data with simulated real-time changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update a few random sensors
        sensor_ids = [f"SENS_{i:03d}" for i in range(1, 13)]
        
        for sensor_id in random.sample(sensor_ids, 3):  # Update 3 random sensors
            fill_change = random.randint(-2, 5)  # Mostly increase fill level
            battery_change = random.randint(-1, 0)  # Slowly decrease battery
            
            cursor.execute("""
                UPDATE sensors
                SET fill_level = CASE 
                    WHEN fill_level + ? > 100 THEN 100
                    WHEN fill_level + ? < 0 THEN 0
                    ELSE fill_level + ?
                END,
                battery_level = CASE
                    WHEN battery_level + ? < 0 THEN 0
                    ELSE battery_level + ?
                END,
                last_update = ?
                WHERE sensor_id = ?
            """, (fill_change, fill_change, fill_change, battery_change, battery_change, 
                  datetime.now().strftime("%H:%M:%S"), sensor_id))
        
        conn.commit()
        conn.close()
    
    def get_user_data(self, user_id: str) -> Dict[str, Any] | None:
        """Get user data by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, name, user_type, points, level, experience, total_disposals
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'name': row[1],
                'user_type': row[2],
                'points': row[3],
                'level': row[4],
                'experience': row[5],
                'total_disposals': row[6]
            }
        return None
    
    def create_user(self, user_id: str, user_type: str) -> Dict[str, Any]:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        name = f"Usuário {user_id}"
        
        cursor.execute("""
            INSERT INTO users (user_id, name, user_type, points, level, experience, total_disposals)
            VALUES (?, ?, ?, 0, 1, 0, 0)
        """, (user_id, name, user_type))
        
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'name': name,
            'user_type': user_type,
            'points': 0,
            'level': 1,
            'experience': 0,
            'total_disposals': 0
        }
    
    def update_user_data(self, user_data: Dict[str, Any]):
        """Update user data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET points = ?, level = ?, experience = ?, total_disposals = ?
            WHERE user_id = ?
        """, (user_data['points'], user_data['level'], user_data['experience'],
              user_data['total_disposals'], user_data['user_id']))
        
        conn.commit()
        conn.close()
    
    def get_recent_collections(self) -> List[Dict[str, Any]]:
        """Get recent collection data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bin_id, amount, collection_date, efficiency, location, waste_type
            FROM collections
            ORDER BY collection_date DESC
            LIMIT 10
        """)
        
        collections = []
        for row in cursor.fetchall():
            collections.append({
                'bin_id': row[0],
                'amount': row[1],
                'date': row[2],
                'efficiency': row[3],
                'location': row[4],
                'waste_type': row[5]
            })
        
        conn.close()
        return collections
    
    def save_sensor_data(self, data: Dict[str, Any]):
        """Save sensor data from API"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sensors 
            (sensor_id, bin_id, fill_level, battery_level, status, last_update)
            VALUES (?, ?, ?, ?, 'online', ?)
        """, (data['sensor_id'], data['bin_id'], data['fill_level'], 
              data['battery_level'], data['timestamp']))
        
        conn.commit()
        conn.close()
    
    def get_api_logs(self) -> List[Dict[str, Any]]:
        """Get recent API logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, endpoint, status, response_time
            FROM api_logs
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'endpoint': row[1],
                'status': row[2],
                'response_time': row[3]
            })
        
        conn.close()
        return logs
    
    def get_esg_data(self, period: str = "Último Mês") -> Dict[str, Any]:
        """Get ESG report data"""
        # Simulated ESG data for demonstration
        return {
            'total_recycled': 2.3,
            'recycled_growth': 15.2,
            'co2_avoided': 5.1,
            'co2_growth': 18.7,
            'fuel_saved': 450.2,
            'fuel_growth': 12.5,
            'active_users': 247,
            'user_growth': 23,
            'recyclable': 45.2,
            'organic': 35.8,
            'common': 18.5,
            'electronic': 0.5,
            'monthly_recycling': [1.2, 1.5, 1.8, 2.1, 2.3, 2.0, 2.2, 2.4, 2.1, 2.3, 2.5, 2.3],
            'recycling_rate': 87.5,
            'landfill_reduction': 72.3,
            'water_saved': 52000,
            'energy_saved': 28500,
            'trees_saved': 245,
            'collection_efficiency': 87.2,
            'avg_collection_time': 42.5,
            'regional_engagement': [45, 52, 38, 41, 47],
            'workshops': 12,
            'people_trained': 280,
            'materials_distributed': 1500,
            'awareness_campaigns': 8,
            'direct_jobs': 15,
            'indirect_jobs': 45,
            'families_benefited': 120,
            'partner_cooperatives': 4,
            'education_investment': 25000.50,
            'training_hours': 480,
            'social_projects': 6,
            'community_participation': 78.5,
            'env_licenses': 8,
            'audits': 4,
            'non_conformities': 2,
            'compliance_training': 15,
            'total_investment': 180000.00,
            'operational_savings': 45000.00,
            'environmental_roi': 25.2,
            'cost_per_ton': 125.50,
            'reports_published': 11,
            'audit_approval': 98.5,
            'risk_mitigation': 92.3,
            'stakeholder_satisfaction': 8.2
        }
    
    def generate_esg_report(self, data: Dict[str, Any]) -> str:
        """Generate ESG report"""
        return f"ESG Report generated with {len(data)} metrics"
    
    def get_sensor_data_export(self, period: str) -> List[Dict[str, Any]]:
        """Get sensor data for export"""
        sensors = self.get_all_sensors()
        return [
            {
                'sensor_id': s['sensor_id'],
                'bin_id': s['bin_id'],
                'fill_level': s['fill_level'],
                'battery_level': s['battery_level'],
                'timestamp': datetime.now().isoformat()
            }
            for s in sensors
        ]
