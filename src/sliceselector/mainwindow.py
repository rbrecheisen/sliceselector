import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QComboBox,
    QLabel,
    QCheckBox,
    QMessageBox,
    QLineEdit,
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

ROOT_DIRECTORY = 'M:\\data\\emmymaas\\13-03-2026\\original'


class MainWindow(QMainWindow):
    def __init__(self, bundle_identifier, app_name, app_title, app_icon, app_version):
        super(MainWindow, self).__init__()
        self._settings = Settings(bundle_identifier=bundle_identifier, app_name=app_name)
        self._app_title = app_title
        self._app_icon = app_icon
        self._app_version = app_version
        self._root_dir_line_edit = QLineEdit(
            placeholderText='Choose root directory...', text=self._settings.get('mainwindow/root_dir', ''))
        self._root_dir_select_button = QPushButton('Select...')
        self._root_dir_select_button.clicked.connect(self.handle_root_dir_select_button)
        self._output_dir_line_edit = QLineEdit(
            placeholderText='Choose output directory...', text=self._settings.get('mainwindow/output_dir', ''))
        self._output_dir_select_button = QPushButton('Select...')
        self._output_dir_select_button.clicked.connect(self.handle_output_dir_select_button)
        self._vertebra_combobox = QComboBox(self)
        self._vertebra_combobox.addItems(['L3', 'T4'])
        self._resume_checkbox = QCheckBox('Resume', self)
        self._resume_checkbox.setChecked(True)
        self._button = QPushButton('Run process')
        self._button.clicked.connect(self.handle_button)
        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.handle_cancel_button)
        self._progress_bar = QProgressBar(self, minimum=0, maximum=100, value=0)
        self._process = None
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
        root_dir_layout = QHBoxLayout()
        root_dir_layout.addWidget(self._root_dir_line_edit)
        root_dir_layout.addWidget(self._root_dir_select_button)
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self._output_dir_line_edit)
        output_dir_layout.addWidget(self._output_dir_select_button)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)        
        layout.addLayout(root_dir_layout)
        layout.addLayout(output_dir_layout)
        layout.addWidget(QLabel('Select vertebra'))
        layout.addWidget(self._vertebra_combobox)
        layout.addWidget(self._resume_checkbox)
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
    
    def handle_root_dir_select_button(self):
        dir_path = QFileDialog.getExistingDirectory(self, dir=self._settings.get('last_directory', ''))
        if dir_path:
            self._root_dir_line_edit.setText(dir_path)
            self._settings.set('mainwindow/root_dir', dir_path)
            self._settings.set('last_directory', dir_path)

    def handle_output_dir_select_button(self):
        dir_path = QFileDialog.getExistingDirectory(self, dir=self._settings.get('last_directory', ''))
        if dir_path:
            self._output_dir_line_edit.setText(dir_path)
            self._settings.set('mainwindow/output_dir', dir_path)
            self._settings.set('last_directory', dir_path)
    
    def handle_button(self):
        root_dir = self._root_dir_line_edit.text()
        if root_dir != '':
            if os.path.isdir(root_dir):
                output_dir = self._output_dir_line_edit.text()
                if output_dir != '':
                    if not os.path.isdir(output_dir):
                        os.makedirs(output_dir, exist_ok=True)
                    self._progress_bar.setValue(0)
                    self._process = SliceSelectProcess(
                        inputs={'root_directory': root_dir}, 
                        output=output_dir, 
                        vertebra=self._vertebra_combobox.currentText(),
                        resume=self._resume_checkbox.isChecked(),
                    )
                    self._process.progress.connect(self.handle_progress)
                    self._process.canceled.connect(self.handle_canceled)
                    self._process.failed.connect(self.handle_failed)
                    self._process.finished.connect(self.handle_finished)
                    self._process_runner.start(self._process)
                    self._button.setEnabled(False)
                else:
                    QMessageBox.warning(self, 'Warning', 'Output directory empty')
            else:
                QMessageBox.warning(self, 'Warning', 'Root directory does not exist')
        else:
            QMessageBox.warning(self, 'Warning', 'Root directory empty')

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

    def handle_canceled(self):
        print(f'find canceled')
        self._button.setEnabled(True)

    def handle_failed(self, e):
        print(f'find failed: {e}')
        self._button.setEnabled(True)

    def handle_finished(self, output):
        self._progress_bar.setValue(100)
        print(output)
        self._button.setEnabled(True)

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
        self._settings.set('mainwindow/root_dir', self._root_dir_line_edit.text())
        self._settings.set('mainwindow/output_dir', self._output_dir_line_edit.text())

    def set_default_size_and_position(self):
        self.resize(1024, 1024)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))