from aqt.qt import *
from aqt.tagedit import TagEdit

from .config import (
    gc,
)
from . import shared_variables


class MyTagEdit(TagEdit):
    def __init__(self, parent, type=0):
        super().__init__(parent, type=0)
        self.isMyTagEdit = True

    def focusInEvent(self, event):
        shared_variables.focused_line = self
        super().focusInEvent(event)

    def keyPressEvent(self, evt):
        modctrl = evt.modifiers() & Qt.KeyboardModifier.ControlModifier 
        sp = gc("tag dialog space")
        if evt.key() == Qt.Key.Key_Space:
            if sp:
                if sp.lower() in ["return", "enter"]:
                    sp = Qt.Key.Key_Space
                else:
                    self.setText(self.text() + sp)
                    return
            else:
                sp = Qt.Key.Key_Space
        # TODO: check changes from 2020-10 in 44e3ef690fa0a64638e14a51e9e1cd2706715e31
        if evt.key() in (sp, Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
            if (evt.key() == Qt.Key.Key_Tab and evt.modifiers() & Qt.KeyboardModifier.ControlModifier):
                super().keyPressEvent(evt)
            else:
                selected_row = self.completer.popup().currentIndex().row()
                if selected_row == -1:
                    self.completer.setCurrentRow(0)
                    index = self.completer.currentIndex()
                    self.completer.popup().setCurrentIndex(index)
                self.hideCompleter()
                # QWidget.keyPressEvent(self, evt)
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
