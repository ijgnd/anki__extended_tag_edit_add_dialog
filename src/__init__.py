# Anki Add-on "Extended tag add/edit dialog"
#
# Copyright (c): 2019- ijgnd
#                2018 Rene Schallner (fuzzy_panel.py)
#     
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from anki.lang import _
from anki.hooks import addHook, wrap

from aqt import mw
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.editor import Editor
from aqt.browser import Browser
from aqt.tagedit import TagEdit
from aqt.utils import getTag, tooltip, showInfo, restoreGeom, saveGeom  # getText
from aqt.qt import *
from aqt.reviewer import Reviewer

from .fuzzy_panel import FilterDialog


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


night_mode_on = False
def refresh_night_mode_state(nm_state):
    global night_mode_on
    night_mode_on = nm_state
addHook("night_mode_state_changed", refresh_night_mode_state)


def tagselector(self):
    alltags = self.col.tags.all()
    d = FilterDialog(parent=self, values=alltags, allownew=True)
    if d.exec():
        # self.setText(self.text() + " " + d.selkey)
        # order and remove duplicates 
        tags = mw.col.tags.split(self.text() + " " + d.selkey)
        uniquetags = list(set(tags))
        self.setText(mw.col.tags.join(mw.col.tags.canonify(uniquetags))) 
TagEdit.tagselector = tagselector


def myinit(self, parent, type=0):
    self.parent = parent
    cut = gc("select and insert tag dialog shortcut - browser, add, edit current window")
    if cut:
        if hasattr(self, "isMyTagEdit") and self.isMyTagEdit:
            return
        # doesn't work in extended dialog since there are multiple TagEdits
        self.tagselector_cut = QShortcut(QKeySequence(cut), self)
        self.tagselector_cut.activated.connect(self.tagselector)
TagEdit.__init__ = wrap(TagEdit.__init__, myinit)


