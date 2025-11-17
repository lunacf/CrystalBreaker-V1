from direct.showbase.ShowBase import ShowBase
from menu import MainMenu, GameOverScreen
from sounds import SoundManager
from user_manager import UserManager
from login_screen import LoginScreen
import time

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.sound_manager = None
       
        from panda3d.core import WindowProperties
        props = WindowProperties()
        props.setTitle("Crystal Breaker - CABJ Edition")
        self.win.requestProperties(props)

        self.game = None
        self.game_start_time = 0  # Para tracking de tiempo jugado
        
        # Sistema de usuarios
        self.user_manager = UserManager()
        
        # Mostrar pantalla de login
        self.show_login_screen()

    def show_login_screen(self):
        """Muestra la pantalla de login"""
        self.login_screen = LoginScreen(self, self.user_manager, self.show_main_menu)
    
    def show_main_menu(self):
        """Dibujo menú principal"""
        self.menu = MainMenu(self, self.user_manager, self.start_game)

    def start_game(self):
        """Inicio del juego"""
        # Limpiar juego anterior si existe
        if self.game:
            self.game.cleanup()
            self.game = None

        # Registrar tiempo de inicio
        self.game_start_time = time.time()

        if not self.sound_manager:
            self.sound_manager = SoundManager(self)
            self.sound_manager.play_music("sounds/lgsa.mp3")
            self.sound_manager.setVolume(0.3)
            self.sound_manager.music.setLoop(True)
        from game import Game
        self.game = Game(self)

    def show_game_over(self, score):
        """Dibujo pantalla de game over"""
        # Calcular tiempo jugado
        time_played = int(time.time() - self.game_start_time)
        
        # Guardar puntuación
        self.user_manager.save_score(score, time_played)
        
        # Mostrar pantalla de game over
        self.game_over_screen = GameOverScreen(
            self, 
            score, 
            self.user_manager,
            self.restart_game
        )

    def restart_game(self):
        """Reiniciar el juego"""
        self.start_game()

    def return_to_menu(self):
        """Volver al menú principal después de presionar Q en el juego"""
        if hasattr(self, 'game') and self.game:
            self.game = None
        self.show_main_menu()

if __name__ == "__main__":
    app = MyApp()
    app.run()
