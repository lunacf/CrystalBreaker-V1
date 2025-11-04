from direct.task import Task
from panda3d.core import Vec3, Point3, AmbientLight, DirectionalLight, CardMaker, CollisionTraverser, CollisionHandlerEvent
from direct.showbase.DirectObject import DirectObject
from entities.player import Player
from entities.projectile import ProjectilePool
from entities.crystal import Crystal
from entities.barrier import BreakableBarrier

class Game:
    def __init__(self, base):
        self.base = base
        self.speed = 10.0
        self.cTrav = CollisionTraverser()

        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('%fn-into-%in')
        self.handler.addInPattern('projectile-into-crystal')
        self.handler.addInPattern('projectile-into-barrier')
        self.handler.addInPattern('player-into-barrier')

        self.setup_scene()
        self.player = Player(self.base, self.cTrav, self.handler)
        self.player.set_on_hit_barrier_callback(self.on_player_hit_barrier)
        self.projectile_pool = ProjectilePool(self.base, self.cTrav, self.handler)
        self.player.set_shoot_callback(self.projectile_pool.spawn)
        self.crystals = []
        self.spawn_demo_crystals()

        self.last_crystal_spawn_time = 0
        self.crystal_spawn_interval = 3.0
        self.crystal_spawn_y_distance = 20

        self.last_obstacle_spawn = 0
        self.obstacle_spawn_distance = 10
        self.obstacles = []

        self.barriers = []
        self.last_barrier_spawn = -10
        self.barrier_spawn_distance = 20

        self.score = 0
        self.game_paused = False
        self.game_over = False

        self.base.accept('projectile-into-crystal', self.on_projectile_hit)

        self.base.accept('projectile-into-barrier', self.on_projectile_hit_barrier)

        self.base.accept('player-into-barrier', self.player.on_hit_barrier)

        self.base.accept('escape', self.toggle_pause)

        self.base.taskMgr.add(self.update, "game-update-task")

    def setup_scene(self):
        from panda3d.core import Vec4
        self.base.setBackgroundColor(Vec4(0.85, 0.88, 0.92, 1))

        from panda3d.core import TransparencyAttrib

        cm = CardMaker('floor')
        cm.setFrame(-50, 50, -50, 50)
        floor = self.base.render.attachNewNode(cm.generate())
        floor.setPos(0, 100, 0)
        floor.setHpr(0, -90, 0)
        floor.setColor(0.65, 0.68, 0.72, 1)

        left_wall = CardMaker('left_wall')
        left_wall.setFrame(0, 500, 0, 10)
        left = self.base.render.attachNewNode(left_wall.generate())
        left.setPos(-8, 0, 0)
        left.setHpr(90, 0, 0)
        left.setColor(0.55, 0.58, 0.62, 1)

        right_wall = CardMaker('right_wall')
        right_wall.setFrame(0, 500, 0, 10)
        right = self.base.render.attachNewNode(right_wall.generate())
        right.setPos(8, 0, 0)
        right.setHpr(-90, 0, 0)
        right.setColor(0.55, 0.58, 0.62, 1)

        ceiling = CardMaker('ceiling')
        ceiling.setFrame(-8, 8, 0, 500)
        ceil = self.base.render.attachNewNode(ceiling.generate())
        ceil.setPos(0, 0, 6)
        ceil.setP(-90)
        ceil.setColor(0.6, 0.63, 0.67, 1)
        ambient = AmbientLight("ambient")
        ambient.setColor((0.75, 0.78, 0.82, 1))
        ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(ambient_np)

        dlight = DirectionalLight("dlight")
        dlight.setColor((0.9, 0.92, 0.95, 1))
        dlnp = self.base.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.base.render.setLight(dlnp)

        dlight2 = DirectionalLight("dlight2")
        dlight2.setColor((0.4, 0.42, 0.45, 1))
        dlnp2 = self.base.render.attachNewNode(dlight2)
        dlnp2.setHpr(180, -30, 0)
        self.base.render.setLight(dlnp2)

        self.base.camera.setPos(0, -5, 2)
        self.base.camera.lookAt(0, 20, 2)

        self.setup_ui()

        print("¡Juego iniciado! Deberías ver la ventana del juego.")

    def setup_ui(self):
        """Configura la interfaz de usuario con instrucciones"""
        from direct.gui.OnscreenText import OnscreenText

        OnscreenText(text="Crystal Breaker Boca Version", pos=(0, 0.9), scale=0.08,
                    fg=(1, 1, 0, 1), align=1, mayChange=False)

        self.crystal_counter = OnscreenText(text="Cristales: 8", pos=(1.2, 0.9), scale=0.06,
                                          fg=(0, 1, 0, 1), align=0, mayChange=True)

        self.score_text = OnscreenText(text="Puntos: 0", pos=(-1.3, 0.8), scale=0.07,
                                      fg=(0, 0.8, 1, 1), align=0, mayChange=True)

    def spawn_demo_crystals(self):
        positions = [
            ( -2, 20, 2 ),
            (  2, 30, 2.5 ),
        ]
        for i, pos in enumerate(positions):
            c = Crystal(self.base, pos, self.cTrav, self.handler)
            c.node.setPythonTag('crystal_ref', c)
            c.collider.setPythonTag('crystal_ref', c)
            self.crystals.append(c)

    def spawn_obstacles(self):
        """Genera obstáculos decorativos (columnas, vigas) para dar contexto"""
        import random
        camera_y = self.base.camera.getY()

        if camera_y > self.last_obstacle_spawn + self.obstacle_spawn_distance:
            self.last_obstacle_spawn = camera_y
            spawn_y = camera_y + 30

            obstacle_type = random.choice(['columns', 'beam', 'arch', 'pillars'])

            if obstacle_type == 'columns':
                self.create_column(-6, spawn_y, random.choice([4, 5, 6]))
                self.create_column(6, spawn_y, random.choice([4, 5, 6]))

            elif obstacle_type == 'beam':
                self.create_beam(spawn_y, 5)

            elif obstacle_type == 'arch':
                self.create_arch(spawn_y)

            elif obstacle_type == 'pillars':
                for _ in range(random.randint(2, 3)):
                    x = random.choice([-7, -6, 6, 7])
                    z = random.uniform(0.5, 2)
                    self.create_pillar(x, spawn_y + random.uniform(0, 5), z)

    def create_column(self, x, y, height):
        """Crear una columna vertical"""
        from panda3d.core import CardMaker

        cm = CardMaker('column')
        cm.setFrame(-0.3, 0.3, 0, height)
        column = self.base.render.attachNewNode(cm.generate())
        column.setPos(x, y, 0)
        column.setColor(0.45, 0.48, 0.52, 1)
        column.setBillboardPointEye()

        self.obstacles.append(column)

    def create_beam(self, y, z):
        """Crear una viga horizontal"""
        from panda3d.core import CardMaker

        cm = CardMaker('beam')
        cm.setFrame(-8, 8, -0.3, 0.3)
        beam = self.base.render.attachNewNode(cm.generate())
        beam.setPos(0, y, z)
        beam.setP(-90)
        beam.setColor(0.4, 0.43, 0.47, 1)

        self.obstacles.append(beam)

    def create_arch(self, y):
        """Crear un arco decorativo"""
        from panda3d.core import CardMaker

        for x in [-5, 5]:
            cm = CardMaker('arch_pillar')
            cm.setFrame(-0.4, 0.4, 0, 4)
            pillar = self.base.render.attachNewNode(cm.generate())
            pillar.setPos(x, y, 0)
            pillar.setColor(0.42, 0.45, 0.5, 1)
            pillar.setBillboardPointEye()
            self.obstacles.append(pillar)

        cm = CardMaker('arch_top')
        cm.setFrame(-5, 5, -0.3, 0.3)
        top = self.base.render.attachNewNode(cm.generate())
        top.setPos(0, y, 4)
        top.setP(-90)
        top.setColor(0.42, 0.45, 0.5, 1)
        self.obstacles.append(top)

    def create_pillar(self, x, y, z):
        """Crear un pilar decorativo pequeño"""
        from panda3d.core import CardMaker

        cm = CardMaker('pillar')
        cm.setFrame(-0.2, 0.2, -0.2, 0.2)
        pillar = self.base.render.attachNewNode(cm.generate())
        pillar.setPos(x, y, z)
        pillar.setColor(0.38, 0.41, 0.46, 1)
        pillar.setBillboardPointEye()

        self.obstacles.append(pillar)

    def cleanup_old_obstacles(self):
        """Eliminar obstáculos que están muy atrás"""
        camera_y = self.base.camera.getY()
        obstacles_to_remove = []

        for obstacle in self.obstacles:
            if obstacle.getY() < camera_y - 50:
                obstacle.removeNode()
                obstacles_to_remove.append(obstacle)

        for obstacle in obstacles_to_remove:
            self.obstacles.remove(obstacle)

    def spawn_barriers(self):
        """Genera barriers (obstáculos rompibles) que deben destruirse para avanzar"""
        import random
        import time

        camera_y = self.base.camera.getY()
        current_time = time.time()

        if current_time >= self.last_barrier_spawn + 8.0:
            self.last_barrier_spawn = current_time

            spawn_y = camera_y + 30
            x = random.choice([-2, 0, 2])
            z = random.uniform(2, 3.5)
            pos = (x, spawn_y, z)

            barrier = BreakableBarrier(self.base, pos, self.cTrav, self.handler)
            barrier.node.setPythonTag('barrier_ref', barrier)
            barrier.collider.setPythonTag('barrier_ref', barrier)
            self.barriers.append(barrier)

    def cleanup_old_barriers(self):
        """Eliminar barriers que pasaron sin romperse (descuenta puntos)"""
        camera_y = self.base.camera.getY()
        barriers_to_remove = []

        for barrier in self.barriers:
            if barrier.pos.getY() < camera_y - 10:
                if not barrier.broken:
                    self.score = max(0, self.score - 10)
                    self.score_text.setText(f"Puntos: {self.score}")
                    print(f"❌ Barrier no roto! Puntos: {self.score}")

                barrier.cleanup()
                barriers_to_remove.append(barrier)

        for barrier in barriers_to_remove:
            self.barriers.remove(barrier)

    def spawn_new_crystals(self):
        """Genera nuevos cristales adelante de la cámara - máximo 2 cada 3 segundos"""
        import random
        import time

        camera_y = self.base.camera.getY()
        current_time = time.time()

        if current_time >= self.last_crystal_spawn_time + self.crystal_spawn_interval:
            self.last_crystal_spawn_time = current_time

            spawn_y = camera_y + self.crystal_spawn_y_distance

            for i in range(2):
                x = random.uniform(-4, 4)
                z = random.uniform(1.5, 3.5)
                pos = (x, spawn_y + random.uniform(0, 5), z)

                c = Crystal(self.base, pos, self.cTrav, self.handler)
                c.node.setPythonTag('crystal_ref', c)
                c.collider.setPythonTag('crystal_ref', c)
                self.crystals.append(c)

    def toggle_pause(self):
        """Alternar pausa del juego"""
        self.game_paused = not self.game_paused

        if self.game_paused:
            from direct.gui.OnscreenText import OnscreenText
            self.pause_text = OnscreenText(
                text="PAUSA\n\nESC = Continuar\nQ = Salir",
                pos=(0, 0), scale=0.12,
                fg=(0, 0.8, 1, 1), align=1,
                mayChange=False
            )
            self.pause_bg = OnscreenText(
                text="", pos=(0, 0), scale=10,
                fg=(0, 0, 0, 0.7), align=1,
                mayChange=False
            )
            self.base.accept('q', self.quit_game)
        else:
            if hasattr(self, 'pause_text'):
                self.pause_text.destroy()
                self.pause_bg.destroy()
            self.base.ignore('q')

    def quit_game(self):
        """Salir del juego"""
        import sys
        sys.exit()

    def cleanup(self):
        """Limpiar recursos del juego"""
        for crystal in self.crystals:
            if hasattr(crystal, 'node') and crystal.node:
                crystal.node.removeNode()
        self.crystals.clear()

        for obstacle in self.obstacles:
            if obstacle:
                obstacle.removeNode()
        self.obstacles.clear()

        if hasattr(self, 'projectile_pool'):
            for proj in self.projectile_pool.pool:
                if hasattr(proj, 'node') and proj.node:
                    proj.node.removeNode()

        if hasattr(self, 'crystal_counter'):
            self.crystal_counter.destroy()
        if hasattr(self, 'score_text'):
            self.score_text.destroy()
        if hasattr(self, 'pause_text'):
            self.pause_text.destroy()
            self.pause_bg.destroy()

    def trigger_game_over(self):
        """Activar game over"""
        self.game_over = True
        self.base.show_game_over(self.score)

    def cleanup_old_crystals(self):
        """Elimina cristales que están muy atrás de la cámara"""
        camera_y = self.base.camera.getY()
        crystals_to_remove = []

        for crystal in self.crystals:
            if crystal.pos.getY() < camera_y - 50:
                crystal.node.removeNode()
                crystals_to_remove.append(crystal)

        for crystal in crystals_to_remove:
            self.crystals.remove(crystal)

    def on_projectile_hit(self, entry):
        print("¡Colisión detectada!")
        try:
            from_np = entry.getFromNodePath().getParent()
            into_np = entry.getIntoNodePath().getParent()
            print(f"From: {from_np}, Into: {into_np}")
        except Exception as e:
            print(f"Error obteniendo nodos: {e}")
            return

        proj = from_np.getPythonTag('projectile_ref')
        crystal = into_np.getPythonTag('crystal_ref')
        print(f"Projectile: {proj}, Crystal: {crystal}")

        if proj:
            print("Desactivando proyectil")
            proj.deactivate()
        if crystal and not crystal.broken:
            print("Rompiendo cristal - ¡+10 puntos!")
            crystal.break_apart()
            self.score += 10
            self.score_text.setText(f"Puntos: {self.score}")

    def on_projectile_hit_barrier(self, entry):
        """Maneja colisión entre proyectil y barrier"""
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
            self.score += 5
            self.score_text.setText(f"Puntos: {self.score}")

    def on_player_hit_barrier(self):
        print("DEBUG: on_player_hit_barrier() called in game.py!")
        self.score = max(0, self.score - 10)
        self.score_text.setText(f"Puntos: {self.score}")
        print(f"¡Chocaste con un barrier! -10 puntos. Puntos actuales: {self.score}")

        if self.score <= 0:
            print("¡Game Over! Te quedaste sin puntos")
            self.trigger_game_over()

    def update(self, task: Task):
        from panda3d.core import ClockObject
        dt = ClockObject.getGlobalClock().getDt()

        if self.game_paused:
            return Task.cont

        if self.game_over:
            return Task.cont

        self.base.camera.setY(self.base.camera, self.speed * dt)

        self.projectile_pool.update_all(dt)

        self.spawn_new_crystals()

        self.spawn_barriers()

        self.spawn_obstacles()

        self.cleanup_old_crystals()

        self.cleanup_old_barriers()

        self.cleanup_old_obstacles()

        active_crystals = sum(1 for c in self.crystals if not c.broken)
        self.crystal_counter.setText(f"Cristales: {active_crystals}")

        self.cTrav.traverse(self.base.render)

        return Task.cont