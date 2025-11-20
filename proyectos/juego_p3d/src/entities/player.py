from panda3d.core import Vec3, Point3, CollisionNode, CollisionSphere, BitMask32
import time


"""
Esta clase maneja el apuntado con el mouse y el sistema de disparo del jugador.
Permite configurar callbacks* para disparar proyectiles y manejar colisiones con barreras.

Los callbacks se pueden establecer mediante los métodos `set_shoot_callback` y `set_barrier_callback`.

*Un callback es una función que se ejecuta en respuesta a un evento específico, como disparar o colisionar con una barrera.

"""
class Player:
    """Maneja apuntado con mouse y sistema de disparo"""
    def __init__(self, base, cTrav, handler):
        self.base = base
        self.cTrav = cTrav
        self.handler = handler
        self.base.accept("mouse1", self.on_shoot)
        self.shoot_callback = None

        cnode = CollisionNode('player')
        cnode.addSolid(CollisionSphere(0, 0, 0, 1.5))
        cnode.setFromCollideMask(BitMask32.bit(1))
        cnode.setIntoCollideMask(BitMask32.allOff())

        self.collider = base.camera.attachNewNode(cnode)
        cTrav.addCollider(self.collider, handler)
        base.accept('player-into-barrier', self.on_hit_barrier)

        self.barrier_callback = None
        self.last_barrier_hit_time = 0
        self.barrier_hit_cooldown = 0.5

    def set_barrier_callback(self, fn):
        self.barrier_callback = fn

    def on_hit_barrier(self, entry):
        try:
            into_np = entry.getIntoNodePath().getParent()
            barrier = into_np.getPythonTag('barrier_ref')
            
            if not barrier or barrier.broken:
                return
                
            current_time = time.time()
            if current_time - self.last_barrier_hit_time < self.barrier_hit_cooldown:
                return

            self.last_barrier_hit_time = current_time
            if self.barrier_callback:
                self.barrier_callback()
        except Exception as e:
            pass

    def set_shoot_callback(self, fn):
        self.shoot_callback = fn

    def get_aim_direction(self):
        """Calcula origen y dirección del disparo desde la cámara"""
        if self.base.mouseWatcherNode.hasMouse():
            mpos = self.base.mouseWatcherNode.getMouse()
            near = Point3()
            far = Point3()
            self.base.camLens.extrude(mpos, near, far)
            near_world = self.base.render.getRelativePoint(self.base.camera, near)
            far_world = self.base.render.getRelativePoint(self.base.camera, far)
            direction = (far_world - near_world)
            direction.normalize()
            origin = near_world
            return origin, direction
        else:
            origin = self.base.camera.getPos(self.base.render)
            forward = self.base.camera.getQuat(self.base.render).getForward()
            return origin, forward

    def on_shoot(self):
        if self.shoot_callback:
            origin, direction = self.get_aim_direction()
            self.shoot_callback(origin, direction)