class MyTagEdit(TagEdit):
    def __init__(self, parent, type=0):
        super().__init__(parent, type=0)
        self.isMyTagEdit = True

    def keyPressEvent(self, evt):
        if evt.key() in (Qt.Key_Space, Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
            if (evt.key() == Qt.Key_Tab and evt.modifiers() & Qt.ControlModifier):
                super().keyPressEvent(evt)
            else:
                selected_row = self.completer.popup().currentIndex().row()
                if selected_row == -1:
                    self.completer.setCurrentRow(0)
                    index = self.completer.currentIndex()
                    self.completer.popup().setCurrentIndex(index)
                self.hideCompleter()
                # QWidget.keyPressEvent(self, evt)
                self.parent.addline()
                return
        else:
            super().keyPressEvent(evt)


class TagDialogExtended(QDialog):
    def __init__(self, parent, tags, alltags):
        QDialog.__init__(self, parent, Qt.Window)  # super().__init__(parent)
        self.parent = parent
        self.alltags = alltags
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QLabel("Edit tags:")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut.activated.connect(self.accept)
        self.helpButton = QPushButton("add empty line", clicked=lambda: self.addline(force=True))
        self.buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        self.filterbutton = QPushButton("insert tag", clicked=self.tagselector)
        self.buttonBox.addButton(self.filterbutton, QDialogButtonBox.ResetRole)
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("Anki - Edit Tags")
        originalheight = self.height()
        restoreGeom(self, "TagDialogExtended")
        self.resize(self.width(), originalheight)
        if not tags:
            tags = ["",]
        else:
            tags.append("")
        self.tes = []
        for t in tags:
            self.addline(t)
        self.cut = gc("select and insert tag dialog shortcut for edit tag dialog")
        if self.cut:
            self.selkey = QShortcut(QKeySequence(self.cut), self)
            self.selkey.activated.connect(self.tagselector)

    def tagselector(self):
        d = FilterDialog(parent=self, values=self.alltags, allownew=True)
        if d.exec():
            fcsd = self.focusWidget()
            if isinstance(fcsd, (MyTagEdit)) and not fcsd.text():
                fcsd.setText(d.selkey)
            else:
                self.addline(tag=d.selkey) 

    def addline(self, tag="", force=False):
        if self.tes and not self.tes[-1].text() and not force:  # last lineedit is empty:
            self.tes[-1].setFocus()
            self.tes[-1].setText(tag)
        else:
            te = MyTagEdit(self)
            te.setCol(mw.col)
            te.setText(tag)
            self.verticalLayout.addWidget(te)
            te.hideCompleter()
            te.setFocus()
            self.tes.append(te)

    def accept(self):
        self.tagstring = ""
        for t in self.tes:
            t.hideCompleter()
            text = t.text()
            if text:
                self.tagstring += text + " "
        saveGeom(self, "TagDialogExtended")
        QDialog.accept(self)

    def reject(self):
        saveGeom(self, "TagDialogExtended")
        QDialog.reject(self)


#### Browser/Editor
def edit_tag_dialogFromEditor(editor):
    fi = editor.currentField
    editor.saveNow(lambda e=editor, i=fi: _edit_tag_dialogFromEditor(e, i))
Editor.edit_tag_dialogFromEditor = edit_tag_dialogFromEditor


def _edit_tag_dialogFromEditor(editor, index):
    mw.checkpoint(_("Edit Tags"))
    note = editor.note
    alltags = mw.col.tags.all()
    d = TagDialogExtended(editor.parentWindow, note.tags, alltags)
    if not d.exec():
        return
    tagString = d.tagstring
    note.setTagsFromStr(tagString)
    note.flush()
    addmode = editor.addMode
    editor.addMode = False
    tooltip('Edited tags "%s"' % tagString)
    editor.loadNote(focusTo=index)
    editor.addMode = addmode


# addHook("setupEditorShortcuts", SetupShortcuts) doesn't work when editor is not focused, e.g.
# if focus is on tag line. So using an editor shortcut here is bad.
def addAddshortcut(self, mw):
    cut = gc("tag dialog shortcut - browser, add, edit current window")
    if cut:
        shortcut = QShortcut(QKeySequence(cut), self)
        shortcut.activated.connect(self.editor.edit_tag_dialogFromEditor)
AddCards.__init__ = wrap(AddCards.__init__, addAddshortcut)
EditCurrent.__init__ = wrap(EditCurrent.__init__, addAddshortcut)


def EditorContextMenu(view, menu):
    a = menu.addAction('edit tags')
    a.triggered.connect(lambda _, e=view.editor: edit_tag_dialogFromEditor(e))
addHook("EditorWebView.contextMenuEvent", EditorContextMenu)


# allow to clone from the browser table (when you are not in the editor)
def browser_edit_tags(browser):
    if len(browser.selectedCards()) == 1:
        return edit_tag_dialogFromEditor(browser.editor)
    tooltip("only works if one card is selected")


def setupMenu(browser):
    global myaction
    myaction = QAction(browser)
    myaction.setText("edit tags")
    cut = gc("tag dialog shortcut - browser, add, edit current window", False)
    if cut:
        myaction.setShortcut(QKeySequence(cut))
    myaction.triggered.connect(lambda _, b=browser: browser_edit_tags(b))
    browser.form.menuEdit.addAction(myaction)
addHook("browser.setupMenus", setupMenu)


def add_to_table_context_menu(browser, menu):
    menu.addAction(myaction)
addHook("browser.onContextMenu", add_to_table_context_menu)


def edit_tag_dialogFromReviewer():
    mw.checkpoint(_("Edit Tags"))
    note = mw.reviewer.card.note()
    alltags = mw.col.tags.all()
    d = TagDialogExtended(mw, note.tags, alltags)
    if not d.exec():
        return
    tagString = d.tagstring
    note.setTagsFromStr(tagString)
    note.flush()
    tooltip('Edited tags "%s"' % tagString)


def addShortcuts(cuts):
    cuts.append((gc("tag dialog shortcut - reviewer", "w"), edit_tag_dialogFromReviewer))
addHook("reviewStateShortcuts", addShortcuts)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    a = menu.addAction('edit tags (shorcut: {})'.format(gc("tag dialog shortcut - reviewer", "w")))
    a.triggered.connect(edit_tag_dialogFromReviewer)
addHook("AnkiWebView.contextMenuEvent", ReviewerContextMenu)
