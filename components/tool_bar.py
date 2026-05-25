from PyQt6.QtWidgets import QToolBar, QLabel, QLineEdit
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QFont


class ToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setMovable(False)

        self.setStyleSheet("""       
            QToolBar {
                border: none;
                background-color: #22282a;
                padding: 3px;
            }

            QToolButton {
                color: #fff;
                width: 21px;
                height: 21px;
            }

            QLabel,
            QLineEdit,
            QToolButton:hover{
                background-color: #363b3f;
            }

            QLabel {
                padding-left: 5px;
                padding-right: 5px;
                margin-left: 5px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }

            QLineEdit {
                padding-top: 2px;
                padding-right: 10px;
                padding-bottom: 2px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                color: #fff;
            }
        """)

        self.setIconSize(QSize(14, 14))

        button_back = self.addAction("Back")
        button_back.setIcon(QIcon("assets/icons/arrow-left.svg"))
        button_back.setToolTip("Back")
        button_back.triggered.connect(self.parent.main.back)

        button_forward = self.addAction("Forward")
        button_forward.setIcon(QIcon("assets/icons/arrow-right.svg"))
        button_forward.setToolTip("Forward")
        button_forward.triggered.connect(self.parent.main.forward)

        button_refresh = self.addAction("Refresh")
        button_refresh.setIcon(QIcon("assets/icons/refresh.svg"))
        button_refresh.setToolTip("Refresh")
        button_refresh.triggered.connect(self.parent.main.reload)

        label = QLabel()
        label.setPixmap(QIcon("assets/icons/search.svg").pixmap(QSize(12, 12)))
        self.addWidget(label)

        self.url_edit = QLineEdit()
        self.url_edit.returnPressed.connect(lambda: self.parent.main.navigate(self.url_edit.text()))
        self.url_edit.setPlaceholderText("Search or enter address")
        self.url_edit.setFont(QFont("Poppins", 11))
        self.addWidget(self.url_edit)

        # Bookmark Button
        self.button_bookmark = self.addAction("☆")
        self.button_bookmark.setToolTip("Bookmark this page")
        self.button_bookmark.triggered.connect(self.toggle_bookmark)

        # Menu Button
        self.button_menu = self.addAction("☰")
        self.button_menu.setToolTip("History & Bookmarks")
        self.button_menu.triggered.connect(self.show_menu)

        # Progress Bar
        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(80)
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        self.addWidget(self.progress_bar)

    def toggle_bookmark(self):
        import components.data_manager as dm
        url = self.parent.main.currentWidget().url().toString()
        title = self.parent.main.tabText(self.parent.main.currentIndex())
        if url == self.parent.main.homepage_url.toString() or not url:
            return
        if dm.is_bookmarked(url):
            dm.remove_bookmark(url)
            self.button_bookmark.setText("☆")
        else:
            dm.add_bookmark(url, title)
            self.button_bookmark.setText("⭐")

    def update_bookmark_icon(self):
        import components.data_manager as dm
        url = self.parent.main.currentWidget().url().toString()
        if dm.is_bookmarked(url):
            self.button_bookmark.setText("⭐")
        else:
            self.button_bookmark.setText("☆")

    def show_menu(self):
        from PyQt6.QtWidgets import QMenu
        import components.data_manager as dm
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #282a36; color: #fff; border: 1px solid #363b3f; } QMenu::item:selected { background-color: #363b3f; }")
        
        bookmarks_menu = menu.addMenu("Bookmarks")
        bookmarks = dm.get_bookmarks()
        if not bookmarks:
            bookmarks_menu.addAction("No bookmarks").setEnabled(False)
        else:
            for b in bookmarks:
                action = bookmarks_menu.addAction(b["title"][:50] + ("..." if len(b["title"])>50 else ""))
                action.triggered.connect(lambda checked, u=b["url"]: self.parent.main.navigate(u))
            
        history_menu = menu.addMenu("History")
        history = dm.get_history()
        if not history:
            history_menu.addAction("No history").setEnabled(False)
        else:
            for h in reversed(history[-15:]):
                title = h["title"][:40] + ("..." if len(h["title"])>40 else "")
                action = history_menu.addAction(f'{title} ({h["time"][11:16]})')
                action.triggered.connect(lambda checked, u=h["url"]: self.parent.main.navigate(u))
        
        menu.addSeparator()
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings)
            
        widget = self.widgetForAction(self.button_menu)
        menu.exec(widget.mapToGlobal(widget.rect().bottomLeft()))

    def open_settings(self):
        from components.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
