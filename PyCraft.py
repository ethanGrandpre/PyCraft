from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile, ClockObject

globalClock = ClockObject.getGlobalClock()

loadPrcFile("src/Prefs/config.prc")

worldX = 10
worldY = 20
worldZ = 10
renderDist = 50

class World:
    def __init__(self, base):
        self.base = base
        self.grass = self.base.loader.loadModel("./src/models/grassBlock3.glb")
        self.grass.reparentTo(self.base.render)

    def generateTerrain(self, x, y, z):
        for i in range(x):
            for j in range(y):
                for h in range(z):
                    block = self.grass.copyTo(self.base.render)
                    block.setPos(i*2, h*2, j*2)

class Player:
    def __init__(self, base):
        self.base = base
        self.control()
    
    def control(self):
        self.base.disableMouse()
        self.base.taskMgr.add(self.cameraControls, "cameraPointToMouse")

    def cameraControls(self, task):
        is_down = self.base.mouseWatcherNode.is_button_down
        speed = 5 * globalClock.getDt()

        if is_down("w"):
            self.base.camera.setPos(self.base.camera, 0, speed, 0)
        if is_down("s"):
            self.base.camera.setPos(self.base.camera, 0, -speed, 0)
        if is_down("a"):
            self.base.camera.setPos(self.base.camera, -speed, 0, 0)
        if is_down("d"):
            self.base.camera.setPos(self.base.camera, speed, 0, 0)
        md = self.base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        centerX = self.base.win.getXSize() // 2
        centerY = self.base.win.getYSize() // 2

        if self.base.win.movePointer(0, centerX, centerY):
            deltaX = x - centerX
            deltaY = y - centerY
            self.base.camera.setH(self.base.camera.getH() - deltaX * 0.1)
            self.base.camera.setP(self.base.camera.getP() - deltaY * 0.1)

        return Task.cont

class PyCraft(ShowBase):
    def __init__(self):
        super().__init__()

        self.world = World(self)
        self.player = Player(self)
        self.world.generateTerrain(worldX, worldY, worldZ)
        self.taskMgr.add(self.occulsionCulling, "renderDistanceLoading")
    
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
        if self.mouseWatcherNode.is_button_down("escape"):
            self.userExit()
        return Task.cont

if __name__ == "__main__":
    base = PyCraft()
    base.run()