"""
Obstáculos rectangulares rompibles para el juego
"""
from panda3d.core import CardMaker, CollisionNode, CollisionSphere, Point3, Vec3, BitMask32, TransparencyAttrib, GeomNode, GeomVertexData, GeomVertexFormat, Geom, GeomTriangles
import random

class BreakableBarrier:
    """Obstáculo rectangular que se puede romper para avanzar"""

    def __init__(self, base, position, cTrav, handler):
        self.base = base
        self.cTrav = cTrav
        self.handler = handler
        self.pos = Point3(*position)
        self.broken = False

        cm = CardMaker("barrier")
        cm.setFrame(-8, 8, -1, 1)
        self.node = base.render.attachNewNode(cm.generate())
        self.node.setPos(self.pos)
        self.node.setHpr(0, 0, 0)

        self.node.setColor(0.4, 0.4, 0.45, 1.0)

        cnode = CollisionNode('barrier')
        cnode.addSolid(CollisionSphere(0, 0, 0, 8.5))

        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(0) | BitMask32.bit(1))

        self.collider = self.node.attachNewNode(cnode)

        self.node.setPythonTag('barrier_ref', self)
        self.collider.setPythonTag('barrier_ref', self)

        self.cTrav.addCollider(self.collider, handler)

    def break_apart(self):
        """Se rompe en fragmentos cuando es golpeado"""
        if self.broken:
            return

        self.broken = True

        fragments = []

        positions = [
            (-6, 0, 0),
            (-2, 0, 0),
            (2, 0, 0),
            (6, 0, 0),
        ]

        from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, Func

        for i, (dx, dy, dz) in enumerate(positions):
            cm = CardMaker(f"barrier_shard_{i}")
            cm.setFrame(-1.8, 1.8, -0.8, 0.8)
            frag = self.base.render.attachNewNode(cm.generate())
            frag.setPos(self.pos + Vec3(dx, dy, dz))
            frag.setColor(0.5, 0.5, 0.55, 1.0)
            frag.setHpr(0, 0, 0)

            vel = Vec3(dx * 0.5, random.uniform(0, 4), random.uniform(-2, 2))

            seq = Sequence(
                LerpPosInterval(frag, 0.5, frag.getPos() + vel * 0.5),
                Func(frag.removeNode)
            )
            seq.start()
            fragments.append(frag)

        self.node.hide()
        self.collider.removeNode()

    def cleanup(self):
        """Limpiar recursos"""
        if self.node:
            self.node.removeNode()
        if self.collider:
            self.collider.removeNode()
