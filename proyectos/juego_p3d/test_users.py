"""
Script de prueba para el sistema de usuarios y puntuaciones
Ejecuta: python test_users.py
"""

from user_manager import UserManager

def test_user_system():
    print("=== Test del Sistema de Usuarios ===\n")
    
    um = UserManager()
    
    print("1. Probando registro de usuario...")
    success, msg = um.register_user("test_user", "test1234")
    print(f"   {msg}")
    assert success, "Registro falló"
    
    print("\n2. Probando registro duplicado...")
    success, msg = um.register_user("test_user", "otherpass")
    print(f"   {msg}")
    assert not success, "Debería fallar con usuario duplicado"
    
    print("\n3. Probando login correcto...")
    success, msg = um.login("test_user", "test1234")
    print(f"   {msg}")
    assert success, "Login falló"
    assert um.is_logged_in(), "Usuario no está logueado"
    
    print("\n4. Probando login con contraseña incorrecta...")
    um.logout()
    success, msg = um.login("test_user", "wrongpass")
    print(f"   {msg}")
    assert not success, "Debería fallar con contraseña incorrecta"
    
    print("\n5. Probando guardar puntuaciones...")
    um.login("test_user", "test1234")
    um.save_score(100, 60)
    um.save_score(250, 120)
    um.save_score(180, 90)
    print("   Puntuaciones guardadas: 100, 250, 180")
    
    print("\n6. Obteniendo mejor puntuación...")
    best = um.get_user_best_score()
    print(f"   Mejor puntuación: {best}")
    assert best == 250, f"Debería ser 250, pero es {best}"
    
    print("\n7. Obteniendo estadísticas...")
    stats = um.get_user_stats()
    print(f"   Total partidas: {stats['total_games']}")
    print(f"   Mejor puntuación: {stats['best_score']}")
    print(f"   Promedio: {stats['average_score']}")
    print(f"   Tiempo total: {stats['total_time']}s")
    
    print("\n8. Obteniendo historial de puntuaciones...")
    scores = um.get_user_scores(limit=5)
    for i, score in enumerate(scores, 1):
        print(f"   {i}. {score['score']} puntos - {score['date']}")
    
    print("\n9. Obteniendo ranking global...")
    highscores = um.get_global_highscores(limit=5)
    for i, entry in enumerate(highscores, 1):
        print(f"   {i}. {entry['username']}: {entry['score']} puntos")
    
    print("\nTodos los tests pasaron correctamente")
    print("\nArchivos generados:")
    print("   - data/users.csv")
    print("   - data/scores.csv")

if __name__ == "__main__":
    test_user_system()
