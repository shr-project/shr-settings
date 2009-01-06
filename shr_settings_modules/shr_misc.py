import elementary, module

class Misc(module.AbstractModule):
    name = "Miscellaneous"
    
    def createView(self):
        la = elementary.Label(self.window)
        la.label_set("Suspend, dim time and etc.")
        return la

