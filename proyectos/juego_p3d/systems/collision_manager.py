"""
CollisionManager - Maneja todas las colisiones del juego
Responsabilidades:
- Configuración del sistema de colisiones
- Manejo de colisión proyectil-cristal
- Manejo de colisión proyectil-barrier
- Manejo de colisión jugador-barrier
"""

from panda3d.core import CollisionTraverser, CollisionHandlerEvent


class CollisionManager:
    def __init__(self, base):
        self.base = base
        
        # Sistema de colisiones
        self.cTrav = CollisionTraverser()
        self.handler = CollisionHandlerEvent()
        
        # Configurar patrones de colisión
        self.handler.addInPattern('%fn-into-%in')
        self.handler.addInPattern('projectile-into-crystal')
        self.handler.addInPattern('projectile-into-barrier')
        self.handler.addInPattern('player-into-barrier')
        
    def setup_collision_handlers(self, on_projectile_hit_crystal, 
                                 on_projectile_hit_barrier, 
                                 on_player_hit_barrier):
        """Configura los callbacks para las colisiones"""
        self.base.accept('projectile-into-crystal', on_projectile_hit_crystal)
        self.base.accept('projectile-into-barrier', on_projectile_hit_barrier)
        self.base.accept('player-into-barrier', on_player_hit_barrier)
        
    def update(self):
        """Actualiza el traverser de colisiones"""
        self.cTrav.traverse(self.base.render)
        
    # ========== HANDLERS DE COLISIÓN ==========
    
    @staticmethod
    def handle_projectile_crystal_collision(entry, on_crystal_broken):
        """
        Maneja colisión entre proyectil y cristal
        
        Args:
            entry: CollisionEntry de Panda3D
            on_crystal_broken: Callback que se llama cuando se rompe un cristal
        """
        print("¡Colisión proyectil-cristal detectada!")
        try:
            from_np = entry.getFromNodePath().getParent()
            into_np = entry.getIntoNodePath().getParent()
        except Exception as e:
            print(f"Error obteniendo nodos: {e}")
            return

        proj = from_np.getPythonTag('projectile_ref')
        crystal = into_np.getPythonTag('crystal_ref')

        if proj:
            print("Desactivando proyectil")
            proj.deactivate()
            
        if crystal and not crystal.broken:
            print("Rompiendo cristal - ¡+10 puntos! +1 munición")
            crystal.break_apart()
            on_crystal_broken()
            
    @staticmethod
    def handle_projectile_barrier_collision(entry, on_barrier_broken):
        """
        Maneja colisión entre proyectil y barrier
        
        Args:
            entry: CollisionEntry de Panda3D
            on_barrier_broken: Callback que se llama cuando se rompe un barrier
        """
        try:
            from_np = entry.getFromNodePath().getParent()
            into_np = entry.getIntoNodePath().getParent()
        except Exception as e:
            print(f"Error obteniendo nodos: {e}")
            return

        proj = from_np.getPythonTag('projectile_ref')
        barrier = into_np.getPythonTag('barrier_ref')

        if proj:
            proj.deactivate()

        if barrier and not barrier.broken:
            print("¡Barrier roto! +5 puntos")
            barrier.break_apart()
            on_barrier_broken()
