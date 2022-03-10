from aqt.qt import *

class My_List_Widget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def event(self, event):
        if (event.type() == QEvent.Type.KeyPress) and (event.key() == Qt.Key.Key_Space):
            print('spaced pressed')
        return QListWidget.event(self, event)
    
    def keyPressEvent(self, evt):
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
            super().keyPressEvent(evt)  # otherwise new text in the line won't be detected/saved
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
