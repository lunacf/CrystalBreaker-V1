from direct.showbase.ShowBase import ShowBase
from menu import MainMenu, GameOverScreen

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Smash Hit (wip)")
        self.win.requestProperties(props)

        self.game = None
        self.show_main_menu()

    def show_main_menu(self):
        """Mostrar el menú principal"""
        self.menu = MainMenu(self, self.start_game)

    def start_game(self):
        """Iniciar el juego"""
        if self.game:
            self.game.cleanup()

        from game import Game
        self.game = Game(self)

    def show_game_over(self, score):
        """Mostrar pantalla de game over"""
        self.game_over_screen = GameOverScreen(self, score, self.restart_game)

    def restart_game(self):
        """Reiniciar el juego"""
        self.start_game()

if __name__ == "__main__":
    app = MyApp()
    app.run()
