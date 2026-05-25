from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QIcon, QShortcut, QKeySequence
from components.tool_bar import ToolBar
from components.main import Main
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setWindowIcon(QIcon("assets/brand/logo-medium.svg"))

        self.setMinimumSize(350, 480)

        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #282a36;
                color: #fff;
                border: none;
            }
        """)

        self.main = Main(self)

        self.tool_bar = ToolBar(self)
        self.addToolBar(self.tool_bar)

        self.setCentralWidget(self.main)

        self.main.add_tab()

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.main.open_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.main.close_tab(self.main.currentIndex()))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.main.reload)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.focus_url)

    def focus_url(self):
        self.tool_bar.url_edit.setFocus()
        self.tool_bar.url_edit.selectAll()


app = QApplication(sys.argv)
QFontDatabase.addApplicationFont("assets/fonts/poppins/poppins-v19-latin-500.ttf")
QFontDatabase.addApplicationFont("assets/fonts/poppins/poppins-v19-latin-600.ttf")
QFontDatabase.addApplicationFont("assets/fonts/poppins/poppins-v19-latin-700.ttf")
QFontDatabase.addApplicationFont("assets/fonts/poppins/poppins-v19-latin-regular.ttf")
window = MainWindow()
window.show()

sys.exit(app.exec())
