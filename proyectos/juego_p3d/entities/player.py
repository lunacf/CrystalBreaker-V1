from panda3d.core import Vec3, Point3, CollisionNode, CollisionSphere, BitMask32
import time

class Player:
    """
    Clase encargada del apuntado por cursor y el disparo.
    - Usa el mouse para apuntar: se extruye un rayo desde la cámara hacia el mundo.
    - Disparo: solicita un proyectil al pool (gestionado desde Game).
    """
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

        self.on_hit_barrier_callback = None
        self.last_barrier_hit_time = 0
        self.barrier_hit_cooldown = 0.5

    def set_on_hit_barrier_callback(self, fn):
        self.on_hit_barrier_callback = fn

    def on_hit_barrier(self, entry):
        try:
            into_np = entry.getIntoNodePath().getParent()
            barrier = into_np.getPythonTag('barrier_ref')
            
            if not barrier or barrier.broken:
                print("DEBUG: No es un barrier válido o ya está roto")
                return
                
            current_time = time.time()
            if current_time - self.last_barrier_hit_time < self.barrier_hit_cooldown:
                print(f"DEBUG: Colisión ignorada (cooldown activo)")
                return

            self.last_barrier_hit_time = current_time
            print("DEBUG: on_hit_barrier() called con barrier válido!")
            if self.on_hit_barrier_callback:
                print("DEBUG: Calling callback")
                self.on_hit_barrier_callback()
            else:
                print("DEBUG: No callback set")
        except Exception as e:
            print(f"DEBUG: Error en on_hit_barrier: {e}")

    def set_shoot_callback(self, fn):
        self.shoot_callback = fn

    def get_aim_direction(self):
        """
        Devuelve (origin_point, direction_vec) en coordenadas del world.
        Si no hay ratón activo, devuelve la dirección frontal de la cámara.
        """
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
        print("¡Disparo!")
        if self.shoot_callback:
            origin, direction = self.get_aim_direction()
            print(f"Origen: {origin}, Dirección: {direction}")
            self.shoot_callback(origin, direction)
        else:
            print("No hay callback configurado")