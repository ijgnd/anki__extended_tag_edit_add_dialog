from aqt import dialogs
from aqt import mw

from aqt.qt import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QKeySequence,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    Qt,
)

from aqt.utils import (
    restoreGeom,
    saveGeom,
    tooltip,
)
from .config import (
    gc,
)

from . import shared_variables
from .fuzzy_panel import FilterDialog
from .my_basic_line_edit import MyBasicEdit
from .my_tag_edit import MyTagEdit


class TagDialogExtended__BasicOrTagEdit(QDialog):
    def __init__(self, parent, tags, alltags):
        QDialog.__init__(self, parent, Qt.WindowType.Window)  # super().__init__(parent)
        self.basic_mode = gc("dialog type: basic_but_quick")
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
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut.activated.connect(self.accept)
        self.helpButton = QPushButton("add empty line", clicked=lambda: self.maybe_add_line(force=True))
        self.buttonBox.addButton(self.helpButton, QDialogButtonBox.ButtonRole.HelpRole)
        self.filterbutton = QPushButton("edit tag for current line", clicked=self.tagselector)
        self.buttonBox.addButton(self.filterbutton, QDialogButtonBox.ButtonRole.ResetRole)
        self.searchButton = QPushButton("search", clicked=lambda: self.do_browser_search(extra_search=""))
        self.buttonBox.addButton(self.searchButton, QDialogButtonBox.ButtonRole.ResetRole)
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
        self.line_list = []
        for t in tags:
            self.maybe_add_line(t)
        self.cut = gc("in tag lines dialog: open filterdialog for single tag")
        if self.cut:
            self.filterbutton.setToolTip('shortcut: {}'.format(self.cut))
            self.selkey = QShortcut(QKeySequence(self.cut), self)
            self.selkey.activated.connect(self.tagselector)
        self.browser_scut = gc("in tag lines dialog: search browser for tag")
        if self.browser_scut:
            self.searchButton.setToolTip('shortcut: {}'.format(self.browser_scut))
            self.browser_scut_key = QShortcut(QKeySequence(self.browser_scut), self)
            self.browser_scut_key.activated.connect(lambda: self.do_browser_search(extra_search=""))
        # don't also set Ctrl+t,a/gc("editor: show filterdialog to add single tag") for 
        # self.tagselector: What if the user has already set them to the same etc. I'd have
        # to do a lot of checking
        self.addnl = gc("in tag lines dialog: insert additional line")
        if self.addnl:
            self.helpButton.setToolTip('shortcut: {}'.format(self.addnl))
            self.addnlscut = QShortcut(QKeySequence(self.addnl), self)
            self.addnlscut.activated.connect(lambda: self.maybe_add_line(force=True))       

    def current_tags_list(self):
        return [t.text() for t in self.line_list if t]

    def do_browser_search(self, extra_search=""):
        # Use the current line's text or the last line if the current one is an empty line
        note_tags = self.current_tags_list()
        searched_tag = shared_variables.focused_line.text() or (note_tags[-1] if len(note_tags)>0 else "")
        if searched_tag:
            browser = dialogs.open('Browser', mw)
            browser.setFilter('tag:"{}*" {}'.format(searched_tag, extra_search))
            self.accept()
        else:
            tooltip("empty tag was selected for search")

    def tagselector(self):
        text = shared_variables.focused_line.text()
        d = FilterDialog(parent=self, values=self.alltags, allownew=True, prefill=text)
        if d.exec():
            shared_variables.focused_line.setText(d.selkey)
        else:
            shared_variables.focused_line.setFocus()

    def change_focus_by_one(self, Down=True):
        for index, edit in enumerate(self.line_list):
            if edit == shared_variables.focused_line:
                if Down:
                    if index == len(self.line_list)-1:  # if in last line go up
                        self.line_list[0].setFocus()
                        break
                    else:
                        newidx = index+1
                        self.line_list[newidx].setFocus()
                        break
                else:  # go up
                    if index == 0:  # if in last line go up
                        newidx = len(self.line_list)-1
                        self.line_list[newidx].setFocus()
                        break
                    else:
                        self.line_list[index-1].setFocus()
                        break

    def maybe_add_line(self, tag="", force=False):
        if self.line_list and not self.line_list[-1].text() and not force:  # last lineedit is empty:
            self.line_list[-1].setFocus()
            self.line_list[-1].setText(tag)
        else:
            if self.basic_mode:
                te = MyBasicEdit(self)
                te.setText(tag)
                self.verticalLayout.addWidget(te)
                te.setFocus()
                self.line_list.append(te)
            else:
                te = MyTagEdit(self)
                te.setCol(mw.col)
                te.setText(tag)
                self.verticalLayout.addWidget(te)
                te.hideCompleter()
                te.setFocus()
                self.line_list.append(te)

    def accept(self):
        self.tagstring = ""
        for t in self.line_list:
            if not self.basic_mode:
                t.hideCompleter()
            text = t.text()
            if text:
                self.tagstring += text + " "
        saveGeom(self, "TagDialogExtended")
        QDialog.accept(self)

    def reject(self):
        saveGeom(self, "TagDialogExtended")
        QDialog.reject(self)