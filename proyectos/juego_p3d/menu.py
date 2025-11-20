from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode, Vec4, CardMaker, TransparencyAttrib

class MainMenu:
    def __init__(self, base, user_manager, start_game_callback):
        self.base = base
        self.user_manager = user_manager
        self.start_game_callback = start_game_callback

        self.create_background()

        self.title = OnscreenText(
            text="Crystal Breaker - CABJ Edition",
            pos=(0, 0.7), scale=0.15,
            fg=(0.6, 0.9, 1.0, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )
        
        current_user = user_manager.get_current_user()
        self.user_text = OnscreenText(
            text=f"Jugador: {current_user}",
            pos=(0, 0.5), scale=0.08,
            fg=(1, 1, 0.5, 1),
            align=TextNode.ACenter
        )
        
        best_score = user_manager.get_user_best_score()
        stats = user_manager.get_user_stats()
        self.stats_text = OnscreenText(
            text=f"Mejor Puntuación: {best_score}\nPartidas Jugadas: {stats['total_games']}",
            pos=(0, 0.3), scale=0.06,
            fg=(0.7, 1, 0.7, 1),
            align=TextNode.ACenter
        )

        self.start_button = DirectButton(
            text="JUGAR",
            scale=0.08,
            pos=(0, 0, 0.05),
            command=self.on_start_click,
            frameColor=(0.2, 0.7, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        self.scores_button = DirectButton(
            text="VER PUNTUACIONES",
            scale=0.06,
            pos=(0, 0, -0.1),
            command=self.show_scores,
            frameColor=(0.3, 0.5, 0.8, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        self.logout_button = DirectButton(
            text="CERRAR SESIÓN",
            scale=0.06,
            pos=(0, 0, -0.22),
            command=self.on_logout_click,
            frameColor=(0.8, 0.4, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )

        self.instructions = OnscreenText(
            text="CONTROLES:\n"
                 "Mouse - Apuntar | Click - Disparar | ESC - Pausa\n\n"
                 "Versión dedicada a Smash Hit y Boca Juniors",
            pos=(0, -0.5), scale=0.05,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter
        )

        self.base.accept('enter', self.on_start_click)
        self.base.accept('space', self.on_start_click)

    def create_background(self):
        """Crea fondo del menú"""
        cm = CardMaker('menu_background')
        cm.setFrame(-2, 2, -1.5, 1.5)
        self.background = self.base.aspect2d.attachNewNode(cm.generate())
        self.background.setScale(2.5)
        self.background.setPos(0, 0, 0)
        
        try:
            tex = self.base.loader.loadTexture("fondo_main.png")
            self.background.setTexture(tex)
            self.background.setTransparency(TransparencyAttrib.MAlpha)
        except:
            self.base.setBackgroundColor(Vec4(0.05, 0.05, 0.15, 1))
        
        self.background.setBin('background', 0)

    def on_start_click(self):
        """Inicia el juego"""
        self.hide()
        self.start_game_callback()
    
    def show_scores(self):
        """Muestra la pantalla de puntuaciones"""
        self.hide()
        from scores_screen import ScoresScreen
        ScoresScreen(self.base, self.user_manager, self.show_menu_again)
    
    def on_logout_click(self):
        """Cierra sesión y vuelve al login"""
        self.hide()
        self.user_manager.logout()
        # Volver a la pantalla de login
        from login_screen import LoginScreen
        LoginScreen(self.base, self.user_manager, self.show_menu_again)
    
    def show_menu_again(self):
        """Vuelve a mostrar este menú"""
        self.__init__(self.base, self.user_manager, self.start_game_callback)

    def hide(self):
        """Ocultar el menú"""
        self.title.destroy()
        self.user_text.destroy()
        self.stats_text.destroy()
        self.start_button.destroy()
        self.scores_button.destroy()
        self.logout_button.destroy()
        self.instructions.destroy()
        if hasattr(self, 'background'):
            self.background.removeNode()
        self.base.ignore('enter')
        self.base.ignore('space')

class GameOverScreen:
    def __init__(self, base, score, user_manager, restart_callback):
        from direct.gui.DirectGui import DirectFrame
        
        self.base = base
        self.user_manager = user_manager
        self.restart_callback = restart_callback

        self.bg = OnscreenText(
            text="",
            pos=(0, 0), scale=10,
            fg=(0, 0, 0, 0.6),
            align=2
        )

        self.panel = DirectFrame(
            frameColor=(0.15, 0.05, 0.05, 0.95),
            frameSize=(-1.2, 1.2, -0.7, 0.7),
            pos=(0, 0, 0)
        )
        
        self.border = DirectFrame(
            frameColor=(1, 0.2, 0.2, 1),
            frameSize=(-1.25, 1.25, -0.75, 0.75),
            pos=(0, 0, 0)
        )
        self.border.reparentTo(self.panel)
        self.border.setBin('fixed', 0)
        self.panel.setBin('fixed', 1)

        self.game_over_text = OnscreenText(
            text="GAME OVER",
            pos=(0, 0.45), scale=0.15,
            fg=(1, 0.2, 0.2, 1),
            shadow=(0, 0, 0, 1),
            align=2,
            parent=self.panel
        )

        self.score_text = OnscreenText(
            text=f"Puntuación: {score}",
            pos=(0, 0.25), scale=0.1,
            fg=(1, 1, 0, 1),
            align=2,
            parent=self.panel
        )
        
        best_score = user_manager.get_user_best_score()
        if score > best_score:
            record_text = "¡NUEVO RÉCORD!"
            record_color = (0.3, 1, 0.3, 1)
        elif score == best_score and best_score > 0:
            record_text = "¡Igualaste tu récord!"
            record_color = (0.5, 0.8, 1, 1)
        else:
            record_text = f"Tu récord: {best_score}"
            record_color = (0.7, 0.7, 0.7, 1)
        
        self.record_text = OnscreenText(
            text=record_text,
            pos=(0, 0.1), scale=0.08,
            fg=record_color,
            align=2,
            parent=self.panel
        )

        self.restart_button = DirectButton(
            text="REINTENTAR",
            scale=0.08,
            pos=(0, 0, -0.15),
            command=self.on_restart_click,
            frameColor=(0.2, 0.8, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1,
            parent=self.panel
        )

        self.menu_button = DirectButton(
            text="MENÚ PRINCIPAL",
            scale=0.08,
            pos=(0, 0, -0.35),
            command=self.return_to_menu,
            frameColor=(0.8, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1,
            parent=self.panel
        )

        self.instructions = OnscreenText(
            text="ENTER = Reintentar | Q = Menú",
            pos=(0, -0.55), scale=0.06,
            fg=(0.9, 0.9, 0.9, 1),
            align=2,
            parent=self.panel
        )

        self.base.accept('enter', self.on_restart_click)
        self.base.accept('q', self.return_to_menu)

    def on_restart_click(self):
        """Reiniciar el juego"""
        self.hide()
        self.restart_callback()

    def return_to_menu(self):
        """Volver al menú principal"""
        self.hide()
        self.base.return_to_menu()

    def hide(self):
        """Ocultar la pantalla de game over"""
        self.bg.destroy()
        self.panel.destroy()
        self.border.destroy()
        self.game_over_text.destroy()
        self.score_text.destroy()
        self.record_text.destroy()
        self.restart_button.destroy()
        self.menu_button.destroy()
        self.instructions.destroy()
        self.base.ignore('enter')
        self.base.ignore('q')
