#!/usr/bin/env python3
"""SchreibAssistent Pro – Version 0.0.2."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "SchreibAssistent Pro"
VERSION = "0.0.2"


class Editor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Hier beginnt Ihr Schreiben …")
        self.setFont(QFont("Noto Sans", 12))
        self.setTabStopDistance(32)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setUndoRedoEnabled(True)
        self.setFrameStyle(QFrame.NoFrame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.document_title = "Neues Dokument"

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1000, 650)
        self.resize(1280, 800)

        self._build_ui()
        self._build_actions()
        self._connect_signals()
        self._apply_style()
        self._update_document_info()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(235)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(18, 22, 18, 18)
        side.setSpacing(8)

        logo = QLabel("SchreibAssistent")
        logo.setObjectName("logo")
        side.addWidget(logo)
        version = QLabel(f"PRO  •  {VERSION}")
        version.setObjectName("version")
        side.addWidget(version)
        side.addSpacing(24)

        self.nav_home = self._nav_button("⌂  Start")
        self.nav_docs = self._nav_button("▤  Dokumente")
        self.nav_templates = self._nav_button("▱  Vorlagen")
        self.nav_ai = self._nav_button("✦  KI-Assistent")
        self.nav_settings = self._nav_button("⚙  Einstellungen")

        for button in [self.nav_home, self.nav_docs, self.nav_templates, self.nav_ai, self.nav_settings]:
            side.addWidget(button)
        side.addStretch()

        info = QLabel("Schnell, übersichtlich\nund professionell.")
        info.setObjectName("sidebarInfo")
        side.addWidget(info)
        root_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        root_layout.addWidget(self.pages, 1)

        self.home_page = self._build_home_page()
        self.editor_page = self._build_editor_page()
        self.docs_page = self._build_documents_page()
        self.templates_page = self._build_templates_page()
        self.ai_page = self._build_ai_page()
        self.settings_page = self._build_settings_page()

        for page in [self.home_page, self.editor_page, self.docs_page, self.templates_page, self.ai_page, self.settings_page]:
            self.pages.addWidget(page)

    def _nav_button(self, text):
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(44)
        return button

    def _header(self, title, subtitle=""):
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("pageSubtitle")
            layout.addWidget(sub)
        return box

    def _build_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(24)
        layout.addWidget(self._header("Guten Abend", "Was möchten Sie heute erledigen?"))

        actions = QHBoxLayout()
        actions.setSpacing(16)
        actions.addWidget(self._card_button("＋", "Neues Dokument", "Direkt losschreiben", self.new_document))
        actions.addWidget(self._card_button("▣", "Dokument öffnen", "Bestehende Datei öffnen", self.open_document))
        actions.addWidget(self._card_button("✦", "KI-Assistent", "Text verbessern und formulieren", lambda: self.pages.setCurrentWidget(self.ai_page)))
        layout.addLayout(actions)

        recent_title = QLabel("Zuletzt verwendet")
        recent_title.setObjectName("sectionTitle")
        layout.addWidget(recent_title)

        recent = QFrame()
        recent.setObjectName("panel")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(22, 18, 22, 18)
        empty = QLabel("Noch keine Dokumente geöffnet.\nErstellen Sie Ihr erstes Dokument mit „Neues Dokument“. ")
        empty.setObjectName("emptyText")
        recent_layout.addWidget(empty)
        layout.addWidget(recent)
        layout.addStretch()
        return page

    def _card_button(self, icon, title, subtitle, callback):
        button = QPushButton()
        button.setObjectName("actionCard")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(145)
        box = QVBoxLayout(button)
        box.setContentsMargins(20, 18, 20, 18)
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        box.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        box.addWidget(title_label)
        sub = QLabel(subtitle)
        sub.setObjectName("cardSubtitle")
        box.addWidget(sub)
        box.addStretch()
        button.clicked.connect(callback)
        return button

    def _build_editor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 28, 36, 24)
        layout.setSpacing(12)

        top = QHBoxLayout()
        self.back_button = QPushButton("‹  Zurück")
        self.back_button.setObjectName("smallButton")
        top.addWidget(self.back_button)
        top.addStretch()
        self.save_button = QPushButton("Speichern")
        self.save_button.setObjectName("primaryButton")
        top.addWidget(self.save_button)
        layout.addLayout(top)

        self.title_edit = QPushButton("Neues Dokument")
        self.title_edit.setObjectName("documentTitle")
        self.title_edit.setCursor(Qt.PointingHandCursor)
        self.title_edit.setToolTip("Klicken Sie hier, um den Dokumentnamen zu ändern")
        layout.addWidget(self.title_edit)

        self.editor = Editor()
        editor_frame = QFrame()
        editor_frame.setObjectName("editorFrame")
        frame_layout = QVBoxLayout(editor_frame)
        frame_layout.setContentsMargins(32, 22, 32, 22)
        frame_layout.addWidget(self.editor)
        layout.addWidget(editor_frame, 1)

        bottom = QHBoxLayout()
        self.word_count = QLabel("0 Wörter")
        self.char_count = QLabel("0 Zeichen")
        bottom.addWidget(self.word_count)
        bottom.addWidget(self.char_count)
        bottom.addStretch()
        bottom.addWidget(QLabel(f"SchreibAssistent Pro {VERSION}"))
        layout.addLayout(bottom)
        return page

    def _build_documents_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(20)
        layout.addWidget(self._header("Dokumente", "Ihre Schriftstücke an einem Ort."))

        buttons = QHBoxLayout()
        new = QPushButton("＋ Neues Dokument")
        new.setObjectName("primaryButton")
        new.clicked.connect(self.new_document)
        open_btn = QPushButton("Öffnen …")
        open_btn.setObjectName("secondaryButton")
        open_btn.clicked.connect(self.open_document)
        buttons.addWidget(new)
        buttons.addWidget(open_btn)
        buttons.addStretch()
        layout.addLayout(buttons)

        panel = QFrame()
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        self.document_list = QListWidget()
        self.document_list.setObjectName("documentList")
        p.addWidget(self.document_list)
        layout.addWidget(panel, 1)
        return page

    def _build_templates_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(20)
        layout.addWidget(self._header("Vorlagen", "Häufige Schreiben schnell erstellen."))
        templates = [
            ("Geschäftsbrief", "Klassischer formeller Brief"),
            ("Beschwerde", "Sachlich und klar formulieren"),
            ("Anfrage", "Professionelle Anfrage"),
            ("Kündigung", "Vorbereitete Kündigung"),
            ("E-Mail", "Professionelle E-Mail"),
        ]
        for name, description in templates:
            button = QPushButton(f"{name}\n{description}")
            button.setObjectName("templateButton")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, n=name: self.use_template(n))
            layout.addWidget(button)
        layout.addStretch()
        return page

    def _build_ai_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(18)
        layout.addWidget(self._header("KI-Assistent", "Die Oberfläche ist vorbereitet – die KI-Anbindung folgt als eigenes Modul."))
        panel = QFrame()
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(28, 28, 28, 28)
        title = QLabel("Was soll mit Ihrem Text passieren?")
        title.setObjectName("sectionTitle")
        p.addWidget(title)
        for text in ["Text verbessern", "Rechtschreibung prüfen", "Formeller formulieren", "Kürzer formulieren"]:
            b = QPushButton(text)
            b.setObjectName("secondaryButton")
            b.clicked.connect(lambda checked=False, t=text: self.ai_placeholder(t))
            p.addWidget(b)
        layout.addWidget(panel)
        layout.addStretch()
        return page

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(18)
        layout.addWidget(self._header("Einstellungen", "Grundlegende Einstellungen für SchreibAssistent Pro."))
        panel = QFrame()
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(28, 28, 28, 28)
        for text in ["Erscheinungsbild", "Dokumente", "Speicherort", "Tastenkürzel"]:
            b = QPushButton(text)
            b.setObjectName("settingButton")
            b.clicked.connect(lambda checked=False, t=text: self.settings_placeholder(t))
            p.addWidget(b)
        layout.addWidget(panel)
        layout.addStretch()
        return page

    def _build_actions(self):
        self.action_new = QAction("Neues Dokument", self)
        self.action_new.setShortcut(QKeySequence("Ctrl+N"))
        self.action_new.triggered.connect(self.new_document)
        self.addAction(self.action_new)

        self.action_open = QAction("Dokument öffnen", self)
        self.action_open.setShortcut(QKeySequence("Ctrl+O"))
        self.action_open.triggered.connect(self.open_document)
        self.addAction(self.action_open)

        self.action_save = QAction("Speichern", self)
        self.action_save.setShortcut(QKeySequence("Ctrl+S"))
        self.action_save.triggered.connect(self.save_document)
        self.addAction(self.action_save)

        self.action_undo = QAction("Rückgängig", self)
        self.action_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self.action_undo.triggered.connect(lambda: self.editor.undo())
        self.addAction(self.action_undo)

        self.action_redo = QAction("Wiederholen", self)
        self.action_redo.setShortcut(QKeySequence("Ctrl+Y"))
        self.action_redo.triggered.connect(lambda: self.editor.redo())
        self.addAction(self.action_redo)

    def _connect_signals(self):
        self.nav_home.clicked.connect(lambda: self.pages.setCurrentWidget(self.home_page))
        self.nav_docs.clicked.connect(lambda: self.pages.setCurrentWidget(self.docs_page))
        self.nav_templates.clicked.connect(lambda: self.pages.setCurrentWidget(self.templates_page))
        self.nav_ai.clicked.connect(lambda: self.pages.setCurrentWidget(self.ai_page))
        self.nav_settings.clicked.connect(lambda: self.pages.setCurrentWidget(self.settings_page))
        self.back_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.home_page))
        self.save_button.clicked.connect(self.save_document)
        self.editor.textChanged.connect(self._update_document_info)
        self.title_edit.clicked.connect(self.rename_document)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #f5f7fa; }
            #sidebar { background: #17202b; }
            #logo { color: white; font-size: 20px; font-weight: 700; }
            #version { color: #91a0b2; font-size: 11px; font-weight: 600; }
            #sidebarInfo { color: #718096; font-size: 12px; padding-top: 12px; }
            #navButton { color: #c7d0db; background: transparent; border: none; border-radius: 9px; text-align: left; padding: 0 14px; font-size: 14px; }
            #navButton:hover { background: #263444; color: white; }
            #navButton:pressed { background: #33465b; }
            #pageTitle { color: #18212b; font-size: 29px; font-weight: 700; }
            #pageSubtitle { color: #6d7885; font-size: 14px; }
            #sectionTitle { color: #25303b; font-size: 17px; font-weight: 650; }
            #panel, #editorFrame { background: white; border: 1px solid #e1e6ec; border-radius: 14px; }
            #actionCard { background: white; border: 1px solid #e0e6ed; border-radius: 14px; text-align: left; }
            #actionCard:hover { border: 1px solid #9fb7d2; background: #fbfdff; }
            #cardIcon { color: #356ea8; font-size: 25px; font-weight: 600; }
            #cardTitle { color: #202a35; font-size: 16px; font-weight: 650; }
            #cardSubtitle, #emptyText { color: #7a8591; font-size: 13px; }
            #primaryButton { background: #356ea8; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-weight: 600; }
            #primaryButton:hover { background: #2d6095; }
            #secondaryButton, #smallButton { background: white; color: #344150; border: 1px solid #d6dde5; border-radius: 8px; padding: 9px 16px; }
            #secondaryButton:hover, #smallButton:hover { background: #f1f4f7; }
            #documentTitle { background: transparent; border: none; color: #1d2731; font-size: 24px; font-weight: 700; text-align: left; padding: 4px 0; }
            #editorFrame { border-radius: 12px; }
            QPlainTextEdit { color: #242b33; background: white; selection-background-color: #c9dcf2; }
            #templateButton, #settingButton { background: white; border: 1px solid #e0e5eb; border-radius: 10px; padding: 15px; text-align: left; color: #2c3742; font-size: 14px; }
            #templateButton:hover, #settingButton:hover { background: #f8fafc; border-color: #b8c8d9; }
            #documentList { border: none; background: transparent; }
        """)

    def _update_document_info(self):
        if not hasattr(self, "editor"):
            return
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        self.word_count.setText(f"{words} Wörter")
        self.char_count.setText(f"{len(text)} Zeichen")

    def new_document(self):
        self.editor.clear()
        self.current_file = None
        self.document_title = "Neues Dokument"
        self.title_edit.setText(self.document_title)
        self.pages.setCurrentWidget(self.editor_page)
        self.editor.setFocus()

    def open_document(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Dokument öffnen", str(Path.home()), "Textdateien (*.txt);;Alle Dateien (*)"
        )
        if not filename:
            return
        path = Path(filename)
        try:
            self.editor.setPlainText(path.read_text(encoding="utf-8"))
            self.current_file = path
            self.document_title = path.stem
            self.title_edit.setText(self.document_title)
            self.pages.setCurrentWidget(self.editor_page)
            self.editor.setFocus()
        except Exception as exc:
            QMessageBox.critical(self, "Fehler beim Öffnen", f"Die Datei konnte nicht geöffnet werden.\n\n{exc}")

    def save_document(self):
        if self.current_file is None:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Dokument speichern", str(Path.home() / f"{self.document_title}.txt"), "Textdateien (*.txt);;Alle Dateien (*)"
            )
            if not filename:
                return
            self.current_file = Path(filename)
        try:
            self.current_file.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.document_title = self.current_file.stem
            self.title_edit.setText(self.document_title)
            QMessageBox.information(self, "Gespeichert", "Das Dokument wurde erfolgreich gespeichert.")
        except Exception as exc:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(exc))

    def rename_document(self):
        from PySide6.QtWidgets import QInputDialog
        value, ok = QInputDialog.getText(self, "Dokumentname", "Neuer Name:", text=self.document_title)
        if ok and value.strip():
            self.document_title = value.strip()
            self.title_edit.setText(self.document_title)

    def use_template(self, name):
        texts = {
            "Geschäftsbrief": "Sehr geehrte Damen und Herren,\n\nhiermit möchte ich mich mit folgendem Anliegen an Sie wenden:\n\n",
            "Beschwerde": "Sehr geehrte Damen und Herren,\n\nhiermit möchte ich mich über folgenden Sachverhalt beschweren:\n\n",
            "Anfrage": "Sehr geehrte Damen und Herren,\n\nich möchte gerne folgende Anfrage an Sie richten:\n\n",
            "Kündigung": "Sehr geehrte Damen und Herren,\n\nhiermit kündige ich den bestehenden Vertrag fristgerecht zum nächstmöglichen Zeitpunkt.\n\n",
            "E-Mail": "Betreff: \n\nSehr geehrte Damen und Herren,\n\n",
        }
        self.new_document()
        self.document_title = name
        self.title_edit.setText(name)
        self.editor.setPlainText(texts.get(name, ""))
        self.editor.setFocus()

    def ai_placeholder(self, action):
        QMessageBox.information(self, "KI-Assistent", f"„{action}“ wird in einem späteren Modul mit einer echten KI-Funktion verbunden.")

    def settings_placeholder(self, item):
        QMessageBox.information(self, "Einstellungen", f"Der Bereich „{item}“ wird als eigenes Einstellungsmodul ausgebaut.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
