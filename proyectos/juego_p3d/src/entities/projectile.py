from panda3d.core import NodePath, CollisionNode, CollisionSphere, Point3, Vec3
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, Func
import time

"""""
 Esta clase representa a un proyectil disparado por el jugador
 puede moverse, colisionar y desactivarse después de un tiempo
 se usa un pool* de proyectiles para optimizar el rendimiento 
 
 
 *(un pool es una colección de objetos reutilizables para evitar la sobrecarga de crear y destruir objetos frecuentemente)
 
 """
 
class Projectile:
    def __init__(self, base):
        self.base = base
        self.active = False
        self.speed = 80.0
        self.lifetime = 3.0
        self.spawn_time = 0.0

        from panda3d.core import CardMaker, TransparencyAttrib, Texture

        cm = CardMaker("projectile_visual")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        self.node = base.render.attachNewNode(cm.generate())

        try:
            import os
            from panda3d.core import Filename, Texture as PandaTexture

            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(project_dir, "images", "projectile.png")

            if os.path.exists(image_path):
                panda_filename = Filename.fromOsSpecific(image_path)

                try:
                    tex = base.loader.loadTexture(panda_filename)
                except Exception:
                    tex = PandaTexture()
                    if not tex.read(panda_filename):
                        raise Exception("No se pudo cargar textura")

                self.node.setTexture(tex)
                self.node.setTransparency(TransparencyAttrib.MAlpha)
                self.node.setColor(1, 1, 1, 1)
            else:
                self.node.setColor(1.0, 0.4, 0.2, 1.0)
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.node.setColor(1.0, 0.4, 0.2, 1.0)

        self.node.setBillboardPointEye()
        self.node.hide()

        cnode = CollisionNode('projectile')
        cnode.addSolid(CollisionSphere(0, 0, 0, 0.5))
        from panda3d.core import BitMask32
        cnode.setFromCollideMask(BitMask32.bit(0))
        cnode.setIntoCollideMask(BitMask32.allOff())
        self.collider = self.node.attachNewNode(cnode)
        self.node.setPythonTag('projectile_ref', self)

    def launch(self, position: Point3, direction: Vec3):
        self.node.setPos(position)
        self.node.show()
        self.direction = direction.normalized()
        self.spawn_time = time.time()
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        displacement = self.direction * (self.speed * dt)
        self.node.setPos(self.node.getPos() + displacement)
        if (time.time() - self.spawn_time) > self.lifetime:
            self.deactivate()

    def deactivate(self):
        self.active = False
        self.node.hide()

class ProjectilePool:
    def __init__(self, base, cTrav, handler, size=12):
        self.base = base
        self.cTrav = cTrav
        self.handler = handler
        self.pool = [Projectile(base) for _ in range(size)]
        for p in self.pool:
            cnp = p.collider
            self.cTrav.addCollider(cnp, handler)

    def get(self):
        for p in self.pool:
            if not p.active:
                return p
        return None

    def spawn(self, origin, direction):
        p = self.get()
        if p:
            print(f"Lanzando proyectil desde {origin} en dirección {direction}")
            p.launch(origin, direction)
        else:
            print("No hay proyectiles disponibles en el pool")

    def update_all(self, dt):
        for p in self.pool:
            p.update(dt)