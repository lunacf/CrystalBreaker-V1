from panda3d.core import CollisionNode, CollisionSphere, BitMask32, Point3
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence

class Crystal:
    def __init__(self, base, position_tuple, cTrav=None, coll_handler=None):
        self.base = base
        self.pos = Point3(*position_tuple)
        self.broken = False
        from panda3d.core import TransparencyAttrib, NodePath
        from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomVertexReader

        self.node = base.render.attachNewNode(f"crystal_{id(self)}")
        self.node.setPos(self.pos)

        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('crystal', vformat, Geom.UHStatic)
        vdata.setNumRows(5)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        vertex.addData3(0, 0.5, -1)
        vertex.addData3(-0.5, -0.5, -1)
        vertex.addData3(0.5, -0.5, -1)
        vertex.addData3(0, 0, 1.5)
        vertex.addData3(0, 0, -1.5)

        for i in range(5):
            normal.addData3(0, 0, 1)
            color.addData4(0.3, 0.7, 0.95, 0.75)

        tris = GeomTriangles(Geom.UHStatic)

        tris.addVertices(3, 0, 1)
        tris.addVertices(3, 1, 2)
        tris.addVertices(3, 2, 0)

        tris.addVertices(4, 1, 0)
        tris.addVertices(4, 2, 1)
        tris.addVertices(4, 0, 2)

        geom = Geom(vdata)
        geom.addPrimitive(tris)

        gnode = GeomNode('crystal_geom')
        gnode.addGeom(geom)

        crystal_np = self.node.attachNewNode(gnode)
        crystal_np.setTransparency(TransparencyAttrib.MAlpha)
        crystal_np.setTwoSided(True)
        cnode = CollisionNode('crystal')
        cnode.addSolid(CollisionSphere(0, 0, 0, 1.0))
        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(0))
        self.collider = self.node.attachNewNode(cnode)
        if cTrav is not None and coll_handler is not None:
            cTrav.addCollider(self.collider, coll_handler)

    def break_apart(self):
        if self.broken:
            return
        self.broken = True
        self.node.hide()
        from panda3d.core import CardMaker, TransparencyAttrib
        import random

        shards = []
        for i in range(8):
            cm = CardMaker(f"shard_{i}")
            size = random.uniform(0.1, 0.3)
            cm.setFrame(-size, size, -size, size)
            shard = self.base.render.attachNewNode(cm.generate())

            shard.reparentTo(self.base.render)
            shard.setPos(self.pos)

            shard.setTransparency(TransparencyAttrib.MAlpha)
            shard.setColor(0.3, 0.7, 0.95, 0.85)

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