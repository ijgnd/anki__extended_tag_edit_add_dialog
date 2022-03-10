from aqt.qt import *

from aqt.utils import tooltip



class My_List_Widget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    """
    # event and keyPressEvent must be modified here. QListWidgetItem doesn't have
    # these events
    def event(self, event):
        # this is strange: QEvent.Type.KeyPress is not detected
        # According to https://doc.qt.io/qt-5/qevent.html#Type-enum
        # a KreyPress has the Value 6.
        # But when I use 'print(event.type())' I never get a 6.
        # Close to pressing a key only the value 7 is printed which means
        # KeyRelease.
        # KeyRelease gets detected but the next problem is that
        # this 'event.key() == Qt.Key.Key_Space' never evaluates to True
        # even though I press Space
        # So I looked into https://doc.qt.io/qt-5/qkeyevent.html
        # and now I compare the event (key) text, i.e. event.text() == " " 
        # which seems to work ...
        # So far I haven't noticed a side effct.
        if (event.type() == QEvent.Type.KeyRelease) and event.text() == " ":
            print('spaced pressed')
        return QListWidget.event(self, event)
    """

    def keyReleaseEvent(self, event):
        # see my notes in 'def event'
        if event.text() == " ":
            print('spaced pressed')
            # the following does not work: this deletes what's in the current line
            # tooltip("space is not allowed in tags")
            # self.parent.maybe_add_line()
        super().keyReleaseEvent(event)
    
    def keyPressEvent(self, evt):
        # doesn't detect space, see my notes in 'def event'
        modctrl = evt.modifiers() & Qt.KeyboardModifier.ControlModifier
        """
        BROKEN:
        sp = False # gc("tag dialog space")
        if evt.key() == Qt.Key.Key_Space:
            # if sp:
            #     if sp.lower() in ["return", "enter"]:
            #         sp = Qt.Key.Key_Space
            #     else:
            #         self.setText(self.text() + sp)
            #         return
            # else:
            #     sp = Qt.Key.Key_Space
            return
        if evt.key() in (sp, Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
            if (evt.key() == Qt.Key.Key_Tab and modctrl):
                return super().keyPressEvent(evt)
            else:
                self.parent.print_text()
                self.parent.maybe_add_line()
                return
        if evt.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            super().keyPressEvent(evt)  #  new text in the line won't be detected/saved
            # the following does not work: this deletes what's in the current line
            self.parent.maybe_add_line()
            return
        """
        if False:
            pass
        elif modctrl and evt.key() == Qt.Key.Key_P:
            self.parent.change_focus_by_one(go_down=False)
            return
        elif modctrl and evt.key() == Qt.Key.Key_N:
            self.parent.change_focus_by_one(go_down=True)
            return
        else:
            super().keyPressEvent(evt)
