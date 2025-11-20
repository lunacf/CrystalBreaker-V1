"""
Obstáculos rectangulares rompibles para el juego
"""
from panda3d.core import CardMaker, CollisionNode, CollisionSphere, Point3, Vec3, BitMask32, TransparencyAttrib
from direct.interval.LerpInterval import LerpHprInterval
import random


"""
Esta clase representa un obstáculo rectangular 3D que rota y se rompe en fragmentos al ser impactado.
También maneja la creación de fragmentos visuales al romperse.

"""
class BreakableBarrier:
    """Obstáculo rectangular 3D rotatorio que se rompe al impactar"""

    def __init__(self, base, position, cTrav, handler):
        self.base = base
        self.cTrav = cTrav
        self.handler = handler
        self.pos = Point3(*position)
        self.broken = False

        self.node = base.render.attachNewNode("barrier_container")
        self.node.setPos(self.pos)
        self.create_3d_barrier()
        self.node.setColor(0.0, 0.2, 0.6, 1.0)

        cnode = CollisionNode('barrier')
        cnode.addSolid(CollisionSphere(0, 0, 0, 8.5))
        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(0) | BitMask32.bit(1))
        self.collider = self.node.attachNewNode(cnode)

        self.node.setPythonTag('barrier_ref', self)
        self.collider.setPythonTag('barrier_ref', self)

        self.cTrav.addCollider(self.collider, handler)

        self.rotation_interval = LerpHprInterval(
            self.node,
            duration=4.0,
            hpr=(360, 0, 0),
            startHpr=(0, 0, 0)
        )
        self.rotation_interval.loop()

    def create_3d_barrier(self):
        """Crea barra 3D con 6 caras"""
        cm_front = CardMaker("barrier_front")
        cm_front.setFrame(-8, 8, -1, 1)
        front = self.node.attachNewNode(cm_front.generate())
        front.setPos(0, 0.5, 0)
        
        cm_back = CardMaker("barrier_back")
        cm_back.setFrame(-8, 8, -1, 1)
        back = self.node.attachNewNode(cm_back.generate())
        back.setPos(0, -0.5, 0)
        back.setH(180)
        
        cm_top = CardMaker("barrier_top")
        cm_top.setFrame(-8, 8, -1, 1)
        top = self.node.attachNewNode(cm_top.generate())
        top.setPos(0, 0, 1)
        top.setP(-90)
        
        cm_bottom = CardMaker("barrier_bottom")
        cm_bottom.setFrame(-8, 8, -1, 1)
        bottom = self.node.attachNewNode(cm_bottom.generate())
        bottom.setPos(0, 0, -1)
        bottom.setP(90)
        
        cm_left = CardMaker("barrier_left")
        cm_left.setFrame(-1, 1, -1, 1)
        left = self.node.attachNewNode(cm_left.generate())
        left.setPos(-8, 0, 0)
        left.setH(90)
        
        cm_right = CardMaker("barrier_right")
        cm_right.setFrame(-1, 1, -1, 1)
        right = self.node.attachNewNode(cm_right.generate())
        right.setPos(8, 0, 0)
        right.setH(-90)

    def break_apart(self):
        """Se rompe en fragmentos cuando es golpeado"""
        if self.broken:
            return

        self.broken = True

        # Detiene animación de rotación
        if hasattr(self, 'rotation_interval'):
            self.rotation_interval.pause()

        fragments = []

        positions = [
            (-6, 0, 0),
            (-2, 0, 0),
            (2, 0, 0),
            (6, 0, 0),
        ]

        from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpHprInterval, Parallel, Func

        for i, (dx, dy, dz) in enumerate(positions):
            # Crea fragmentos 3D más pequeños
            cm = CardMaker(f"barrier_shard_{i}")
            cm.setFrame(-1.8, 1.8, -0.8, 0.8)
            frag = self.base.render.attachNewNode(cm.generate())
            frag.setPos(self.pos + Vec3(dx, dy, dz))
            frag.setColor(0.0, 0.3, 0.7, 1.0)  # Azul Boca más claro
            frag.setHpr(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))

            vel = Vec3(dx * 0.5, random.uniform(0, 4), random.uniform(-2, 2))

            # Animación con movimiento y rotación
            move = LerpPosInterval(frag, 0.8, frag.getPos() + vel * 0.5)
            spin = LerpHprInterval(frag, 0.8, (
                frag.getH() + random.uniform(180, 360),
                frag.getP() + random.uniform(180, 360),
                frag.getR() + random.uniform(180, 360)
            ))
            
            seq = Sequence(
                Parallel(move, spin),
                Func(frag.removeNode)
            )
            seq.start()
            fragments.append(frag)

        self.node.hide()
        self.collider.removeNode()

    def cleanup(self):
        """Limpia recursos de la barrera"""
        if hasattr(self, 'rotation_interval'):
            self.rotation_interval.pause()
        if self.node:
            self.node.removeNode()
        if self.collider:
            self.collider.removeNode()
    def is_breakable_barrier(self):
    
        return True