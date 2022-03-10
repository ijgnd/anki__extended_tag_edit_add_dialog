from aqt.qt import *

from .config import (
    gc,
)
from . import shared_variables


class MyBasicEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.isMyTagEdit = False

    def focusInEvent(self, event):
        shared_variables.focused_line = self
        super().focusInEvent(event)

    def keyPressEvent(self, evt):
        modctrl = evt.modifiers() & Qt.KeyboardModifier.ControlModifier
        sp = None # gc("tag dialog space")
        if evt.key() == Qt.Key.Key_Space:
            if sp:
                if sp.lower() in ["return", "enter"]:
                    sp = Qt.Key.Key_Space
                else:
                    self.setText(self.text() + sp)
                    return
            else:
                sp = Qt.Key.Key_Space
        if evt.key() in (sp, Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
            if (evt.key() == Qt.Key.Key_Tab and modctrl):
                super().keyPressEvent(evt)
            else:
                self.parent.maybe_add_line()
                return
        elif (evt.key() == Qt.Key.Key_Up) or (modctrl and evt.key() == Qt.Key.Key_P):
            self.parent.change_focus_by_one(False)
            return
        elif (evt.key() == Qt.Key.Key_Down) or (modctrl and evt.key() == Qt.Key.Key_N):
            self.parent.change_focus_by_one()
            return
        else:
            super().keyPressEvent(evt)