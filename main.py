#!/usr/bin/env python3
"""SchreibAssistent Pro - Version 0.0.1"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QStatusBar,
    QToolBar,
)

APP_NAME = "SchreibAssistent Pro"
VERSION = "0.0.1"


class Editor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Beginnen Sie hier mit Ihrem Schreiben …")
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setTabStopDistance(32)
        self.setFont(QFont("Noto Sans", 12))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file: Path | None = None
        self.editor = Editor()
        self.setCentralWidget(self.editor)
        self.setWindowTitle(f"{APP_NAME} – Neues Dokument")
        self.resize(1200, 760)
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_style()
        self.editor.textChanged.connect(self._update_status)

    def _create_actions(self):
        self.new_action = QAction("Neu", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_document)

        self.open_action = QAction("Öffnen …", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_document)

        self.save_action = QAction("Speichern", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_document)

        self.save_as_action = QAction("Speichern unter …", self)
        self.save_as_action.triggered.connect(self.save_as)

        self.exit_action = QAction("Beenden", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        self.cut_action = QAction("Ausschneiden", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction("Kopieren", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction("Einfügen", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.editor.paste)

    def _create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Datei")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu.addMenu("Bearbeiten")
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        undo = self.editor.undoAction()
        undo.setText("Rückgängig")
        redo = self.editor.redoAction()
        redo.setText("Wiederholen")
        edit_menu.addAction(undo)
        edit_menu.addAction(redo)

        help_menu = menu.addMenu("Hilfe")
        about = QAction("Über SchreibAssistent Pro", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def _create_toolbar(self):
        toolbar = QToolBar("Schnellzugriff")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.paste_action)
        self.addToolBar(toolbar)

    def _create_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._update_status()

    def _update_status(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.status.showMessage(f"{words} Wörter  •  {chars} Zeichen  •  Version {VERSION}")

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #f4f6f8; }
            QMenuBar { background: #ffffff; padding: 5px; }
            QMenuBar::item { padding: 7px 12px; border-radius: 6px; }
            QMenuBar::item:selected { background: #e8edf3; }
            QMenu { background: #ffffff; border: 1px solid #d8dee6; padding: 5px; }
            QMenu::item { padding: 8px 28px 8px 12px; border-radius: 5px; }
            QMenu::item:selected { background: #e8edf3; }
            QToolBar { background: #ffffff; border: none; border-bottom: 1px solid #dce2e8; padding: 7px; spacing: 5px; }
            QToolButton { padding: 7px 12px; border-radius: 6px; }
            QToolButton:hover { background: #e8edf3; }
            QPlainTextEdit { background: #ffffff; color: #20252b; border: none; padding: 42px 70px; selection-background-color: #cfe1ff; }
            QStatusBar { background: #ffffff; border-top: 1px solid #dce2e8; color: #66717d; padding: 4px 10px; }
        """)

    def new_document(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle(f"{APP_NAME} – Neues Dokument")

    def open_document(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Dokument öffnen", "", "Textdateien (*.txt);;Alle Dateien (*)"
        )
        if not filename:
            return
        try:
            path = Path(filename)
            self.editor.setPlainText(path.read_text(encoding="utf-8"))
            self.current_file = path
            self.setWindowTitle(f"{APP_NAME} – {path.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Öffnen fehlgeschlagen", str(exc))

    def save_document(self):
        if self.current_file is None:
            return self.save_as()
        self._write_file(self.current_file)

    def save_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Dokument speichern", "Neues Dokument.txt", "Textdateien (*.txt);;Alle Dateien (*)"
        )
        if not filename:
            return False
        path = Path(filename)
        if path.suffix == "":
            path = path.with_suffix(".txt")
        self.current_file = path
        return self._write_file(path)

    def _write_file(self, path: Path):
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.setWindowTitle(f"{APP_NAME} – {path.name}")
            self.status.showMessage(f"Gespeichert: {path}", 3000)
            return True
        except Exception as exc:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(exc))
            return False

    def show_about(self):
        QMessageBox.about(
            self,
            "Über SchreibAssistent Pro",
            f"<h2>{APP_NAME}</h2><p>Professioneller Schreib- und Dokumentenassistent für Linux.</p><p>Version {VERSION}</p>",
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("SchreibAssistent Pro")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
