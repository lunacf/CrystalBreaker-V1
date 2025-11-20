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
        self.game_start_time = 0
        self.user_manager = UserManager()
        
        self.show_login_screen()

    def show_login_screen(self):
        """Muestra pantalla de login"""
        self.login_screen = LoginScreen(self, self.user_manager, self.show_main_menu)
    
    def show_main_menu(self):
        """Muestra menú principal"""
        self.menu = MainMenu(self, self.user_manager, self.start_game)

    def start_game(self):
        """Inicia el juego"""
        if self.game:
            self.game.cleanup()
            self.game = None

        self.game_start_time = time.time()

        if not self.sound_manager:
            self.sound_manager = SoundManager(self)
            self.sound_manager.play_music("sounds/lgsa.mp3")
            self.sound_manager.setVolume(0.3)
            self.sound_manager.music.setLoop(True)
        from game import Game
        self.game = Game(self)

    def show_game_over(self, score):
        """Muestra pantalla de game over"""
        time_played = int(time.time() - self.game_start_time)
        self.user_manager.save_score(score, time_played)
        
        self.game_over_screen = GameOverScreen(
            self, 
            score, 
            self.user_manager,
            self.restart_game
        )

    def restart_game(self):
        """Reinicia el juego"""
        self.start_game()

    def return_to_menu(self):
        """Vuelve al menú principal"""
        if hasattr(self, 'game') and self.game:
            self.game = None
        self.show_main_menu()

if __name__ == "__main__":
    app = MyApp()
    app.run()
