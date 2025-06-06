from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile, ClockObject, NodePath, WindowProperties, TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
import json
import os

globalClock = ClockObject.getGlobalClock()
loadPrcFile("src/Prefs/config.prc")

worldX = 10
worldY = 20
worldZ = 10
playerSpeed = 20
renderDist = 45
camSensativity = 0.2


class GUI:
    def __init__(self):
        self.node = NodePath("guiRoot")
        self.node.reparentTo(aspect2d) #type: ignore

        self.hotbar = OnscreenImage(image="./src/img/minecraftHotbar.png", pos=(0, 0, -0.85), scale=(0.8, 1, 0.09))
        self.hotbar.reparentTo(self.node)

        self.crosshair = OnscreenImage(image="./src/img/crosshair.png", pos=(0, 0, 0), scale=0.06)
        self.crosshair.reparentTo(self.node)
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

        self.clickSound = loader.loadSfx("src/audio/Click.mp3") #type: ignore
        self.homeScreen()
        self.pauseFrame = None
        self.pauseOpen = False
        self.lastEscape = False
        self.homescreen = True

        base.taskMgr.add(self.pauseTask, "pauseTask")
        self.handleEscapeKey()
    
    def homeScreen(self):
        props = WindowProperties()
        base.player.enabled = False
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)

        self.homeFrame = DirectFrame(
            parent=self.node,
            frameColor=(1, 1, 1, 1),
            frameSize=(1.35, -1.35, 1.35, -1.35),
            pos=(0, 0, 0),
        )
        self.singlePlayerButton = DirectButton(
            parent=self.homeFrame,
            frameSize=(-5, 5, -1, 1),
            scale=0.1,
            pos=(0, 1, 0.3),
            text="Singleplayer",
            text_shadow=(0, 0, 0, 1),
            command=self.handleSingleplayerClick,
        )
    
    def singlePlayer(self):
        self.sPlayer = True
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        self.homeFrame.hide()

        self.singlePlayerScreen = DirectFrame(
            parent=self.node,
            frameColor=(0.5, 0.3, 0.2, 1),
            frameSize=(1.35, -1.35, 1.35, -1.35),
            pos=(0, 0, 0),
        )

        has_saves = os.path.exists("saves") and os.listdir("saves")
        if has_saves:
            y_offset = 0.4
            for idx, filename in enumerate(os.listdir("saves")):
                if filename.endswith(".json"):
                    world_name = filename[:-5]
                    DirectButton(
                        parent=self.singlePlayerScreen,
                        text=world_name,
                        scale=0.08,
                        frameSize=(-5, 5, -0.8, 0.8),
                        frameColor=(1, 1, 1, 1),
                        text_fg=(0, 0, 0, 1),
                        pos=(0, 0, y_offset),
                        command=self.loadWorld,
                        extraArgs=[filename]
                    )
                    y_offset -= 0.2

        DirectButton(
            parent=self.singlePlayerScreen,
            text="Create New World",
            scale=0.1,
            frameSize=(-5, 5, -0.8, 0.8),
            frameColor=(1, 1, 1, 1),
            text_fg=(0, 0, 0, 1),
            pos=(0, 0, -0.6),
            command=self.createNewWorld
        )


    def blank(self):
        self.pauseOpen = False
        base.player.enabled = True
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)
        self.homeFrame.destroy()
        self.blankFrame = DirectFrame(
            parent=self.node,
            frameColor=(0, 0, 0, 0),
            frameSize=(1.35, -1.35, 1.35, -1.35),
            pos=(0, 0, 0),
        )

    def pauseScreen(self):
        self.pauseOpen = True
        base.player.enabled = False
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)

        self.pauseFrame = DirectFrame(
            parent=self.node,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(1.35, -1.35, 1.35, -1.35),
            pos=(0, 0, 0),
        )
        self.text = OnscreenText(
            parent=self.pauseFrame,
            text="Change Sensativity",
            pos=(-0.6, 0.6, 1),
            fg=(1,1,1,1),
        )
        self.slider = DirectSlider(
            parent=self.pauseFrame,
            range=(0.1, 0.4),
            value=camSensativity,
            pageSize=0.1,
            pos=(-0.5, 0, 0.5),
            scale=0.5,
            thumb_relief="ridge",
            command=self.updateSensitivity
        )
        self.quitButton = DirectButton(
            parent=self.pauseFrame,
            text="Quit",
            frameSize=(-5,5,-0.8,0.8),
            scale=0.1,
            pos=(0, 0, -0.7),
            command=self.quitGame
        )

    def quitGame(self):
        self.clickSound.play()
        base.userExit()

    def resumeGame(self):
        self.pauseOpen = False
        base.player.enabled = True

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.MConfined)
        base.win.requestProperties(props)

        if self.pauseFrame:
            self.pauseFrame.destroy()
            self.pauseFrame = None

    def pauseTask(self, task):
        is_down = base.mouseWatcherNode.is_button_down("escape")
        if not self.homescreen:
            if is_down and not self.lastEscape:
                if self.pauseOpen:
                    self.resumeGame()
                else:
                    self.pauseScreen()
            self.lastEscape = is_down
        return Task.cont

    def handleEscapeKey(self):
        base.accept("escape", self.togglePause)

    def togglePause(self):
        if self.pauseOpen:
            self.resumeGame()
        else:
            self.pauseScreen()

    def updateSensitivity(self):
        global camSensativity
        camSensativity = self.slider['value']
        if not base.mouseWatcherNode.is_button_down("mouse1"):
            self.clickSound.play()
        self.clickSound.play()
    
    def handleSingleplayerClick(self):
        self.clickSound.play()
        self.singlePlayer()
    
    def createNewWorld(self):
        self.frame = DirectFrame(
            parent=self.node,
            frameSize=(1.35, -1.35, 1.35, -1.35),
            frameColor=(0.5, 0.3, 0.1, 1),
        )
        self.worldName = DirectEntry(
            parent=self.frame,
            width=10,
            scale=0.1,
            pos=(-0.5, 0, 0.7),
        )
        self.backButton = DirectButton(
            parent=self.frame,
            text="Back",
            scale=0.1,
            pos=(-0.3, 0, -0.5),
            command=self.singlePlayer,
        )
        self.createButton = DirectButton(
            parent=self.frame,
            text="Create",
            scale=0.1,
            pos=(0.3, 0, -0.5),
            command=self.createWorld
        )

    def createWorld(self):
        name = self.worldName.get()
        if not os.path.exists("saves"):
            os.makedirs("saves")
        data = {
            "world_name": name,
            "seed": None,
            "created": True
        }
        with open(f"saves/{name}.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"World '{name}' saved.")

    def loadWorld(self, filename):
        with open(f"saves/{filename}", "r") as f:
            data = json.load(f)
        print(f"Loaded world: {data['world_name']}")
        self.singlePlayerScreen.hide()
        self.blank()


class World:
    def __init__(self, base):
        self.base = base
        self.grass = self.base.loader.loadModel("./src/models/grassBlock3.glb")
        self.dirt = self.base.loader.loadModel("./src/models/dirtBlock.glb")
        self.stone = self.base.loader.loadModel("./src/models/stoneBlock.glb")

    def generateTerrain(self, x, y, z):
        for i in range(x):
            for k in range(z):
                for j in range(y):
                    if j == y - 1:
                        block = self.grass.copyTo(self.base.render)
                    elif j > y - 5:
                        block = self.dirt.copyTo(self.base.render)
                    else:
                        block = self.stone.copyTo(self.base.render)
                    block.setPos(i * 2, k * 2, j * 2)


class Player:
    def __init__(self, base):
        self.base = base
        self.enabled = True
        self.control()

    def control(self):
        self.base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        props.setMouseMode(WindowProperties.MConfined)
        self.base.win.requestProperties(props)

        self.base.taskMgr.add(self.cameraControls, "cameraPointToMouse")

    def cameraControls(self, task):
        if not self.enabled:
            return Task.cont

        is_down = self.base.mouseWatcherNode.is_button_down
        speed = playerSpeed * globalClock.getDt()

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
            self.base.camera.setH(self.base.camera.getH() - deltaX * camSensativity)
            self.base.camera.setP(self.base.camera.getP() - deltaY * camSensativity)

        return Task.cont


class PyCraft(ShowBase):
    def __init__(self):
        super().__init__()

        self.world = World(self)
        self.player = Player(self)
        self.gui = GUI()
        self.world.generateTerrain(worldX, worldY, worldZ)
        self.taskMgr.add(self.occulsionCulling, "renderDistance")

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
