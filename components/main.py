from PyQt6.QtWidgets import QTabWidget, QPushButton
from PyQt6.QtCore import QUrl, QSize, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
import validators
import os
import time

class Main(QTabWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.homepage_url = QUrl.fromLocalFile(os.path.abspath("homepage/index.html"))

        self.setStyleSheet("""
            QPushButton,
            QTabBar::tab{
                color: #fff;
            }
        
            QPushButton {
                background-color: transparent;
                border: none;
            }
            
            QTabWidget::pane {  
                border: none;
            }

            QPushButton:hover,
            QTabBar::tab,
            QTabBar{
                background-color: #363b3f;
            }

            QTabBar::tab:selected {
                background-color: #22282a;
            }
            
            QTabBar::close-button {
                image: url(assets/icons/close.svg);
                padding: 3px;
                margin-bottom: 1px;
           }
            
            QTabBar QToolButton,
            QTabBar QToolButton:selected {
                background-color: transparent;
                color: #fff;
            }
        """)

        self.setFont(QFont("Poppins", 10))

        self.tab_last_active = {}
        self.sleep_timer = QTimer(self)
        self.sleep_timer.timeout.connect(self.check_sleeping_tabs)
        self.sleep_timer.start(60000)

        self.add_tab_button = QPushButton("+", clicked=self.open_tab)
        self.add_tab_button.setFixedSize(QSize(25, 24))
        self.add_tab_button.setFont(QFont("Poppins", 12))

        self.add_tab_button.setParent(self)

        self.tabBarClicked.connect(self.select_tab)
        self.tabCloseRequested.connect(self.close_tab)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)

        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setHttpCacheMaximumSize(500 * 1024 * 1024)

        from components.adblocker import AdBlockInterceptor
        self.adblock_interceptor = AdBlockInterceptor(self)
        profile.setUrlRequestInterceptor(self.adblock_interceptor)

        settings = profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

        profile.downloadRequested.connect(self.handle_download)

    def handle_download(self, download):
        import os
        from PyQt6.QtWidgets import QFileDialog, QProgressDialog
        from PyQt6.QtCore import Qt
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
        
        default_path = download.downloadDirectory() + "/" + download.downloadFileName()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        
        if path:
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            
            progress = QProgressDialog(f"Downloading {download.downloadFileName()}...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Download Progress")
            progress.setWindowModality(Qt.WindowModality.NonModal)
            progress.setAutoClose(True)
            progress.show()
            
            def update_progress(bytes_received, bytes_total):
                if bytes_total > 0:
                    percent = int((bytes_received / bytes_total) * 100)
                    progress.setValue(percent)
                    
            download.receivedBytesChanged.connect(update_progress)
            
            def check_state(state):
                if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                    progress.setValue(100)
                elif state in (QWebEngineDownloadRequest.DownloadState.DownloadCancelled, QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
                    progress.cancel()
                    
            download.stateChanged.connect(check_state)
            progress.canceled.connect(download.cancel)
            
            download.accept()

    def change_url(self):
        url = self.currentWidget().url().toString()
        self.parent.tool_bar.url_edit.setText("" if url == self.homepage_url.toString() else url)
        if hasattr(self.parent, 'tool_bar') and hasattr(self.parent.tool_bar, 'update_bookmark_icon'):
            self.parent.tool_bar.update_bookmark_icon()

    def change_title(self, tab, title):
        self.setTabText(self.indexOf(tab), title)
        self.move_add_tab_button()
        
        import components.data_manager as dm
        url = tab.url().toString()
        if url != self.homepage_url.toString():
            dm.add_to_history(url, title)

    def change_icon(self, tab, icon):
        self.setTabIcon(self.indexOf(tab), icon)
        self.move_add_tab_button()

    def resizeEvent(self, event):
        self.move_add_tab_button()

    def move_add_tab_button(self):
        tap_bar = self.tabBar()
        tap_bar.setFixedWidth(0)

        tabs_width = 0

        for i in range(tap_bar.count()):
            tabs_width += tap_bar.tabRect(i).width()

        tap_bar.setFixedWidth(tabs_width)

        tab_bar_width = tap_bar.width()

        self.add_tab_button.move(tab_bar_width, 0)

        width = self.width()
        button_width = self.add_tab_button.width()
        difference = width - button_width

        if self.add_tab_button.x() > difference:
            tap_bar.setFixedWidth(difference)
            self.add_tab_button.move(width - self.add_tab_button.width(), 0)

    def select_tab(self, index):
        self.setCurrentIndex(index)
        self.change_url()

        tab = self.widget(index)
        if tab:
            self.tab_last_active[tab] = time.time()
            if tab.page().lifecycleState() == QWebEnginePage.LifecycleState.Discarded:
                tab.page().setLifecycleState(QWebEnginePage.LifecycleState.Active)

    def close_tab(self, index):
        if self.count() > 1:
            tab = self.widget(index)
            if tab in self.tab_last_active:
                del self.tab_last_active[tab]
            self.removeTab(index)
            self.move_add_tab_button()
        else:
            self.parent.close()

    def open_tab(self):
        self.add_tab()
        self.move_add_tab_button()

    def add_tab(self, url=None):
        tab = QWebEngineView()

        if url:
            tab.setUrl(QUrl(url))
        else:
            tab.setUrl(self.homepage_url)

        tab.urlChanged.connect(self.change_url)
        tab.titleChanged.connect(lambda title: self.change_title(tab, title))
        tab.iconChanged.connect(lambda icon: self.change_icon(tab, icon))
        
        tab.loadStarted.connect(lambda: self.handle_load_started(tab))
        tab.loadProgress.connect(lambda p: self.handle_load_progress(tab, p))
        tab.loadFinished.connect(lambda ok: self.handle_load_finished(tab))

        self.addTab(tab, "New Tab")
        self.setCurrentWidget(tab)

        self.tab_last_active[tab] = time.time()
        self.change_url()

    def handle_load_started(self, tab):
        if self.currentWidget() == tab and hasattr(self.parent, 'tool_bar'):
            self.parent.tool_bar.progress_bar.show()

    def handle_load_progress(self, tab, progress):
        if self.currentWidget() == tab and hasattr(self.parent, 'tool_bar'):
            self.parent.tool_bar.progress_bar.setValue(progress)

    def handle_load_finished(self, tab):
        if self.currentWidget() == tab and hasattr(self.parent, 'tool_bar'):
            self.parent.tool_bar.progress_bar.hide()
    
        if tab.url().toString() == self.homepage_url.toString():
            import components.data_manager as dm
            settings = dm.get_settings()
            engine = settings.get("search_engine", "DuckDuckGo")
            tab.page().runJavaScript(f"window.defaultSearchEngine = '{engine}';")

    def back(self):
        self.currentWidget().back()

    def forward(self):
        self.currentWidget().forward()

    def reload(self):
        self.currentWidget().reload()

    def navigate(self, url):
        browser = self.currentWidget()

        if os.path.exists(url):
            browser.setUrl(QUrl.fromLocalFile(url))
            return

        if validators.url(url):
            normalized_url = url
        elif validators.domain(url):
            normalized_url = f"http://{url}"
        else:
            import components.data_manager as dm
            settings = dm.get_settings()
            engine = settings.get("search_engine", "DuckDuckGo")
            
            if engine == "Google":
                normalized_url = f"https://www.google.com/search?q={url}"
            elif engine == "Bing":
                normalized_url = f"https://www.bing.com/search?q={url}"
            elif engine == "Yahoo":
                normalized_url = f"https://search.yahoo.com/search?p={url}"
            else:
                normalized_url = f"https://duckduckgo.com/?q={url}"

        browser.setUrl(QUrl(normalized_url))

    def check_sleeping_tabs(self):
        current_time = time.time()
        current_tab = self.currentWidget()
        
        for i in range(self.count()):
            tab = self.widget(i)
            if tab != current_tab and tab in self.tab_last_active:
                if current_time - self.tab_last_active[tab] > 300:
                    if tab.page().lifecycleState() == QWebEnginePage.LifecycleState.Active:
                        tab.page().setLifecycleState(QWebEnginePage.LifecycleState.Discarded)
