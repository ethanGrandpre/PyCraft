from direct.showbase.ShowBase import ShowBase

class PyCraft(ShowBase):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    base = PyCraft()
    base.run()