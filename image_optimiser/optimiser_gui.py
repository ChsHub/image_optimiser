from utility.logger import Logger
from wx import BoxSizer, VERTICAL
from wx import Frame, ID_ANY, App, EXPAND, Panel, EVT_CLOSE

from image_optimiser.main import convert


class GUI(Frame):

    def __init__(self, *callbacks):
        Frame.__init__(self, None, ID_ANY, "CUT")
        self.Bind(EVT_CLOSE, lambda x: self.Destroy())
        root = Panel(self, EXPAND)
        sizer = BoxSizer(VERTICAL)

        elements = []
        for element in callbacks:
            sizer.Add(element, 1, EXPAND)

        root.SetSizer(sizer)


# Run the program
def init_gui():
    app = App(False)
    frame = GUI()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    log = Logger(50)
    init_gui()
    convert("")
    log.shutdown()
