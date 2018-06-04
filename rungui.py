from PyQt5.QtWidgets import (QMainWindow, QCheckBox, QAction, QWidget, QLabel,
QFileDialog, QApplication, QMessageBox, QLineEdit, qApp, QGridLayout, QPushButton)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import sys, os


class centralWidget(QWidget):

    def __init__(self):

        super().__init__()
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        grid.setSpacing(10)

        sourceLabel = QLabel("Source Folder:")
        destiLabel = QLabel("Destination Folder:")
        paramLabel = QLabel("Backup params:")

        self.sourceLine = QLineEdit()
        self.destLine = QLineEdit()
        #self.sourceLine.setEchoMode(2)

        self.sourceButton = QPushButton('select')
        self.sourceButton.resize(self.sourceButton.sizeHint())
        self.destiButton = QPushButton('select')
        self.destiButton.resize(self.destiButton.sizeHint())
        self.startButton = QPushButton('start backup')
        self.startButton.resize(self.startButton.sizeHint())

        self.setFullBackup = QCheckBox('full backup')
        self.setViewLog = QCheckBox('View log after backup')
        self.setFullBackup.setChecked(True)
        self.setViewLog.setChecked(False)
        self.setFullBackup.setToolTip("Select to run full backup process,\nif not select,script will run a incr-backup")
        self.setViewLog.setToolTip("Select to see the backup log after backup process is finished")

        grid.addWidget(sourceLabel, 1, 0)
        grid.addWidget(self.sourceLine, 1, 1)
        grid.addWidget(self.sourceButton, 1, 2)

        grid.addWidget(destiLabel, 2, 0)
        grid.addWidget(self.destLine, 2, 1)
        grid.addWidget(self.destiButton, 2, 2)

        grid.addWidget(paramLabel, 3, 0)
        grid.addWidget(self.setFullBackup, 3, 1)
        grid.addWidget(self.setViewLog, 3, 2)

        grid.addWidget(self.startButton, 4, 2)

        self.setLayout(grid)
        #self.setGeometry(300, 300, 500, 200)
        self.show()


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.initUI()

    def initUI(self):

        chooseFolder = QAction('Choose folder', self)
        chooseFolder.setShortcut('Ctrl+O')
        chooseFolder.setStatusTip('Choose the folder which you want to backup')
        chooseFolder.triggered.connect(self.selectSourceFolder)

        chooseDestination = QAction('Choose backup destination', self)
        chooseDestination.setShortcut('Ctrl+T')
        chooseDestination.setStatusTip('''Choose the folder which you want to store the backup zip files''')
        chooseDestination.triggered.connect(self.selectDestinationFolder)

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit pybackup-GUI')
        exitAct.triggered.connect(qApp.quit)

        viewLog = QAction('View backup log', self)
        viewLog.setShortcut('Ctrl+L')
        viewLog.setStatusTip('View the log file of back up')

        helpInfo = QAction('Help', self)
        helpInfo.setShortcut('Ctrl+H')
        helpInfo.setStatusTip('Help documents')

        aboutAuthor = QAction('About', self)
        aboutAuthor.setStatusTip('About author')
        aboutAuthor.triggered.connect(self.showAuthor)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        viewMenu = menuBar.addMenu('&View')
        helpMenu = menuBar.addMenu('&Help')

        fileMenu.addAction(chooseFolder)
        fileMenu.addAction(chooseDestination)
        fileMenu.addAction(exitAct)
        viewMenu.addAction(viewLog)
        helpMenu.addAction(helpInfo)
        helpMenu.addAction(aboutAuthor)

        self.central = centralWidget()
        self.central.sourceButton.clicked.connect(self.selectSourceFolder)
        self.central.destiButton.clicked.connect(self.selectDestinationFolder)
        self.central.startButton.clicked.connect(self.clickStartButton)
        self.statusBar()
        self.setCentralWidget(self.central)
        self.setGeometry(300, 300, 500, 300)
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

    def selectSourceFolder(self):

        path = QFileDialog.getExistingDirectory(self, "Choose source folder",
        os.getcwd())
        self.central.sourceLine.setText(path)
        print(path)
        return path

    def selectDestinationFolder(self):

        dir = QFileDialog.getExistingDirectory(self, "Choose destination folder",
        os.getcwd())
        self.central.destLine.setText(dir)
        print(dir)
        return dir

    def clickStartButton(self):

        sourceFolder = self.central.sourceLine.displayText()
        destiFolder = self.central.destLine.displayText()
        viewLogState = self.central.setViewLog.checkState()
        fullBackupState = self.central.setFullBackup.checkState()
        print(sourceFolder, destiFolder, viewLogState, fullBackupState)

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
