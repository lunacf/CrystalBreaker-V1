from panda3d.core import CollisionNode, CollisionSphere, BitMask32, Point3
from direct.interval.LerpInterval import LerpHprInterval, LerpColorScaleInterval, LerpPosInterval
from direct.interval.MetaInterval import Sequence, Parallel
from direct.interval.FunctionInterval import Func

class PowerUpObstacle:
    """Obstáculo especial que otorga munición extra al ser destruido"""
    
    def __init__(self, base, position_tuple, cTrav, coll_handler, ammo_bonus=5):
        self.base = base
        self.pos = Point3(*position_tuple)
        self.destroyed = False
        self.ammo_bonus = ammo_bonus
        
        # Crear modelo visual - caja brillante dorada
        self.node = base.loader.loadModel("models/box")
        self.node.reparentTo(base.render)
        self.node.setScale(0.8, 0.8, 0.8)
        self.node.setPos(self.pos)
        
        # Color dorado/amarillo brillante para distinguirlo
        self.node.setColor(1.0, 0.85, 0.0, 1)
        
        # Añadir colisión (usar bit 0 como los cristales para que el proyectil lo detecte)
        cnode = CollisionNode('powerup')
        cnode.addSolid(CollisionSphere(0, 0, 0, 1.2))
        cnode.setIntoCollideMask(BitMask32.bit(0))
        self.collider = self.node.attachNewNode(cnode)
        
        # Guardar referencia para colisiones (necesario para que el sistema lo detecte)
        self.node.setPythonTag('powerup_ref', self)
        self.collider.setPythonTag('powerup_ref', self)
        
        # Animación de rotación continua
        self.rotation_interval = LerpHprInterval(
            self.node, 
            duration=2.0,
            hpr=(360, 0, 0),
            startHpr=(0, 0, 0)
        )
        self.rotation_interval.loop()
        
        # Efecto de pulso de brillo
        self.pulse_seq = Sequence(
            LerpColorScaleInterval(self.node, 0.5, (1.3, 1.3, 0.3, 1)),
            LerpColorScaleInterval(self.node, 0.5, (1.0, 1.0, 1.0, 1))
        )
        self.pulse_seq.loop()
    
    def destroy(self):
        """Destruir el power-up con efecto visual"""
        if self.destroyed:
            return
        
        self.destroyed = True
        
        # Detener animaciones
        if hasattr(self, 'rotation_interval'):
            self.rotation_interval.pause()
        if hasattr(self, 'pulse_seq'):
            self.pulse_seq.pause()
        
        # Efecto de explosión dorada
        particles = []
        for i in range(8):
            try:
                particle = self.base.loader.loadModel("models/smiley")
            except Exception:
                particle = None
            
            if particle:
                particle.reparentTo(self.base.render)
                particle.setScale(0.15)
                particle.setPos(self.pos)
                particle.setColor(1.0, 0.9, 0.2, 1)
                particles.append(particle)
        
        # Animación de partículas
        for i, particle in enumerate(particles):
            angle = (i / len(particles)) * 3.14159 * 2
            import math
            dir_x = math.cos(angle) * 2.0
            dir_z = math.sin(angle) * 2.0
            target = particle.getPos() + Point3(dir_x, 1.0, dir_z)
            
            move_seq = Sequence(
                LerpPosInterval(particle, 0.6, target),
                Func(particle.removeNode)
            )
            move_seq.start()
        
        # Ocultar el power-up original
        self.node.hide()
    
    def cleanup(self):
        """Limpiar recursos"""
        if hasattr(self, 'rotation_interval'):
            self.rotation_interval.pause()
        if hasattr(self, 'pulse_seq'):
            self.pulse_seq.pause()
        if hasattr(self, 'node') and self.node:
            self.node.removeNode()
