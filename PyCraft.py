from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    loadPrcFile,
)
loadPrcFile("src/Prefs/config.prc")
worldX = 10
worldY = 10
worldZ = 20
renderDist = 50

class PyCraft(ShowBase):
    def __init__(self):
        super().__init__()
        self.grass = self.loader.loadModel("./src/models/grassBlock.glb")
        self.grass.reparentTo(self.render)
        self.generateTerrain(worldX, worldY, worldZ)
        self.taskMgr.add(self.occulsionCulling, "renderDistanceLoading")
    
    def generateTerrain(self, x, y, z):
        for i in range(x):
            for j in range(y):
                for h in range(z):
                    block = self.grass.copyTo(self.render)
                    block.setPos(i*2, h*2, j*2)
    
    def occulsionCulling(self, task):
        camera_pos = self.camera.getPos()
        for node in self.render.getChildren():
            if node != self.camera:
                node_pos = node.getPos()
                distance = (node_pos - camera_pos).length()
                if distance > renderDist:
                    node.hide()
                else:
                    node.show()
        return Task.cont

if __name__ == "__main__":
    base = PyCraft()
    base.run()