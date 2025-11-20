"""
SceneManager - Maneja la configuración visual de la escena
Responsabilidades:
- Color de fondo
- Creación de geometría (piso, paredes, techo)
- Sistema de iluminación (ambient, directional lights)
- Posición y orientación de la cámara
"""

from panda3d.core import Vec4, CardMaker, AmbientLight, DirectionalLight


class SceneManager:
    def __init__(self, base):
        self.base = base
        
        # Referencias a las luces para poder limpiarlas
        self.ambient_np = None
        self.dlnp = None
        self.dlnp2 = None
        
    def setup(self):
        """Configura toda la escena visual"""
        self._setup_background()
        self._setup_geometry()
        self._setup_lighting()
        self._setup_camera()
        
    def _setup_background(self):
        """Configura el color de fondo"""
        self.base.setBackgroundColor(Vec4(0.85, 0.88, 0.92, 1))
        
    def _setup_geometry(self):
        """Crea el piso, paredes y techo del túnel"""
        # Piso
        cm = CardMaker('floor')
        cm.setFrame(-50, 50, -50, 50)
        floor = self.base.render.attachNewNode(cm.generate())
        floor.setPos(0, 100, 0)
        floor.setHpr(0, -90, 0)
        floor.setColor(0.65, 0.68, 0.72, 1)

        # Pared izquierda
        left_wall = CardMaker('left_wall')
        left_wall.setFrame(0, 500, 0, 10)
        left = self.base.render.attachNewNode(left_wall.generate())
        left.setPos(-8, 0, 0)
        left.setHpr(90, 0, 0)
        left.setColor(0.55, 0.58, 0.62, 1)

        # Pared derecha
        right_wall = CardMaker('right_wall')
        right_wall.setFrame(0, 500, 0, 10)
        right = self.base.render.attachNewNode(right_wall.generate())
        right.setPos(8, 0, 0)
        right.setHpr(-90, 0, 0)
        right.setColor(0.55, 0.58, 0.62, 1)

        # Techo
        ceiling = CardMaker('ceiling')
        ceiling.setFrame(-8, 8, 0, 500)
        ceil = self.base.render.attachNewNode(ceiling.generate())
        ceil.setPos(0, 0, 6)
        ceil.setP(-90)
        ceil.setColor(0.6, 0.63, 0.67, 1)
        
    def _setup_lighting(self):
        """Configura el sistema de iluminación"""
        # Luz ambiental (iluminación general)
        ambient = AmbientLight("ambient")
        ambient.setColor((0.75, 0.78, 0.82, 1))
        self.ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(self.ambient_np)

        # Luz direccional principal
        dlight = DirectionalLight("dlight")
        dlight.setColor((0.9, 0.92, 0.95, 1))
        self.dlnp = self.base.render.attachNewNode(dlight)
        self.dlnp.setHpr(0, -60, 0)
        self.base.render.setLight(self.dlnp)

        # Luz direccional secundaria
        dlight2 = DirectionalLight("dlight2")
        dlight2.setColor((0.4, 0.42, 0.45, 1))
        self.dlnp2 = self.base.render.attachNewNode(dlight2)
        self.dlnp2.setHpr(180, -30, 0)
        self.base.render.setLight(self.dlnp2)
        
    def _setup_camera(self):
        """Configura la posición inicial de la cámara"""
        self.base.camera.setPos(0, -5, 2)
        self.base.camera.lookAt(0, 20, 2)
        
    def cleanup(self):
        """Limpia las luces de la escena"""
        if self.ambient_np:
            self.base.render.clearLight(self.ambient_np)
            self.ambient_np.removeNode()
        if self.dlnp:
            self.base.render.clearLight(self.dlnp)
            self.dlnp.removeNode()
        if self.dlnp2:
            self.base.render.clearLight(self.dlnp2)
            self.dlnp2.removeNode()
