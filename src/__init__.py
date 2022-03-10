# see license.txt

from .anki_version_detection import anki_point_version

from anki.hooks import addHook, wrap

if anki_point_version >= 24:
    from aqt import gui_hooks
from aqt import mw
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.editor import Editor
from aqt.tagedit import TagEdit
from aqt.utils import (
    tooltip,
)
from aqt.qt import (
    QAction,
    QKeySequence,
    QShortcut,
    qtmajor,
)

from .config import gc
from .fuzzy_panel import FilterDialog
from .tag_dialog_extended__BasicOrTagEdit import TagDialogExtended__BasicOrTagEdit
from .tag_dialog_extended__QListWidgetFromDesigner import TagDialogExtended__qlistwidget_scrollable

from .shared_variables import init_vars
init_vars()


def tagselector(self):
    all_tags = self.col.tags.all()
    d = FilterDialog(parent=self, values=all_tags, allownew=True)
    if d.exec():
        # self.setText(self.text() + " " + d.selkey)
        # order and remove duplicates 
        tags = mw.col.tags.split(self.text() + " " + d.selkey)
        uniquetags = list(set(tags))
        self.setText(mw.col.tags.join(mw.col.tags.canonify(uniquetags))) 
TagEdit.tagselector = tagselector


def myinit(self, parent, type=0):
    self.parent = parent
    cut = gc("editor: show filterdialog to add single tag")
    if cut:
        if hasattr(self, "isMyTagEdit") and self.isMyTagEdit:
            return
        # doesn't work in extended dialog since there are multiple TagEdits
        self.tagselector_cut = QShortcut(QKeySequence(cut), self)
        self.tagselector_cut.activated.connect(self.tagselector)
TagEdit.__init__ = wrap(TagEdit.__init__, myinit)








def get_tag_dialog(parent, tags, alltags):
    if len(tags) < gc("dialog type: scrollable if more tags than"):
        return TagDialogExtended__BasicOrTagEdit(parent, tags, alltags)
    else:
        # Extending TagDialogExtended__BasicOrTagEdit with QScrollArea
        # didn't work well. The scroll position didn't follow line
        # changes automatically and it seemed complicated to implement this
        return TagDialogExtended__qlistwidget_scrollable(parent, tags, alltags)



#### Browser/Editor
def edit_tag_dialogFromEditor(editor):
    fi = editor.currentField
    editor.saveNow(lambda e=editor, i=fi: _edit_tag_dialogFromEditor(e, i))
Editor.edit_tag_dialogFromEditor = edit_tag_dialogFromEditor


def _edit_tag_dialogFromEditor(editor, index):
    note = editor.note
    alltags = mw.col.tags.all()
    d = get_tag_dialog(editor.parentWindow, note.tags.copy(), alltags)
    if not d.exec():
        return
    tagString = d.tagstring
    if qtmajor == 5:
        note.setTagsFromStr(tagString)
    else:
        note.set_tags_from_str(tagString)
    if not editor.addMode:
        note.flush()
    addmode = editor.addMode
    editor.addMode = False
    tooltip('Edited tags "%s"' % tagString)
    editor.loadNote(focusTo=index)
    editor.addMode = addmode


# addHook("setupEditorShortcuts", SetupShortcuts) doesn't work when editor is not focused, e.g.
# if focus is on tag line. So using an editor shortcut here is bad.
def addAddshortcut(self, mw):
    cut = gc("open tag lines dialog: from editor")
    if cut:
        shortcut = QShortcut(QKeySequence(cut), self)
        shortcut.activated.connect(self.editor.edit_tag_dialogFromEditor)
if anki_point_version <= 49:
    AddCards.__init__ = wrap(AddCards.__init__, addAddshortcut)
    EditCurrent.__init__ = wrap(EditCurrent.__init__, addAddshortcut)


def handle_js_message(handled, message, context: Editor):
    if message == "1135507717_shorcut":
        editor = context
        editor.edit_tag_dialogFromEditor()
        return (True, "no result")
    else:
        return handled


# Damien wrote about setting about shortcuts in 2.1.50+ with js at
# https://forums.ankiweb.net/t/emacs-style-shortcuts-with-ctrl-t-in-the-editor-in-45/12280/8
# in 2.1.50+ the tag line is implemented in js so I no longer have the old limitation
# so that I can actually set up the shortcut in the Editor (instaed of Addcards or EditCurrent)
def add_editor_shortcut(editor):
    cut = gc("open tag lines dialog: from editor")
    cut = cut.replace("Ctrl", "Control")   # qt want "Ctrl", Js "Control"
    if not cut:
        return
    jsstring = """
function extended_tag_shortcut_callback(event) {
    event.preventDefault();
    pycmd("1135507717_shorcut");
}
require("anki/shortcuts").registerShortcut(extended_tag_shortcut_callback, "SHORTCUT");
""".replace("SHORTCUT", cut)
    editor.web.eval(jsstring)
if anki_point_version >= 50:
    gui_hooks.editor_did_init.append(add_editor_shortcut)
    gui_hooks.webview_did_receive_js_message.append(handle_js_message)



def EditorContextMenu(view, menu):
    a = menu.addAction('edit tags')
    a.triggered.connect(lambda _, e=view.editor: edit_tag_dialogFromEditor(e))
addHook("EditorWebView.contextMenuEvent", EditorContextMenu)


# allow to clone from the browser table (when you are not in the editor)
def browser_edit_tags(browser):
    if browser.editor.note:
        return edit_tag_dialogFromEditor(browser.editor)
    tooltip("only works if one card is selected.<br>the editor at the bottom of the browser window must be visible.", period=5000)


def setupMenu(browser):
    self = browser
    self.ExTaDiAction = QAction(browser)
    self.ExTaDiAction.setText("edit tags")
    cut = gc("open tag lines dialog: from editor", False)
    if cut:
        self.ExTaDiAction.setShortcut(QKeySequence(cut))
    self.ExTaDiAction.triggered.connect(lambda _, b=browser: browser_edit_tags(b))
    browser.form.menuEdit.addAction(self.ExTaDiAction)
addHook("browser.setupMenus", setupMenu)


def add_to_table_context_menu(browser, menu):
    menu.addAction(browser.ExTaDiAction)
#addHook("browser.onContextMenu", add_to_table_context_menu)


def edit_tag_dialogFromReviewer():
    note = mw.reviewer.card.note()
    alltags = mw.col.tags.all()
    d = get_tag_dialog(mw, note.tags, alltags)
    if not d.exec():
        return
    if qtmajor == 5:
        note.setTagsFromStr(d.tagstring)
    else:
        note.set_tags_from_str(d.tagstring)
    note.flush()
    tooltip('Edited tags "%s"' % d.tagstring)


def addShortcuts(cuts):
    cuts.append((gc("open tag lines dialog: from reviewer", "w"), edit_tag_dialogFromReviewer))
addHook("reviewStateShortcuts", addShortcuts)


def ReviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    a = menu.addAction('edit tags (shorcut: {})'.format(gc("open tag lines dialog: from reviewer", "w")))
    a.triggered.connect(edit_tag_dialogFromReviewer)
addHook("AnkiWebView.contextMenuEvent", ReviewerContextMenu)
