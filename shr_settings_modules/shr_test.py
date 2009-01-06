import elementary, module

class Test(module.AbstractModule):
    def totest(self, obj, event, *argns, **kargs):
        print event
        print "it works!"
        obj.label_set("lol")
    def name(self, ):
        print "name"
        return "Test"
    def isEnabled(self):
        return False
    def createView(self):
        bt = elementary.Button(self.window)
        bt.clicked = self.totest
        bt.label_set("Just for fun")
        bt.size_hint_align_set(-1.0, 0.0)
        bt.show()

        return bt

