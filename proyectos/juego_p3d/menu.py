from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode, Vec4

class MainMenu:
    def __init__(self, base, start_game_callback):
        self.base = base
        self.start_game_callback = start_game_callback

        self.base.setBackgroundColor(Vec4(0.1, 0.1, 0.2, 1))

        self.title = OnscreenText(
            text="CRYSTAL BREAKER",
            pos=(0, 0.5), scale=0.15,
            fg=(0.6, 0.9, 1.0, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )

        self.subtitle = OnscreenText(
            text="WIP",
            pos=(0, 0.3), scale=0.08,
            fg=(1, 1, 0.5, 1),
            align=TextNode.ACenter
        )

        self.start_button = DirectButton(
            text="INICIAR JUEGO",
            scale=0.08,
            pos=(0, 0, 0),
            command=self.on_start_click,
            frameColor=(0.2, 0.5, 0.8, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )

        self.instructions = OnscreenText(
            text="CONTROLES:\n\n"
                 "Mouse - Apuntar\n"
                 "Click Izquierdo - Disparar\n"
                 "ESC - Pausa\n\n"
                 "Version dedicada a smash hit y boca juniors",
            pos=(0, -0.4), scale=0.06,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter
        )

        self.base.accept('enter', self.on_start_click)
        self.base.accept('space', self.on_start_click)

    def on_start_click(self):
        """Cuando se hace clic en iniciar"""
        self.hide()
        self.start_game_callback()

    def hide(self):
        """Ocultar el menú"""
        self.title.destroy()
        self.subtitle.destroy()
        self.start_button.destroy()
        self.instructions.destroy()
        self.base.ignore('enter')
        self.base.ignore('space')

class GameOverScreen:
    def __init__(self, base, score, restart_callback):
        self.base = base
        self.restart_callback = restart_callback

        self.bg = OnscreenText(
            text="",
            pos=(0, 0), scale=10,
            fg=(0, 0, 0, 0.8),
            align=TextNode.ACenter
        )

        self.game_over_text = OnscreenText(
            text="GAME OVER",
            pos=(0, 0.3), scale=0.15,
            fg=(1, 0.2, 0.2, 1),
            shadow=(0, 0, 0, 1),
            align=TextNode.ACenter
        )

        self.score_text = OnscreenText(
            text=f"Puntuación Final: {score}",
            pos=(0, 0.1), scale=0.1,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter
        )

        self.restart_button = DirectButton(
            text="REINTENTAR",
            scale=0.08,
            pos=(0, 0, -0.2),
            command=self.on_restart_click,
            frameColor=(0.2, 0.8, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=1
        )

        self.instructions = OnscreenText(
            text="Presiona ENTER para reintentar\nPresiona Q para salir",
            pos=(0, -0.5), scale=0.06,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter
        )

        self.base.accept('enter', self.on_restart_click)
        self.base.accept('q', self.quit_game)

    def on_restart_click(self):
        """Reiniciar el juego"""
        self.hide()
        self.restart_callback()

    def quit_game(self):
        """Salir del juego"""
        import sys
        sys.exit()

    def hide(self):
        """Ocultar la pantalla de game over"""
        self.bg.destroy()
        self.game_over_text.destroy()
        self.score_text.destroy()
        self.restart_button.destroy()
        self.instructions.destroy()
        self.base.ignore('enter')
        self.base.ignore('q')
