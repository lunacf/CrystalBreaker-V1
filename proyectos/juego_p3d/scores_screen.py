"""
ScoresScreen - Pantalla para ver historial de puntuaciones y ranking
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode, Vec4


class ScoresScreen:
    def __init__(self, base, user_manager, back_callback):
        self.base = base
        self.user_manager = user_manager
        self.back_callback = back_callback
        
        # Fondo
        self.base.setBackgroundColor(Vec4(0.05, 0.05, 0.15, 1))
        
        # Título
        self.title = OnscreenText(
            text="PUNTUACIONES",
            pos=(0, 0.8), scale=0.12,
            fg=(0.6, 0.9, 1.0, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )
        
        # Usuario actual
        current_user = user_manager.get_current_user()
        self.user_text = OnscreenText(
            text=f"Jugador: {current_user}",
            pos=(0, 0.65), scale=0.07,
            fg=(1, 1, 0.5, 1),
            align=TextNode.ACenter
        )
        
        # Estadísticas personales
        stats = user_manager.get_user_stats()
        stats_text = (
            f"═══ TUS ESTADÍSTICAS ═══\n\n"
            f"Mejor Puntuación: {stats['best_score']}\n"
            f"Partidas Jugadas: {stats['total_games']}\n"
            f"Promedio: {stats['average_score']}\n"
            f"Tiempo Total: {stats['total_time'] // 60} min"
        )
        
        self.stats_text = OnscreenText(
            text=stats_text,
            pos=(-0.6, 0.35), scale=0.05,
            fg=(0.7, 1, 0.7, 1),
            align=TextNode.ALeft
        )
        
        # Top 5 puntuaciones personales
        user_scores = user_manager.get_user_scores(limit=5)
        personal_scores_text = "═══ TUS MEJORES 5 ═══\n\n"
        
        if user_scores:
            for i, score in enumerate(user_scores, 1):
                date_short = score['date'].split()[0]  # Solo la fecha
                personal_scores_text += f"{i}. {score['score']} pts - {date_short}\n"
        else:
            personal_scores_text += "Aún no has jugado"
        
        self.personal_scores = OnscreenText(
            text=personal_scores_text,
            pos=(-0.6, 0.0), scale=0.045,
            fg=(0.9, 0.9, 0.9, 1),
            align=TextNode.ALeft
        )
        
        # Ranking global
        global_scores = user_manager.get_global_highscores(limit=10)
        ranking_text = "═══ TOP 10 GLOBAL ═══\n\n"
        
        if global_scores:
            for i, entry in enumerate(global_scores, 1):
                user = entry['username']
                score = entry['score']
                # Destacar al usuario actual
                if user == current_user:
                    ranking_text += f"→ {i}. {user}: {score} pts ←\n"
                else:
                    ranking_text += f"  {i}. {user}: {score} pts\n"
        else:
            ranking_text += "No hay puntuaciones aún"
        
        self.ranking_text = OnscreenText(
            text=ranking_text,
            pos=(0.6, 0.35), scale=0.045,
            fg=(1, 0.9, 0.5, 1),
            align=TextNode.ALeft
        )
        
        # Botón Volver
        self.back_button = DirectButton(
            text="VOLVER",
            scale=0.07,
            pos=(0, 0, -0.7),
            command=self.on_back_click,
            frameColor=(0.3, 0.3, 0.6, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        # Instrucciones
        self.instructions = OnscreenText(
            text="Presiona ESC para volver",
            pos=(0, -0.85), scale=0.05,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter
        )
        
        # Controles
        self.base.accept('escape', self.on_back_click)
        self.base.accept('q', self.on_back_click)
    
    def on_back_click(self):
        """Volver al menú principal"""
        self.hide()
        self.back_callback()
    
    def hide(self):
        """Ocultar la pantalla"""
        self.title.destroy()
        self.user_text.destroy()
        self.stats_text.destroy()
        self.personal_scores.destroy()
        self.ranking_text.destroy()
        self.back_button.destroy()
        self.instructions.destroy()
        
        self.base.ignore('escape')
        self.base.ignore('q')
