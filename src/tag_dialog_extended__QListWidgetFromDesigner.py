from aqt import dialogs
from aqt import mw

from aqt.qt import (
    QDialog,
    QEvent,
    QKeySequence,
    QObject,
    QShortcut,
    Qt,
    qtmajor,
)

from aqt.utils import (
    restoreGeom,
    saveGeom,
    tooltip,
)
from .config import (
    gc,
)

from .anki_version_detection import anki_point_version
from .fuzzy_panel import FilterDialog
if qtmajor == 5:
    from .forms5 import dialog_qlistwidget  # type: ignore  # noqa
else:
    from .forms6 import dialog_qlistwidget  # type: ignore  # noqa


if anki_point_version < 20:
    class Object():
        pass
    theme_manager = Object()
    theme_manager.night_mode = False
else:
    from aqt.theme import theme_manager



stylesheet_dark = """
QListWidget {
    background-color: #2f2f31;
}
QListWidget::item {
    background-color: #3a3a3a;
    margin-top: 6px;
    margin-bottom: 6px;

    border-style: solid;
    border-width: 1px;
}
QListWidget::item:selected {
    border-color: #6daed3;
}
"""


stylesheet_light = """
QListWidget {
    background-color: #eff0f1;
}
QListWidget::item {
    background-color: #fcfcfc;
    margin-top: 6px;
    margin-bottom: 6px;

    border-style: solid;
    border-width: 1px;
}
QListWidget::item:selected {
    border-color: #77c2e8;
}
"""



class TagDialogExtended__qlistwidget_scrollable(QDialog):
    def __init__(self, parent, tags, alltags):
        QDialog.__init__(self, parent, Qt.WindowType.Window)  # super().__init__(parent)
        self.parent = parent
        self.all_tags = alltags
        self.setWindowTitle("Anki - Edit Tags")

        self.form = dialog_qlistwidget.Ui_Dialog()
        self.form.setupUi(self)
        
        sheet_to_use = stylesheet_dark if theme_manager.night_mode else stylesheet_light
        self.form.listWidget.setStyleSheet(sheet_to_use)
        # self.form.listWidget.currentRowChanged.connect(self.on_row_changed)

        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(self.reject)
        self.form.pb_search.clicked.connect(lambda: self.do_browser_search(extra_search=""))
        self.form.pb_edit_tag.clicked.connect(self.tagselector)
        self.form.pb_add_empty.clicked.connect(lambda: self.maybe_add_line(force=True))

        self.shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut.activated.connect(self.accept)

        originalheight = self.height()
        restoreGeom(self, "TagDialogExtended")
        self.resize(self.width(), originalheight)
        
        if not tags:
            tags = ["",]
        else:
            tags.append("")
        
        for t in tags:
            self.maybe_add_line(t)

        self.cut = gc("in tag lines dialog: open filterdialog for single tag")
        if self.cut:
            self.form.pb_edit_tag.setToolTip('shortcut: {}'.format(self.cut))
            self.selkey = QShortcut(QKeySequence(self.cut), self)
            self.selkey.activated.connect(self.tagselector)
        
        self.browser_scut = gc("in tag lines dialog: search browser for tag")
        if self.browser_scut:
            self.form.pb_search.setToolTip('shortcut: {}'.format(self.browser_scut))
            self.browser_scut_key = QShortcut(QKeySequence(self.browser_scut), self)
            self.browser_scut_key.activated.connect(lambda: self.do_browser_search(extra_search=""))
        
        # don't also set Ctrl+t,a/gc("editor: show filterdialog to add single tag") for 
        # self.tagselector: What if the user has already set them to the same etc. I'd have
        # to do a lot of checking
        self.addnl = gc("in tag lines dialog: insert additional line")
        if self.addnl:
            self.form.pb_add_empty.setToolTip('shortcut: {}'.format(self.addnl))
            self.addnlscut = QShortcut(QKeySequence(self.addnl), self)
            self.addnlscut.activated.connect(lambda: self.maybe_add_line(force=True))       

    def current_tags_list(self):
        all_tags = []
        for i in range(self.form.listWidget.count()):
            text = self.form.listWidget.item(i).text()
            if text:
                all_tags.append(text)
        return all_tags

    def do_browser_search(self, extra_search=""):
        # Use the current line's text or the last line if the current one is an empty line
        note_tags = self.current_tags_list()
        searched_tag = self.form.listWidget.currentItem().text() or (note_tags[-1] if len(note_tags)>0 else "")
        if searched_tag:
            browser = dialogs.open('Browser', mw)
            browser.setFilter('tag:"{}*" {}'.format(searched_tag, extra_search))
            self.accept()
        else:
            tooltip("empty tag was selected for search")

    def tagselector(self):
        text = self.form.listWidget.currentItem().text()
        d = FilterDialog(parent=self, values=self.all_tags, allownew=True, prefill=text)
        if d.exec():
            self.form.listWidget.currentItem().setText(d.selkey)

    def change_focus_by_one(self, go_down=True):
        source_row = self.form.listWidget.currentRow()
        if go_down:
            new_row = min(source_row + 1, self.form.listWidget.count())
        else:
            new_row = max(source_row - 1, 0)
        item_to_focus = self.form.listWidget.item(new_row)
        self.form.listWidget.setCurrentItem(item_to_focus)
        self.form.listWidget.setCurrentRow(new_row)

    def maybe_add_line(self, tag="", force=False):
        # TODO/BROKEN: if last line is empty don't add a new line, just focus the last line
        # if cur_row < idx_last_line and row_count >= 1:   
        #     if not text_in_last and not force:  # last lineedit is empty:
        #         last_item = self.form.listWidget.item(row_count - 1)
        #         self.form.listWidget.setCurrentItem(last_item)
        #         self.form.listWidget.setCurrentRow(row_count - 1)
        #         return
        self.form.listWidget.addItem(tag)
        self.make_all_lines_editable()
        row_count = self.form.listWidget.count()
        last_item = self.form.listWidget.item(row_count - 1)
        # these two focus the last line but I still can't type in it directly
        # only after arrow_up, arrow_down ??
        # self.form.listWidget.setCurrentItem(last_item)
        # self.form.listWidget.setCurrentRow(row_count - 1) # , QItemSelectionModel.SelectionFlag.Select)
        
        # relevant when button clicked
        if not self.form.listWidget.hasFocus():
            self.form.listWidget.setFocus()

    def make_all_lines_editable(self):
        # a lot of unneeded work, but this makes sure I don't have an uneditable
        # line by accident ...
        for i in range(self.form.listWidget.count()):
            item = self.form.listWidget.item(i)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

    def accept(self):
        self.tagstring = ""
        for t in self.current_tags_list():
            self.tagstring += f"{t} "
        saveGeom(self, "TagDialogExtended")
        QDialog.accept(self)

    def reject(self):
        saveGeom(self, "TagDialogExtended")
        QDialog.reject(self)
