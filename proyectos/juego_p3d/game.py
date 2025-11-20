from direct.task import Task
from panda3d.core import Vec3, Point3, AmbientLight, DirectionalLight, CardMaker, CollisionTraverser, CollisionHandlerEvent
from direct.showbase.DirectObject import DirectObject
from entities.player import Player
from entities.projectile import ProjectilePool
from entities.crystal import Crystal
from entities.barrier import BreakableBarrier
from entities.powerup import PowerUpObstacle

class Game:
    def __init__(self, base):
        self.base = base
        self.speed = 10.0
        self.cTrav = CollisionTraverser()

        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('%fn-into-%in')
        self.handler.addInPattern('projectile-into-crystal')
        self.handler.addInPattern('projectile-into-barrier')
        self.handler.addInPattern('projectile-into-powerup')
        self.handler.addInPattern('player-into-barrier')

        self.setup_scene()
        self.player = Player(self.base, self.cTrav, self.handler)
        self.player.set_barrier_callback(self.on_player_hit_barrier)
        self.projectile_pool = ProjectilePool(self.base, self.cTrav, self.handler)
        self.player.set_shoot_callback(self.shoot)
        self.crystals = []
        self.spawn_demo_crystals()

        self.last_crystal_spawn_time = 0
        self.crystal_spawn_interval = 3.0
        self.crystal_spawn_y_distance = 20

        self.powerups = []
        self.last_powerup_spawn = 0
        self.powerup_spawn_distance = 35

        self.barriers = []
        self.last_barrier_spawn = -10
        self.barrier_spawn_distance = 20

        self.score = 0
        self.ammo = 20
        self.game_paused = False
        self.game_over = False

        self.base.accept('projectile-into-crystal', self.on_projectile_hit)

        self.base.accept('projectile-into-barrier', self.on_projectile_hit_barrier)

        self.base.accept('projectile-into-powerup', self.on_projectile_hit_powerup)

        self.base.accept('player-into-barrier', self.player.on_hit_barrier)

        self.base.accept('escape', self.toggle_pause)

        self.load_sounds()

        self.base.taskMgr.add(self.update, "game-update-task")

    def setup_scene(self):
        from panda3d.core import Vec4
        self.create_game_background()

        from panda3d.core import TransparencyAttrib
        
        self.create_sun()
        self.clouds = []
        self.create_clouds()

        cm = CardMaker('floor')
        cm.setFrame(-50, 50, -100, 100) 
        self.floor = self.base.render.attachNewNode(cm.generate())
        self.floor.setPos(0, 0, 0)
        self.floor.setHpr(0, -90, 0)
        self.floor.setColor(0.3, 0.3, 0.50, 1)
        
        self.road_lines = []
        for i in range(-10, 120, 8):
            line = CardMaker(f'road_line_{i}')
            line.setFrame(-0.15, 0.15, -2, 2)
            line_node = self.base.render.attachNewNode(line.generate())
            line_node.setPos(0, i, 0.02)
            line_node.setHpr(0, -90, 0)
            line_node.setColor(1, 0.9, 0.2, 1)
            self.road_lines.append(line_node)
        
        left_edge = CardMaker('left_edge')
        left_edge.setFrame(-0.2, 0.2, -100, 100)
        self.left_edge = self.base.render.attachNewNode(left_edge.generate())
        self.left_edge.setPos(-6, 0, 0.02)
        self.left_edge.setHpr(0, -90, 0)
        self.left_edge.setColor(0.9, 0.9, 0.9, 1)
        
        right_edge = CardMaker('right_edge')
        right_edge.setFrame(-0.2, 0.2, -100, 100)
        self.right_edge = self.base.render.attachNewNode(right_edge.generate())
        self.right_edge.setPos(6, 0, 0.02)
        self.right_edge.setHpr(0, -90, 0)
        self.right_edge.setColor(0.9, 0.9, 0.9, 1)

        self.create_brick_wall('left')
        self.create_brick_wall('right')
        self.ceiling = None
        
        ambient = AmbientLight("ambient")
        ambient.setColor((0.75, 0.78, 0.82, 1))
        self.ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(self.ambient_np)

        dlight = DirectionalLight("dlight")
        dlight.setColor((0.9, 0.92, 0.95, 1))
        self.dlnp = self.base.render.attachNewNode(dlight)
        self.dlnp.setHpr(0, -60, 0)
        self.base.render.setLight(self.dlnp)

        dlight2 = DirectionalLight("dlight2")
        dlight2.setColor((0.4, 0.42, 0.45, 1))
        self.dlnp2 = self.base.render.attachNewNode(dlight2)
        self.dlnp2.setHpr(180, -30, 0)
        self.base.render.setLight(self.dlnp2)

        self.base.camera.setPos(0, -5, 2)
        self.base.camera.lookAt(0, 20, 2)

        self.setup_ui()

    def load_sounds(self):
        """Carga efectos de sonido"""
        import os
        if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
            shoot_sound = os.path.join("sounds", "disparo.wav")
            if not os.path.exists(shoot_sound):
                shoot_sound = os.path.join("sounds", "disparo.mp3")
            
            if os.path.exists(shoot_sound):
                self.base.sound_manager.preload_sound('shoot', shoot_sound)
            else:
                print("Sonido de disparo no encontrado")
            
            break_sound = os.path.join("sounds", "fantasma_romper.wav")
            if not os.path.exists(break_sound):
                break_sound = os.path.join("sounds", "fantasma_romper.mp3")
            
            if os.path.exists(break_sound):
                self.base.sound_manager.preload_sound('crystal_break', break_sound)
            else:
                print("Sonido de romper fantasma no encontrado")
            
            powerup_sound = os.path.join("sounds", "powerup.wav")
            if not os.path.exists(powerup_sound):
                powerup_sound = os.path.join("sounds", "powerup.mp3")
            
            if os.path.exists(powerup_sound):
                self.base.sound_manager.preload_sound('powerup', powerup_sound)

    def create_brick_wall(self, side):
        """Crea pared con textura de ladrillo simplificada"""
        x_pos = -8 if side == 'left' else 8
        hpr = 90 if side == 'left' else -90
        
        wall = CardMaker(f'{side}_wall')
        wall.setFrame(-100, 100, 0, 10)
        wall_node = self.base.render.attachNewNode(wall.generate())
        wall_node.setPos(x_pos, 0, 0)
        wall_node.setHpr(hpr, 0, 0)
        wall_node.setColor(0.65, 0.35, 0.25, 1)
        
        if side == 'left':
            self.left_wall = wall_node
            self.left_wall_bricks = []
        else:
            self.right_wall = wall_node
            self.right_wall_bricks = []
        
        brick_list = self.left_wall_bricks if side == 'left' else self.right_wall_bricks
        
        for z in range(0, 17):
            line = CardMaker(f'{side}_joint_{z}')
            line.setFrame(-100, 100, -0.04, 0.04)
            line_node = self.base.render.attachNewNode(line.generate())
            line_node.setPos(x_pos, 0, z * 0.6)
            line_node.setHpr(hpr, 0, 0)
            line_node.setColor(0.4, 0.3, 0.25, 1)
            brick_list.append(line_node)
    
    def create_sun(self):
        """Crea sol brillante en el cielo"""
        from panda3d.core import TransparencyAttrib
        sun_cm = CardMaker('sun')
        sun_cm.setFrame(-3, 3, -3, 3)
        self.sun = self.base.render.attachNewNode(sun_cm.generate())
        self.sun.setPos(15, 50, 25)
        self.sun.setColor(1, 0.95, 0.3, 1)
        self.sun.setBillboardPointEye()
        self.sun.setTransparency(TransparencyAttrib.MAlpha)
    
    def create_clouds(self):
        """Crea nubes animadas en el cielo"""
        import random
        from panda3d.core import TransparencyAttrib
        
        for i in range(8):
            cloud = CardMaker(f'cloud_{i}')
            width = random.uniform(4, 7)
            height = random.uniform(1.5, 2.5)
            cloud.setFrame(-width/2, width/2, -height/2, height/2)
            
            cloud_node = self.base.render.attachNewNode(cloud.generate())
            x_pos = random.uniform(-20, 20)
            y_pos = random.uniform(-50, 150)
            z_pos = random.uniform(15, 30)
            cloud_node.setPos(x_pos, y_pos, z_pos)
            cloud_node.setColor(1, 1, 1, 0.8)
            cloud_node.setBillboardPointEye()
            cloud_node.setTransparency(TransparencyAttrib.MAlpha)
            
            cloud_speed = random.uniform(2, 5)
            self.clouds.append({'node': cloud_node, 'speed': cloud_speed, 'start_y': y_pos})
    
    def create_game_background(self):
        """Crea fondo del juego"""
        from panda3d.core import Vec4
        self.base.setBackgroundColor(Vec4(0.53, 0.81, 0.98, 1))
    
    def setup_ui(self):
        """Configura interfaz de usuario"""
        from direct.gui.OnscreenText import OnscreenText

        OnscreenText(text="Crystal Breaker Boca Version", pos=(0, 0.9), scale=0.08,
                    fg=(1, 1, 0, 1), align=1, mayChange=False)

        self.crystal_counter = OnscreenText(text="Cristales: 8", pos=(1.2, 0.9), scale=0.06,
                                          fg=(0, 1, 0, 1), align=0, mayChange=True)

        self.score_text = OnscreenText(text="Puntuación: 0", pos=(-1.3, 0.8), scale=0.07,
                                      fg=(0, 0.8, 1, 1), align=0, mayChange=True)
        
        self.ammo_text = OnscreenText(text="Disparos: 20", pos=(-1.3, 0.65), scale=0.07,
                                     fg=(1, 0.5, 0, 1), align=0, mayChange=True)
        
        self.powerup_message = None
        self.powerup_message_task = None

    def shoot(self, origin, direction):
        """Dispara si hay munición"""
        if self.game_paused or self.game_over:
            return
        
        if self.ammo > 0:
            self.ammo -= 1
            self.ammo_text.setText(f"Disparos: {self.ammo}")
            
            if self.ammo == 0:
                self.trigger_game_over()
            else:
                self.projectile_pool.spawn(origin, direction)
                if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
                    self.base.sound_manager.play_sound('shoot', volume=0.3)

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

    def spawn_powerups(self):
        """Genera power-ups que otorgan munición extra"""
        import random
        camera_y = self.base.camera.getY()

        if camera_y > self.last_powerup_spawn + self.powerup_spawn_distance:
            self.last_powerup_spawn = camera_y
            spawn_y = camera_y + 40
            
            x_pos = random.uniform(-6, 6)
            z_pos = random.uniform(1, 4)
            ammo_bonus = random.choice([3, 5, 7])
            powerup = PowerUpObstacle(
                self.base,
                (x_pos, spawn_y, z_pos),
                self.cTrav,
                self.handler,
                ammo_bonus=ammo_bonus
            )
            
            self.cTrav.addCollider(powerup.collider, self.handler)
            
            self.powerups.append(powerup)

    def create_column(self, x, y, height):
        """Elimina power-ups que están muy atrás"""
        camera_y = self.base.camera.getY()
        powerups_to_remove = []

        for powerup in self.powerups:
            if powerup.pos.y < camera_y - 50:
                powerup.cleanup()
                powerups_to_remove.append(powerup)

        for powerup in powerups_to_remove:
            self.powerups.remove(powerup)

    def spawn_pattern_gauntlet(self, start_y):
        """Patrón desafío: múltiples barreras seguidas con cristales"""
        from entities.barrier import BreakableBarrier
    
        for i in range(3):
            barrier = BreakableBarrier(
                self.base,
                (0, start_y + i * 10, 2),
                self.cTrav,
                self.handler
            )
            self.barriers.append(barrier)

        for x in [-3, 3]:
            c = Crystal(self.base, (x, start_y + i * 10 - 3, 2), self.cTrav, self.handler)
            c.node.setPythonTag('crystal_ref', c)
            c.collider.setPythonTag('crystal_ref', c)
            self.crystals.append(c)
            
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
                    print(f"❌ Colisión detectada. Puntos: {self.score}")

                barrier.cleanup()
                barriers_to_remove.append(barrier)

        for barrier in barriers_to_remove:
            self.barriers.remove(barrier)

    def cleanup_old_powerups(self):
        """Eliminar power-ups que están muy atrás"""
        camera_y = self.base.camera.getY()
        powerups_to_remove = []

        for powerup in self.powerups:
            if powerup.pos.y < camera_y - 50:
                powerup.cleanup()
                powerups_to_remove.append(powerup)

        for powerup in powerups_to_remove:
            self.powerups.remove(powerup)

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
        """Alterna pausa del juego"""
        self.game_paused = not self.game_paused

        if self.game_paused:
            if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
                if hasattr(self.base.sound_manager, 'music') and self.base.sound_manager.music:
                    self.base.sound_manager.music.stop()
            
            from direct.gui.OnscreenText import OnscreenText
            from direct.gui.DirectGui import DirectFrame
            
            self.pause_overlay = OnscreenText(
                text="", pos=(0, 0), scale=10,
                fg=(0, 0, 0, 0.6), align=1,
                mayChange=False
            )
            
            self.pause_panel = DirectFrame(
                frameColor=(0.1, 0.15, 0.2, 0.95),
                frameSize=(-1.2, 1.2, -0.6, 0.6),
                pos=(0, 0, 0)
            )
            
            self.pause_border = DirectFrame(
                frameColor=(0, 0.8, 1, 1),
                frameSize=(-1.25, 1.25, -0.65, 0.65),
                pos=(0, 0, 0)
            )
            self.pause_border.reparentTo(self.pause_panel)
            self.pause_border.setBin('fixed', 0)
            self.pause_panel.setBin('fixed', 1)
            
            self.pause_title = OnscreenText(
                text="JUEGO PAUSADO",
                pos=(0, 0.35), scale=0.15,
                fg=(1, 1, 0, 1), align=2,
                mayChange=False,
                parent=self.pause_panel
            )
            
            self.pause_text = OnscreenText(
                text="ESC = Continuar\nQ = Salir al Menú",
                pos=(0, -0.15), scale=0.09,
                fg=(0.9, 0.9, 0.9, 1), align=2,
                mayChange=False,
                parent=self.pause_panel
            )
            
            self.base.accept('q', self.quit_game)
        else:
            if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
                if hasattr(self.base.sound_manager, 'music') and self.base.sound_manager.music:
                    self.base.sound_manager.music.play()
            
            if hasattr(self, 'pause_overlay'):
                self.pause_overlay.destroy()
            if hasattr(self, 'pause_panel'):
                self.pause_panel.destroy()
            if hasattr(self, 'pause_border'):
                self.pause_border.destroy()
            if hasattr(self, 'pause_title'):
                self.pause_title.destroy()
            if hasattr(self, 'pause_text'):
                self.pause_text.destroy()
            self.base.ignore('q')

    def quit_game(self):
        """Vuelve al menú principal"""
        self.cleanup()
        self.base.return_to_menu()

    def cleanup(self):
        """Limpia recursos del juego"""
        for crystal in self.crystals:
            if hasattr(crystal, 'node') and crystal.node:
                crystal.node.removeNode()
        self.crystals.clear()

        for powerup in self.powerups:
            if powerup:
                powerup.cleanup()
        self.powerups.clear()

        if hasattr(self, 'projectile_pool'):
            for proj in self.projectile_pool.pool:
                if hasattr(proj, 'node') and proj.node:
                    proj.node.removeNode()

        # Limpiar luces - IMPORTANTE: clearLight antes de removeNode
        if hasattr(self, 'ambient_np') and self.ambient_np:
            self.base.render.clearLight(self.ambient_np)
            self.ambient_np.removeNode()
            self.ambient_np = None
        if hasattr(self, 'dlnp') and self.dlnp:
            self.base.render.clearLight(self.dlnp)
            self.dlnp.removeNode()
            self.dlnp = None
        if hasattr(self, 'dlnp2') and self.dlnp2:
            self.base.render.clearLight(self.dlnp2)
            self.dlnp2.removeNode()
            self.dlnp2 = None

        # Limpiar geometría de la escena
        if hasattr(self, 'floor') and self.floor:
            self.floor.removeNode()
            self.floor = None
        if hasattr(self, 'road_lines'):
            for line in self.road_lines:
                if line:
                    line.removeNode()
            self.road_lines.clear()
        if hasattr(self, 'left_edge') and self.left_edge:
            self.left_edge.removeNode()
            self.left_edge = None
        if hasattr(self, 'right_edge') and self.right_edge:
            self.right_edge.removeNode()
            self.right_edge = None
        if hasattr(self, 'left_wall') and self.left_wall:
            self.left_wall.removeNode()
            self.left_wall = None
        if hasattr(self, 'left_wall_bricks'):
            for brick in self.left_wall_bricks:
                if brick:
                    brick.removeNode()
            self.left_wall_bricks.clear()
        if hasattr(self, 'right_wall') and self.right_wall:
            self.right_wall.removeNode()
            self.right_wall = None
        if hasattr(self, 'right_wall_bricks'):
            for brick in self.right_wall_bricks:
                if brick:
                    brick.removeNode()
            self.right_wall_bricks.clear()
        if hasattr(self, 'ceiling') and self.ceiling:
            self.ceiling.removeNode()
            self.ceiling = None
        
        # Limpiar sol y nubes
        if hasattr(self, 'sun') and self.sun:
            self.sun.removeNode()
            self.sun = None
        if hasattr(self, 'clouds'):
            for cloud_data in self.clouds:
                if cloud_data['node']:
                    cloud_data['node'].removeNode()
            self.clouds.clear()

        if hasattr(self, 'crystal_counter'):
            self.crystal_counter.destroy()
        if hasattr(self, 'score_text'):
            self.score_text.destroy()
        if hasattr(self, 'ammo_text'):
            self.ammo_text.destroy()
        if hasattr(self, 'powerup_message') and self.powerup_message:
            self.powerup_message.destroy()
        if hasattr(self, 'powerup_message_task') and self.powerup_message_task:
            self.base.taskMgr.remove(self.powerup_message_task)
        
        # Limpiar elementos de pausa
        if hasattr(self, 'pause_overlay'):
            self.pause_overlay.destroy()
        if hasattr(self, 'pause_panel'):
            self.pause_panel.destroy()
        if hasattr(self, 'pause_border'):
            self.pause_border.destroy()
        if hasattr(self, 'pause_title'):
            self.pause_title.destroy()
        if hasattr(self, 'pause_text'):
            self.pause_text.destroy()

    def trigger_game_over(self):
        """Activa game over"""
        self.game_over = True
        
        # Pausar música
        if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
            if hasattr(self.base.sound_manager, 'music') and self.base.sound_manager.music:
                self.base.sound_manager.music.stop()
        
        self.base.show_game_over(self.score)

    def cleanup_old_crystals(self):
        """Elimina cristales que están muy atrás de la cámara"""
        camera_y = self.base.camera.getY()
        crystals_to_remove = []

        for crystal in self.crystals:
            if crystal.pos.getY() < camera_y - 50:
                if not crystal.broken:
                    self.ammo = max(0, self.ammo - 5)
                    self.ammo_text.setText(f"Disparos: {self.ammo}")
                    #print(f"Fantasma escapó: -5 disparos. Disparos: {self.ammo}")
                    if self.ammo <= 0:
                        self.trigger_game_over()
                
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
            print(f"Rompiendo cristal - Disparos antes: {self.ammo}")
            crystal.break_apart()
            # Reproducir sonido de romper fantasma
            if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
                self.base.sound_manager.play_sound('crystal_break', volume=0.4)
            self.score += 10
            self.ammo += 1
            print(f"Rompiendo cristal - Disparos después: {self.ammo}")
            self.score_text.setText(f"Puntos: {self.score}")
            self.ammo_text.setText(f"Disparos: {self.ammo}")
        elif crystal and crystal.broken:
            print("Cristal ya estaba roto, no suma disparos")

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
            print("¡Objetivo roto! +3 disparos")
            barrier.break_apart()
            self.ammo += 3
            self.ammo_text.setText(f"Disparos: {self.ammo}")

    def on_projectile_hit_powerup(self, entry):
        """Maneja colisión entre proyectil y power-up"""
        print("🎯 COLISIÓN DETECTADA CON POWER-UP!")
        try:
            from_np = entry.getFromNodePath().getParent()
            into_np = entry.getIntoNodePath().getParent()
            print(f"   From: {from_np}, Into: {into_np}")
        except Exception as e:
            print(f"❌ Error obteniendo nodos: {e}")
            return

        proj = from_np.getPythonTag('projectile_ref')
        powerup = into_np.getPythonTag('powerup_ref')
        
        print(f"   Projectile ref: {proj}")
        print(f"   PowerUp ref: {powerup}")

        if proj:
            print("   ✅ Desactivando proyectil")
            proj.deactivate()

        if powerup and not powerup.destroyed:
            print(f"   💥 ¡Power-Up destruido! +{powerup.ammo_bonus} munición")
            powerup.destroy()
            # Reproducir sonido de power-up
            if hasattr(self.base, 'sound_manager') and self.base.sound_manager:
                self.base.sound_manager.play_sound('powerup', volume=0.5)
            self.ammo += powerup.ammo_bonus
            self.score += 15
            self.score_text.setText(f"Puntos: {self.score}")
            self.ammo_text.setText(f"Disparos: {self.ammo}")
            
            # Mostrar mensaje temporal
            self.show_powerup_message(f"+{powerup.ammo_bonus} DISPAROS!")

    def show_powerup_message(self, message):
        """Muestra un mensaje temporal en pantalla cuando se recoge un power-up"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Limpiar mensaje anterior si existe
        if self.powerup_message:
            self.powerup_message.destroy()
        if self.powerup_message_task:
            self.base.taskMgr.remove(self.powerup_message_task)
        
        # Crear nuevo mensaje
        self.powerup_message = OnscreenText(
            text=message,
            pos=(0, 0.3),
            scale=0.15,
            fg=(1, 0.9, 0.2, 1),
            shadow=(0, 0, 0, 1),
            align=2
        )
        
        def hide_message(task):
            if self.powerup_message:
                self.powerup_message.destroy()
                self.powerup_message = None
            return Task.done
        
        self.powerup_message_task = self.base.taskMgr.doMethodLater(
            2.0, hide_message, 'hide-powerup-message'
        )

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

        # Mantiene paredes laterales alineadas con la cámara
        camera_y = self.base.camera.getY()
        self.left_wall.setY(camera_y)
        self.right_wall.setY(camera_y)
        
        # Mantiene ladrillos alineados con las paredes
        for brick in self.left_wall_bricks:
            brick.setY(camera_y)
        for brick in self.right_wall_bricks:
            brick.setY(camera_y)
        
        # Mantiene el piso/camino alineado con la cámara
        self.floor.setY(camera_y)
        self.left_edge.setY(camera_y)
        self.right_edge.setY(camera_y)
        
        # Anima las líneas del camino para efecto de movimiento
        for line in self.road_lines:
            line.setY(camera_y + (line.getY() - camera_y) % 16 - 8)
        
        # Anima nubes
        for cloud_data in self.clouds:
            cloud = cloud_data['node']
            speed = cloud_data['speed']
            # Mover nube hacia adelante
            cloud.setY(cloud.getY() + speed * dt)
            # Si la nube se aleja mucho, reposicionarla atrás
            if cloud.getY() > camera_y + 100:
                cloud.setY(camera_y - 50)

        self.projectile_pool.update_all(dt)

        self.spawn_new_crystals()

        self.spawn_barriers()

        self.spawn_powerups()

        self.cleanup_old_crystals()

        self.cleanup_old_barriers()

        self.cleanup_old_powerups()

        active_crystals = sum(1 for c in self.crystals if not c.broken)
        self.crystal_counter.setText(f"Cristales: {active_crystals}")

        self.cTrav.traverse(self.base.render)

        return Task.cont