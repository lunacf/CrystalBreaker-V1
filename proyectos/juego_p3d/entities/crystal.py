from panda3d.core import CollisionNode, CollisionSphere, BitMask32, Point3, CardMaker, TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
import os

class Crystal:
    def __init__(self, base, position_tuple, cTrav=None, coll_handler=None):
        self.base = base
        self.pos = Point3(*position_tuple)
        self.broken = False

        # Crear sprite con imagen de fantasma
        cm = CardMaker('crystal_card')
        cm.setFrame(-0.8, 0.8, -0.8, 0.8)
        
        self.node = base.render.attachNewNode(f"crystal_{id(self)}")
        self.node.setPos(self.pos)
        
        crystal_np = self.node.attachNewNode(cm.generate())
        
        # Carga textura del fantasma
        try:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(project_dir, "fantasma.png")
            
            if os.path.exists(image_path):
                from panda3d.core import Filename
                tex = base.loader.loadTexture(Filename.fromOsSpecific(image_path))
                crystal_np.setTexture(tex)
                crystal_np.setTransparency(TransparencyAttrib.MAlpha)
                print(f"✅ Textura fantasma cargada para cristal")
            else:
                print(f"⚠️ No se encontró fantasma.png en {image_path}")
                crystal_np.setColor(0.3, 0.7, 0.95, 0.75)
        except Exception as e:
            print(f"❌ Error cargando textura fantasma: {e}")
            crystal_np.setColor(0.3, 0.7, 0.95, 0.75)
        
        # Hace que siempre mire a la cámara
        crystal_np.setBillboardPointEye()
        
        cnode = CollisionNode('crystal')
        cnode.addSolid(CollisionSphere(0, 0, 0, 1.0))
        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(0))
        self.collider = self.node.attachNewNode(cnode)
        if cTrav is not None and coll_handler is not None:
            cTrav.addCollider(self.collider, coll_handler)
        
        # Agregar movimiento aleatorio al fantasma
        self.start_movement()

    def start_movement(self):
        """Inicia el movimiento del fantasma"""
        import random
        from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
        from direct.interval.MetaInterval import Sequence, Parallel
        
        # Movimiento lateral (izquierda-derecha)
        current_x = self.pos.getX()
        direction = random.choice([-1, 1])
        distance = random.uniform(1.5, 3.0)
        target_x = current_x + (direction * distance)
        
        # Limitar para que no se salga del área de juego
        target_x = max(-6, min(6, target_x))
        
        # Movimiento vertical (arriba-abajo)
        current_z = self.pos.getZ()
        z_offset = random.uniform(-0.5, 0.5)
        target_z = current_z + z_offset
        target_z = max(1.0, min(5.0, target_z))
        
        # Crear movimiento de ida
        duration = random.uniform(2.0, 3.5)
        move_to = LerpPosInterval(
            self.node,
            duration,
            Point3(target_x, self.pos.getY(), target_z),
            startPos=Point3(current_x, self.pos.getY(), current_z)
        )
        
        # Crear movimiento de vuelta
        move_back = LerpPosInterval(
            self.node,
            duration,
            Point3(current_x, self.pos.getY(), current_z),
            startPos=Point3(target_x, self.pos.getY(), target_z)
        )
        
        # Secuencia que se repite (ida y vuelta)
        self.movement_sequence = Sequence(move_to, move_back)
        self.movement_sequence.loop()
    
    def break_apart(self):
        if self.broken:
            return
        self.broken = True
        
        # Detener movimiento si existe
        if hasattr(self, 'movement_sequence'):
            self.movement_sequence.finish()
        
        self.node.hide()
        from panda3d.core import CardMaker, TransparencyAttrib, Filename
        import random

        shards = []
        for i in range(8):
            cm = CardMaker(f"shard_{i}")
            size = random.uniform(0.15, 0.35)
            cm.setFrame(-size, size, -size, size)
            shard = self.base.render.attachNewNode(cm.generate())

            shard.reparentTo(self.base.render)
            shard.setPos(self.pos)
            
            # Desactivar colisiones en los fragmentos
            shard.setCollideMask(BitMask32.allOff())

            # Intentar cargar textura del fantasma para los fragmentos
            try:
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                image_path = os.path.join(project_dir, "fantasma.png")
                if os.path.exists(image_path):
                    tex = self.base.loader.loadTexture(Filename.fromOsSpecific(image_path))
                    shard.setTexture(tex)
                    shard.setTransparency(TransparencyAttrib.MAlpha)
                    shard.setColor(1, 1, 1, 0.7)  # Semi-transparente
                else:
                    shard.setColor(0.3, 0.7, 0.95, 0.85)
            except:
                shard.setTransparency(TransparencyAttrib.MAlpha)
                shard.setColor(0.3, 0.7, 0.95, 0.85)
            
            shard.setBillboardPointEye()
            shards.append(shard)

        seqs = []
        for i, shard in enumerate(shards):
            x_dir = random.uniform(-2, 2)
            y_dir = random.uniform(0.5, 2)
            z_dir = random.uniform(-1, 2)

            dir_vec = Point3(x_dir, y_dir, z_dir)
            target = shard.getPos() + dir_vec

            move = LerpPosInterval(shard, 1.2, target)
            hide = Func(shard.removeNode)
            seqs.append(Sequence(move, hide))

        for s in seqs:
            s.start()