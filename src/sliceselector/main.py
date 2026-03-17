import sys
from PySide6 import QtWidgets
from sliceselector.mainwindow import MainWindow


def main():
    app_name = 'sliceselector'
    QtWidgets.QApplication.setApplicationName(app_name)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(
        bundle_identifier='nl.rbeesoft',
        app_name=app_name,
        app_title='Slice Selector',
        app_icon=app.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward),
        app_version='1.0.0',
    )
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()