from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction,
QFileDialog, QApplication, QMessageBox, qApp)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import sys

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.initUI()

    def initUI(self):

        self.statusBar()

        chooseFolder = QAction('Choose folder', self)
        chooseFolder.setShortcut('Ctrl+O')
        chooseFolder.setStatusTip('Choose the folder you want to backup')

        chooseDestination = QAction('Choose backup destination', self)
        chooseDestination.setShortcut('Ctrl+T')
        chooseDestination.setStatusTip('''Choose the folder you want to store the
        backup zip files''')

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit pybackup-GUI')
        exitAct.triggered.connect(qApp.quit)

        helpInfo = QAction('Help', self)
        helpInfo.setShortcut('Ctrl+H')
        helpInfo.setStatusTip('Help documents')

        aboutAuthor = QAction('About', self)
        aboutAuthor.setStatusTip('About author')
        aboutAuthor.triggered.connect(self.showAuthor)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        helpMenu = menuBar.addMenu('&Help')

        fileMenu.addAction(chooseFolder)
        fileMenu.addAction(chooseDestination)
        fileMenu.addAction(exitAct)
        helpMenu.addAction(helpInfo)
        helpMenu.addAction(aboutAuthor)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('pybackup-GUI')
        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
        "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showHelp(self):
        pass

    def showAuthor(self):

        QMessageBox.information(self, "About Author",
        '''pybackup-GUI: A python script to backup your files\n
        Author: rogerclark\n
        E-mail: rogerclark@163.com\n
        Fork ME!: https://github.com/rogerclarkgc/pybackup.git''')





if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
