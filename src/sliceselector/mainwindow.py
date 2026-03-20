import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QProgressBar,
)
from PySide6.QtGui import (
    QGuiApplication,
    QAction,
)
from PySide6.QtCore import Qt, QByteArray
from sliceselector.settings import Settings
from sliceselector.processes.processrunner import ProcessRunner
from sliceselector.processes.sliceselect.sliceselectprocess import SliceSelectProcess

ROOT_DIRECTORY = 'M:\\data\\emmymaas\\original'


class MainWindow(QMainWindow):
    def __init__(self, bundle_identifier, app_name, app_title, app_icon, app_version):
        super(MainWindow, self).__init__()
        self._settings = Settings(bundle_identifier=bundle_identifier, app_name=app_name)
        self._app_title = app_title
        self._app_icon = app_icon
        self._app_version = app_version
        self._button = QPushButton('Run process')
        self._button.clicked.connect(self.handle_button)
        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.handle_cancel_button)
        self._progress_bar = QProgressBar(self, minimum=0, maximum=100, value=0)
        self._process = SliceSelectProcess(inputs={'root_directory': ROOT_DIRECTORY}, output=None)
        self._process.progress.connect(self.handle_progress)
        self._process.canceled.connect(self.handle_canceled)
        self._process.failed.connect(self.handle_failed)
        self._process.finished.connect(self.handle_finished)
        self._process_runner = ProcessRunner()
        self.init()

    # INITIALIZATION

    def init(self):
        self.setWindowTitle(f'{self._app_title} ({self._app_version})')
        self.setWindowIcon(self._app_icon)
        if not self.load_geometry_and_state():
            self.set_default_size_and_position()
        self.init_menus()
        self.init_layout()

    def init_menus(self):
        self.init_app_menu()

    def init_app_menu(self):
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        app_menu = self.menuBar().addMenu('Application')
        app_menu.addAction(exit_action)

    def init_layout(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._button)
        layout.addWidget(self._cancel_button)
        layout.addWidget(self._progress_bar)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # EVENTS

    def closeEvent(self, event):
        self.save_geometry_and_state()
        return super().closeEvent(event)
    
    def handle_button(self):
        self._progress_bar.setValue(0)
        self._process_runner.start(self._process)

    def handle_cancel_button(self):
        self._process_runner.cancel()

    # PROCESS EVENTS

    def handle_find_start(self):
        self._progress_bar.setValue(0)

    def handle_progress(self, step, nr_steps):
        progress = int(float(step+1) / nr_steps * 100.0)
        self._progress_bar.setValue(progress)
        if progress > 100:
            self._progress_bar.setValue(100)
        print('.', sep='', end='', flush=True)

    def handle_canceled(self):
        print(f'find canceled')

    def handle_failed(self, e):
        print(f'find failed: {e}')

    def handle_finished(self, output):
        self._progress_bar.setValue(100)
        print(output)

    # HELPERS

    def load_geometry_and_state(self):
        geometry = self._settings.get('mainwindow/geometry')
        state = self._settings.get('mainwindow/state')
        if isinstance(geometry, QByteArray) and self.restoreGeometry(geometry):
            if isinstance(state, QByteArray):
                self.restoreState(state)
            return True
        return False
    
    def save_geometry_and_state(self):
        self._settings.set('mainwindow/geometry', self.saveGeometry())
        self._settings.set('mainwindow/state', self.saveState())

    def set_default_size_and_position(self):
        self.resize(1024, 1024)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))