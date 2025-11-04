from panda3d.core import CollisionNode, CollisionSphere, BitMask32, Point3
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from panda3d.core import NodePath

class Crystal:
    def __init__(self, base, position_tuple, cTrav, coll_handler):
        self.base = base
        self.pos = Point3(*position_tuple)
        self.broken = False
        self.node = base.loader.loadModel("models/panda")
        self.node.reparentTo(base.render)
        self.node.setScale(0.0035, 0.0035, 0.006)
        self.node.setPos(self.pos)
        cnode = CollisionNode('crystal')
        cnode.addSolid(CollisionSphere(0, 0, 0, 1.0))
        cnode.setIntoCollideMask(BitMask32.bit(1))
        self.collider = self.node.attachNewNode(cnode)

    def break_apart(self):
        if self.broken:
            return
        self.broken = True
        self.node.hide()
        shards = []
        for i in range(6):
            try:
                shard = self.base.loader.loadModel("models/smiley")
            except Exception:
                shard = None
            if shard:
                shard.reparentTo(self.base.render)
                shard.setScale(0.12)
                shard.setPos(self.pos)
                shards.append(shard)

        seq = []
        for i, shard in enumerate(shards):
            angle = (i / len(shards)) * 3.14159 * 2
            dir_vec = (Point3((0.8 * (i%2+1)) * (1 if i%2==0 else -1), 1.0 + 0.4*i, 0.2 + 0.2*i))
            target = shard.getPos() + dir_vec
            move = LerpPosInterval(shard, 0.8, target)
            hide = Func(shard.hide)
            seq.append(Sequence(move, hide))
        for s in seq:
            s.start()