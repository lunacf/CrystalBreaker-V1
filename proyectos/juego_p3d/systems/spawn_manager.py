"""
SpawnManager - Maneja la generación de objetos en el juego
Responsabilidades:
- Spawn de cristales
- Spawn de barriers (obstáculos rompibles)
- Spawn de obstáculos decorativos (columnas, vigas, arcos)
- Limpieza de objetos fuera de vista
- Patrones de spawn
"""

import random
import time
from panda3d.core import CardMaker
from entities.crystal import Crystal
from entities.barrier import BreakableBarrier


class SpawnManager:
    def __init__(self, base, cTrav, handler):
        self.base = base
        self.cTrav = cTrav
        self.handler = handler
        
        # Listas de objetos activos
        self.crystals = []
        self.barriers = []
        self.obstacles = []
        
        # Configuración de spawn de cristales
        self.last_crystal_spawn_time = 0
        self.crystal_spawn_interval = 3.0
        self.crystal_spawn_y_distance = 20
        
        # Configuración de spawn de barriers
        self.last_barrier_spawn = -10
        self.barrier_spawn_distance = 20
        
        # Configuración de spawn de obstáculos decorativos
        self.last_obstacle_spawn = 0
        self.obstacle_spawn_distance = 10
        
    # ========== CRISTALES ==========
    
    def spawn_demo_crystals(self):
        """Genera cristales de demostración al inicio"""
        positions = [
            (-2, 20, 2),
            (2, 30, 2.5),
        ]
        for pos in positions:
            self._create_crystal(pos)
            
    def spawn_new_crystals(self):
        """Genera nuevos cristales adelante de la cámara - máximo 2 cada 3 segundos"""
        camera_y = self.base.camera.getY()
        current_time = time.time()

        if current_time >= self.last_crystal_spawn_time + self.crystal_spawn_interval:
            self.last_crystal_spawn_time = current_time
            spawn_y = camera_y + self.crystal_spawn_y_distance

            for i in range(2):
                x = random.uniform(-4, 4)
                z = random.uniform(1.5, 3.5)
                pos = (x, spawn_y + random.uniform(0, 5), z)
                self._create_crystal(pos)
                
    def _create_crystal(self, pos):
        """Crea un cristal en la posición indicada"""
        c = Crystal(self.base, pos, self.cTrav, self.handler)
        c.node.setPythonTag('crystal_ref', c)
        c.collider.setPythonTag('crystal_ref', c)
        self.crystals.append(c)
        
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
            
    def get_active_crystal_count(self):
        """Retorna la cantidad de cristales no rotos"""
        return sum(1 for c in self.crystals if not c.broken)
    
    # ========== BARRIERS ==========
    
    def spawn_barriers(self):
        """Genera barriers (obstáculos rompibles) que deben destruirse"""
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
            
    def cleanup_old_barriers(self, on_barrier_missed_callback):
        """Elimina barriers que pasaron sin romperse"""
        camera_y = self.base.camera.getY()
        barriers_to_remove = []

        for barrier in self.barriers:
            if barrier.pos.getY() < camera_y - 10:
                if not barrier.broken:
                    # Llamar callback para penalizar al jugador
                    on_barrier_missed_callback()
                barrier.cleanup()
                barriers_to_remove.append(barrier)

        for barrier in barriers_to_remove:
            self.barriers.remove(barrier)
            
    def spawn_pattern_gauntlet(self, start_y):
        """Patrón de desafío: dos cristales con un barrier en medio"""
        self._create_crystal((-3, start_y, 2))
        self._create_crystal((3, start_y + 5, 2.5))
        
        barrier = BreakableBarrier(self.base, (0, start_y + 2.5, 2.5), self.cTrav, self.handler)
        barrier.node.setPythonTag('barrier_ref', barrier)
        barrier.collider.setPythonTag('barrier_ref', barrier)
        self.barriers.append(barrier)
    
    # ========== OBSTÁCULOS DECORATIVOS ==========
    
    def spawn_obstacles(self):
        """Genera obstáculos decorativos (columnas, vigas) para dar contexto"""
        camera_y = self.base.camera.getY()

        if camera_y > self.last_obstacle_spawn + self.obstacle_spawn_distance:
            self.last_obstacle_spawn = camera_y
            spawn_y = camera_y + 30

            obstacle_type = random.choice(['columns', 'beam', 'arch', 'pillars', 'decorative', ''])

            if obstacle_type == 'columns':
                self._create_column(-6, spawn_y, random.choice([4, 5, 6]))
                self._create_column(6, spawn_y, random.choice([4, 5, 6]))

            elif obstacle_type == 'beam':
                self._create_beam(spawn_y, 5)

            elif obstacle_type == 'arch':
                self._create_arch(spawn_y)

            elif obstacle_type == 'pillars':
                for _ in range(random.randint(2, 3)):
                    x = random.choice([-7, -6, 6, 7])
                    z = random.uniform(0.5, 2)
                    self._create_pillar(x, spawn_y + random.uniform(0, 5), z)
            
            elif obstacle_type == 'decorative':
                for _ in range(random.randint(3, 5)):
                    x = random.uniform(-7, 7)
                    z = random.uniform(0.5, 3)
                    self._create_pillar(x, spawn_y + random.uniform(0, 5), z)
                    
    def _create_column(self, x, y, height):
        """Crear una columna vertical"""
        cm = CardMaker('column')
        cm.setFrame(-0.3, 0.3, 0, height)
        column = self.base.render.attachNewNode(cm.generate())
        column.setPos(x, y, 0)
        column.setColor(0.45, 0.48, 0.52, 1)
        column.setBillboardPointEye()
        self.obstacles.append(column)

    def _create_beam(self, y, z):
        """Crear una viga horizontal"""
        cm = CardMaker('beam')
        cm.setFrame(-8, 8, -0.3, 0.3)
        beam = self.base.render.attachNewNode(cm.generate())
        beam.setPos(0, y, z)
        beam.setP(-90)
        beam.setColor(0.4, 0.43, 0.47, 1)
        self.obstacles.append(beam)

    def _create_arch(self, y):
        """Crear un arco decorativo"""
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

    def _create_pillar(self, x, y, z):
        """Crear un pilar decorativo pequeño"""
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
    
    # ========== LIMPIEZA GENERAL ==========
    
    def cleanup(self):
        """Limpia todos los objetos spawneados"""
        # Limpiar cristales
        for crystal in self.crystals:
            if hasattr(crystal, 'node') and crystal.node:
                crystal.node.removeNode()
        self.crystals.clear()
        
        # Limpiar barriers
        for barrier in self.barriers:
            if hasattr(barrier, 'node') and barrier.node:
                barrier.cleanup()
        self.barriers.clear()

        # Limpiar obstáculos
        for obstacle in self.obstacles:
            if obstacle:
                obstacle.removeNode()
        self.obstacles.clear()
