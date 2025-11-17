"""
GameState - Maneja el estado del juego
Responsabilidades:
- Puntuación (score)
- Munición (ammo)
- Estado de pausa
- Estado de game over
- Interfaz de usuario (UI)
"""

from direct.gui.OnscreenText import OnscreenText


class GameState:
    def __init__(self, base):
        self.base = base
        
        # Estado del juego
        self.score = 0
        self.ammo = 20
        self.game_paused = False
        self.game_over = False
        
        # Referencias a UI
        self.title_text = None
        self.crystal_counter = None
        self.score_text = None
        self.ammo_text = None
        self.pause_text = None
        self.pause_bg = None
        
    def setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        self.title_text = OnscreenText(
            text="Crystal Breaker Boca Version", 
            pos=(0, 0.9), 
            scale=0.08,
            fg=(1, 1, 0, 1), 
            align=1, 
            mayChange=False
        )

        self.crystal_counter = OnscreenText(
            text="Cristales: 8", 
            pos=(1.2, 0.9), 
            scale=0.06,
            fg=(0, 1, 0, 1), 
            align=0, 
            mayChange=True
        )

        self.score_text = OnscreenText(
            text="Puntuación: 0", 
            pos=(-1.3, 0.8), 
            scale=0.07,
            fg=(0, 0.8, 1, 1), 
            align=0, 
            mayChange=True
        )
        
        self.ammo_text = OnscreenText(
            text="Disparos: 20", 
            pos=(-1.3, 0.65), 
            scale=0.07,
            fg=(1, 0.5, 0, 1), 
            align=0, 
            mayChange=True
        )
        
    def add_score(self, points):
        """Añade puntos al score"""
        self.score += points
        self.score_text.setText(f"Puntos: {self.score}")
        
    def subtract_score(self, points):
        """Resta puntos del score (no baja de 0)"""
        self.score = max(0, self.score - points)
        self.score_text.setText(f"Puntos: {self.score}")
        
    def add_ammo(self, amount):
        """Añade munición"""
        self.ammo += amount
        self.ammo_text.setText(f"Disparos: {self.ammo}")
        
    def use_ammo(self):
        """Usa una unidad de munición. Retorna True si había munición disponible"""
        if self.ammo > 0:
            self.ammo -= 1
            self.ammo_text.setText(f"Disparos: {self.ammo}")
            return True
        return False
        
    def update_crystal_counter(self, count):
        """Actualiza el contador de cristales activos"""
        self.crystal_counter.setText(f"Cristales: {count}")
        
    def show_pause_menu(self):
        """Muestra el menú de pausa"""
        self.pause_text = OnscreenText(
            text="PAUSA\n\nESC = Continuar\nQ = Salir",
            pos=(0, 0), 
            scale=0.12,
            fg=(0, 0.8, 1, 1), 
            align=2,
            mayChange=False
        )
        self.pause_bg = OnscreenText(
            text="", 
            pos=(0, 0), 
            scale=10,
            fg=(0, 0, 0, 0.7), 
            align=1,
            mayChange=False
        )
        
    def hide_pause_menu(self):
        """Oculta el menú de pausa"""
        if self.pause_text:
            self.pause_text.destroy()
            self.pause_text = None
        if self.pause_bg:
            self.pause_bg.destroy()
            self.pause_bg = None
            
    def cleanup(self):
        """Limpia los elementos de UI"""
        if self.title_text:
            self.title_text.destroy()
        if self.crystal_counter:
            self.crystal_counter.destroy()
        if self.score_text:
            self.score_text.destroy()
        if self.ammo_text:
            self.ammo_text.destroy()
        if self.pause_text:
            self.pause_text.destroy()
        if self.pause_bg:
            self.pause_bg.destroy()
