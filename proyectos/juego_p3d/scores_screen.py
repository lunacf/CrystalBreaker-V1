"""
ScoresScreen - Pantalla para ver historial de puntuaciones y ranking
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectFrame
from panda3d.core import TextNode, Vec4, CardMaker, TransparencyAttrib


class ScoresScreen:
    def __init__(self, base, user_manager, back_callback):
        self.base = base
        self.user_manager = user_manager
        self.back_callback = back_callback
        
        self.create_background()
        
        self.title = OnscreenText(
            text="PUNTUACIONES",
            pos=(0, 0.85), scale=0.14,
            fg=(1, 0.9, 0.3, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )
        
        current_user = user_manager.get_current_user()
        self.user_text = OnscreenText(
            text=f"Jugador: {current_user}",
            pos=(0, 0.7), scale=0.08,
            fg=(0.3, 1, 0.3, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter
        )
        
        # Panel izquierdo - Estadísticas personales
        self.left_panel = DirectFrame(
            frameColor=(0.1, 0.15, 0.25, 0.9),
            frameSize=(-0.32, 0.32, -0.48, 0.48),
            pos=(-0.7, 0, -0.05)
        )
        
        stats = user_manager.get_user_stats()
        stats_title = OnscreenText(
            text="ESTADÍSTICAS",
            pos=(0, 0.38), scale=0.055,
            fg=(0.6, 0.9, 1.0, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        
        OnscreenText(
            text=f"Mejor Puntuación",
            pos=(0, 0.22), scale=0.042,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        OnscreenText(
            text=f"{stats['best_score']}",
            pos=(0, 0.13), scale=0.06,
            fg=(1, 1, 0.3, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        
        OnscreenText(
            text=f"Partidas Jugadas",
            pos=(0, -0.02), scale=0.042,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        OnscreenText(
            text=f"{stats['total_games']}",
            pos=(0, -0.11), scale=0.06,
            fg=(0.3, 1, 0.3, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        
        OnscreenText(
            text=f"Promedio",
            pos=(0, -0.26), scale=0.042,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        OnscreenText(
            text=f"{stats['average_score']}",
            pos=(0, -0.35), scale=0.06,
            fg=(0.3, 0.8, 1, 1),
            align=TextNode.ACenter,
            parent=self.left_panel
        )
        
        # Panel central - Mejores personales
        self.center_panel = DirectFrame(
            frameColor=(0.15, 0.1, 0.25, 0.9),
            frameSize=(-0.32, 0.32, -0.48, 0.48),
            pos=(0, 0, -0.05)
        )
        
        personal_title = OnscreenText(
            text="MIS MEJORES 5",
            pos=(0, 0.38), scale=0.055,
            fg=(1, 0.9, 0.3, 1),
            align=TextNode.ACenter,
            parent=self.center_panel
        )
        
        user_scores = user_manager.get_user_scores(limit=5)
        
        if user_scores:
            y_pos = 0.2
            for i, score in enumerate(user_scores, 1):
                date_short = score['date'].split()[0]
                OnscreenText(
                    text=f"{i}. {score['score']} pts - {date_short}",
                    pos=(0, y_pos), scale=0.045,
                    fg=(0.9, 0.9, 0.9, 1),
                    align=TextNode.ACenter,
                    parent=self.center_panel
                )
                y_pos -= 0.13
        else:
            OnscreenText(
                text="Sin partidas",
                pos=(0, 0), scale=0.05,
                fg=(0.7, 0.7, 0.7, 1),
                align=TextNode.ACenter,
                parent=self.center_panel
            )
        
        # Panel derecho - Ranking global
        self.right_panel = DirectFrame(
            frameColor=(0.1, 0.2, 0.15, 0.9),
            frameSize=(-0.32, 0.32, -0.48, 0.48),
            pos=(0.7, 0, -0.05)
        )
        
        ranking_title = OnscreenText(
            text="TOP 10 GLOBAL",
            pos=(0, 0.38), scale=0.055,
            fg=(0.3, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.right_panel
        )
        
        global_scores = user_manager.get_global_highscores(limit=10)
        
        if global_scores:
            y_pos = 0.22
            for i, entry in enumerate(global_scores[:8], 1):
                user = entry['username']
                score = entry['score']
                color = (1, 1, 0.3, 1) if user == current_user else (0.9, 0.9, 0.9, 1)
                prefix = "→ " if user == current_user else ""
                OnscreenText(
                    text=f"{prefix}{i}. {user}: {score}",
                    pos=(0, y_pos), scale=0.042,
                    fg=color,
                    align=TextNode.ACenter,
                    parent=self.right_panel
                )
                y_pos -= 0.09
        else:
            OnscreenText(
                text="Sin datos",
                pos=(0, 0), scale=0.05,
                fg=(0.7, 0.7, 0.7, 1),
                align=TextNode.ACenter,
                parent=self.right_panel
            )
        
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
    
    def create_background(self):
        """Crea fondo de puntuaciones"""
        cm = CardMaker('scores_background')
        cm.setFrame(-2, 2, -1.5, 1.5)
        self.background = self.base.aspect2d.attachNewNode(cm.generate())
        self.background.setScale(2.5)
        self.background.setPos(0, 0, 0)
        
        try:
            tex = self.base.loader.loadTexture("images/fondo_main.png")
            self.background.setTexture(tex)
            self.background.setTransparency(TransparencyAttrib.MAlpha)
        except:
            self.base.setBackgroundColor(Vec4(0.05, 0.05, 0.15, 1))
        
        self.background.setBin('background', 0)
    
    def on_back_click(self):
        """Volver al menú principal"""
        self.hide()
        self.back_callback()
    
    def hide(self):
        """Ocultar la pantalla"""
        self.title.destroy()
        self.user_text.destroy()
        self.left_panel.destroy()
        self.center_panel.destroy()
        self.right_panel.destroy()
        self.back_button.destroy()
        self.instructions.destroy()
        if hasattr(self, 'background'):
            self.background.removeNode()
        
        self.base.ignore('escape')
        self.base.ignore('q')
