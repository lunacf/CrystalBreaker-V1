"""
UserManager - Sistema de gestión de usuarios y puntuaciones
Maneja:
- Registro de usuarios
- Login/Logout
- Guardar y cargar puntuaciones (highscores)
- Persistencia en archivos CSV
"""

import csv
import os
import hashlib
from datetime import datetime


class UserManager:
    def __init__(self):
        self.users_file = "data/users.csv"
        self.scores_file = "data/scores.csv"
        self.current_user = None
        
        os.makedirs("data", exist_ok=True)
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Inicializa los archivos CSV si no existen"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password_hash', 'created_at'])
        
        if not os.path.exists(self.scores_file):
            with open(self.scores_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'score', 'date', 'time_played'])
    
    def _hash_password(self, password):
        """Genera hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """
        Registra un nuevo usuario
        Retorna: (success: bool, message: str)
        """
        if not username or not password:
            return False, "Usuario y contraseña no pueden estar vacíos"
        
        if len(username) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"
        
        if len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres"
        
        if self._user_exists(username):
            return False, "El usuario ya existe"
        
        password_hash = self._hash_password(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.users_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([username, password_hash, created_at])
        
        return True, f"Usuario '{username}' registrado exitosamente"
    
    def login(self, username, password):
        """
        Inicia sesión con un usuario
        Retorna: (success: bool, message: str)
        """
        if not username or not password:
            return False, "Usuario y contraseña no pueden estar vacíos"
        
        password_hash = self._hash_password(password)
        
        with open(self.users_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    if row['password_hash'] == password_hash:
                        self.current_user = username
                        return True, f"¡Bienvenido {username}!"
                    else:
                        return False, "Contraseña incorrecta"
        
        return False, "Usuario no encontrado"
    
    def logout(self):
        """Cierra sesión del usuario actual"""
        self.current_user = None
    
    def _user_exists(self, username):
        """Verifica si un usuario existe"""
        if not os.path.exists(self.users_file):
            return False
        
        with open(self.users_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    return True
        return False
    
    def save_score(self, score, time_played=0):
        """
        Guarda la puntuación del usuario actual
        
        Args:
            score: Puntuación obtenida
            time_played: Tiempo jugado en segundos (opcional)
        """
        if not self.current_user:
            print("No hay usuario logueado")
            return False
        
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.scores_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([self.current_user, score, date, time_played])
        
        print(f"Puntuación guardada: {score} puntos")
        return True
    
    def get_user_best_score(self, username=None):
        """
        Obtiene la mejor puntuación de un usuario
        Si no se especifica username, usa el usuario actual
        """
        if username is None:
            username = self.current_user
        
        if not username:
            return 0
        
        best_score = 0
        
        if not os.path.exists(self.scores_file):
            return 0
        
        with open(self.scores_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    score = int(row['score'])
                    if score > best_score:
                        best_score = score
        
        return best_score
    
    def get_user_scores(self, username=None, limit=10):
        """
        Obtiene las últimas puntuaciones de un usuario
        
        Args:
            username: Usuario (None = usuario actual)
            limit: Cantidad máxima de scores a retornar
        
        Returns:
            Lista de tuplas (score, date, time_played)
        """
        if username is None:
            username = self.current_user
        
        if not username:
            return []
        
        scores = []
        
        if not os.path.exists(self.scores_file):
            return []
        
        with open(self.scores_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    scores.append({
                        'score': int(row['score']),
                        'date': row['date'],
                        'time_played': int(row['time_played']) if row['time_played'] else 0
                    })
        
        # Ordenar por puntuación descendente
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        return scores[:limit]
    
    def get_global_highscores(self, limit=10):
        """
        Obtiene el ranking global de mejores puntuaciones
        
        Returns:
            Lista de tuplas (username, score, date)
        """
        scores = []
        
        if not os.path.exists(self.scores_file):
            return []
        
        with open(self.scores_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                scores.append({
                    'username': row['username'],
                    'score': int(row['score']),
                    'date': row['date']
                })
        
        # Ordenar por puntuación descendente
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        return scores[:limit]
    
    def get_user_stats(self, username=None):
        """
        Obtiene estadísticas del usuario
        
        Returns:
            dict con: total_games, best_score, average_score, total_time
        """
        if username is None:
            username = self.current_user
        
        if not username:
            return None
        
        scores = []
        total_time = 0
        
        if not os.path.exists(self.scores_file):
            return {
                'total_games': 0,
                'best_score': 0,
                'average_score': 0,
                'total_time': 0
            }
        
        with open(self.scores_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    scores.append(int(row['score']))
                    total_time += int(row['time_played']) if row['time_played'] else 0
        
        if not scores:
            return {
                'total_games': 0,
                'best_score': 0,
                'average_score': 0,
                'total_time': 0
            }
        
        return {
            'total_games': len(scores),
            'best_score': max(scores),
            'average_score': sum(scores) // len(scores),
            'total_time': total_time
        }
    
    def is_logged_in(self):
        """Verifica si hay un usuario logueado"""
        return self.current_user is not None
    
    def get_current_user(self):
        """Retorna el nombre del usuario actual"""
        return self.current_user
