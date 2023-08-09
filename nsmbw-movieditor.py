from PyQt6 import QtGui, QtWidgets
import sys
import struct
from wii import archive
import operator
import os

# Made with CLF78's moviedata.bin/moviesound.bin Documentation
# Thanks to L-Dev for doing the logo
# Thanks to the Reggie (Next) staff for the U8 Archive API

version = "1.0"

aboutMsg = "NSMBW Movieditor v" + version + "\nCoded by LiQ - MIT License"
warningMsg = "This file includes both moviedata and moviesound Commands.\nMake sure to fix your file!"

effects = [
    "Wm_dm_landsmoke",
    "Wm_dm_cream01",
    "Wm_dm_cream02",
    "Wm_dm_bosslandsmoke",
    "Wm_dm_mrlandsmoke",
    "Wm_dm_fireworks",
    "Wm_dm_cannonsmoke01",
    "Wm_dm_cannonsmoke02",
    "Wm_dm_castlelandsmoke",
    "Wm_dm_presentopen",
    "Wm_dm_itemsmoke",
    "Wm_dm_gondolasmoke",
    "Wm_dm_koopasmoke",
    "Wm_dm_koopaturnover",
    "Wm_dm_mortonlandsmoke",
    "Wm_dm_ludwiglandsmoke",
    "Wm_dm_wndylandsmoke",
    "Wm_dm_larylandsmoke",
    "Wm_dm_castlebreak",
    "Wm_dm_falldust",
    "Wm_dm_downlandsmoke01",
    "Wm_dm_downlandsmoke02"
]


def assembleListString(type, correspondingData=0, correspondingData2=0, correspondingData3=0):
    """
    Get string for list entry name
    """
    final = ""
    match type:
        case 0:
            final = "Switch to Scene %d" % correspondingData
        case 1:
            final = "Move Camera to (%d, %d, %d)" % (correspondingData, correspondingData2, correspondingData3)
        case 2:
            final = "Play Sound %d" % correspondingData
        case 3:
            final = "Spawn Effect \"%s\"" % effects[correspondingData]
        case 4:
            final = "End Cutscene"
        case 5:
            final = "Shake Screen (Type %d)" % correspondingData

    return final


def throwBinError(binName):
    """
    Bin is not in the arc
    """
    error = QtWidgets.QMessageBox()
    error.setText("File \"%s\" was not found in the archive!" % binName)
    error.setWindowTitle("Error while opening!")
    error.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
    error.exec()


def checkFileFunctionality(listW):
    """
    Do we really seperate moviedata and moviedemo cmds?
    """
    commandThree = False
    commandNotThree = False
    for i in range(listW.count()):
        currentEntry = listW.item(i)
        if currentEntry.cmdType == 2:
            commandThree = True
        else:
            commandNotThree = True
    if commandThree and commandNotThree:
        warning = QtWidgets.QMessageBox()
        warning.setText(warningMsg)
        warning.setWindowTitle("Warning")
        warning.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        warning.exec()


def getLast4CharsOfStr(string):
    """
    To see if its '.bin'
    (Might be a bad way tho)
    """
    return operator.getitem(string, slice(len(string) - 4, len(string)))

2
class AddRemButtons(QtWidgets.QWidget):
    def __init__(self, otherWidget):
        super().__init__()

        self.addButton = QtWidgets.QPushButton()
        self.removeButton = QtWidgets.QPushButton()

        self.addButton.setText("Add Command")
        self.removeButton.setText("Remove Command")
        self.addButton.setFixedWidth(130)
        self.removeButton.setFixedWidth(130)
        self.addButton.clicked.connect(otherWidget.addCmd)
        self.removeButton.clicked.connect(otherWidget.removeCmd)
        self.addButton.setEnabled(False)
        self.removeButton.setEnabled(False)

        layout = QtWidgets.QFormLayout()

        layout.addRow(self.addButton, self.removeButton)

        self.setLayout(layout)


class CommandStruct(QtWidgets.QListWidgetItem):
    def __init__(self):
        QtWidgets.QListWidgetItem.__init__(self)

        self.frame = 0
        self.cmdType = 0

        self.field0 = 0
        self.field1 = 0
        self.field2 = 0
        self.field3 = 0
        self.field4 = 0
        self.field5 = 0
        self.field6 = 0


class Widgets(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.openProcess = False

        # widgets
        self.listField = QtWidgets.QListWidget()
        self.sceneType = QtWidgets.QComboBox()
        self.frame = QtWidgets.QSpinBox()

        self.fields = []
        for i in range(7):
            self.fields.append(QtWidgets.QSpinBox())

        self.fieldLabels = []
        for i in range(7):
            self.fieldLabels.append(QtWidgets.QLabel())

        # settings
        self.listField.setFixedHeight(250)
        self.listField.itemSelectionChanged.connect(self.selectionChanged)
        self.listField.setDragEnabled(True)
        self.listField.setAcceptDrops(True)
        self.listField.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.listField.setFixedSize(300, 300)

        self.buttons = AddRemButtons(self)

        self.sceneType.addItem("Switch Scene")
        self.sceneType.addItem("Move Camera")
        self.sceneType.addItem("Play Sound")
        self.sceneType.addItem("Spawn Effect")
        self.sceneType.addItem("End Cutscene")
        self.sceneType.addItem("Shake Screen")
        self.sceneType.currentIndexChanged.connect(self.changeCmdTypeValue)

        self.frame.setMinimum(0)
        self.frame.setMaximum(2147483647)
        self.frame.valueChanged.connect(self.updateValues)

        for i in range(7):
            self.fields[i].setRange(-2147483648, 2147483647)
            self.fields[i].valueChanged.connect(self.updateValues)

        # init layout
        layout = QtWidgets.QGridLayout()

        # add rows
        layout.addWidget(self.listField, 0, 0, 10, 1)
        layout.addWidget(self.buttons, 15, 0, 10, 1)
        layout.addWidget(QtWidgets.QLabel("Command Type:"), 0, 1)
        layout.addWidget(self.sceneType, 0, 2)
        layout.addWidget(QtWidgets.QLabel("Execution Frame:"), 1, 1)
        layout.addWidget(self.frame, 1, 2)
        for i in range(7):
            layout.addWidget(self.fieldLabels[i], 2 + i, 1)
            layout.addWidget(self.fields[i], 2 + i, 2)
            self.fieldLabels[i].setVisible(False)
            self.fields[i].setVisible(False)

        # set the layout
        self.setLayout(layout)

    def addCmd(self):
        """
        Add command to list
        """
        newCmd = CommandStruct()
        newCmd.setText("Switch to Scene 0")
        self.listField.addItem(newCmd)

    def removeCmd(self):
        """
        Remove command from list
        """
        selected = self.listField.selectedIndexes()[0]
        self.listField.takeItem(selected.row())
        if self.listField.count() == 0:
            self.buttons.removeButton.setEnabled(False)

    def updateValues(self):
        """
        Updates the values
        """
        if self.openProcess:
            return
        try:
            currentItem = self.listField.currentItem()
            currentItem.frame = self.frame.value()
            match currentItem.cmdType:
                case 0:
                    currentItem.field0 = self.fields[0].value()
                case 1:
                    currentItem.field0 = self.fields[0].value()
                    currentItem.field1 = self.fields[1].value()
                    currentItem.field2 = self.fields[2].value()
                    currentItem.field3 = self.fields[3].value()
                    currentItem.field4 = self.fields[4].value()
                    currentItem.field5 = self.fields[5].value()
                    currentItem.field6 = self.fields[6].value()
                case 2:
                    currentItem.field0 = self.fields[0].value()
                case 3:
                    currentItem.field0 = self.fields[0].value()
                    currentItem.field1 = self.fields[1].value()
                    currentItem.field2 = self.fields[2].value()
                    currentItem.field3 = self.fields[3].value()
                case 4:
                    pass
                case 5:
                    currentItem.field0 = self.fields[0].value()
            self.listField.currentItem().setText(assembleListString(self.sceneType.currentIndex(),
                                                                    currentItem.field0,
                                                                    currentItem.field1,
                                                                    currentItem.field2))
        except:
            return
        finally:
            return

    def selectionChanged(self):
        """
        Load correct datas into the fields
        """
        self.openProcess = True
        try:
            if not self.buttons.removeButton.isEnabled():
                self.buttons.removeButton.setEnabled(True)

            currentItem = self.listField.currentItem()
            self.sceneType.setCurrentIndex(currentItem.cmdType)
            self.frame.setValue(currentItem.frame)

            self.listField.currentItem().setText(assembleListString(self.sceneType.currentIndex(),
                                                                    currentItem.field0,
                                                                    currentItem.field1,
                                                                    currentItem.field2))

            match currentItem.cmdType:
                case 0:
                    self.fields[0].setValue(currentItem.field0)
                case 1:
                    self.fields[0].setValue(currentItem.field0)
                    self.fields[1].setValue(currentItem.field1)
                    self.fields[2].setValue(currentItem.field2)
                    self.fields[3].setValue(currentItem.field3)
                    self.fields[4].setValue(currentItem.field4)
                    self.fields[5].setValue(currentItem.field5)
                    self.fields[6].setValue(currentItem.field6)
                case 2:
                    self.fields[0].setValue(currentItem.field0)
                case 3:
                    self.fields[0].setValue(currentItem.field0)
                    self.fields[1].setValue(currentItem.field1)
                    self.fields[2].setValue(currentItem.field2)
                    self.fields[3].setValue(currentItem.field3)
                case 4:
                    pass
                case 5:
                    self.fields[0].setValue(currentItem.field0)
            self.changeCmdType()
        except:
            self.openProcess = False
            return
        finally:
            self.openProcess = False
            return

    def changeCmdTypeValue(self):
        try:
            currentItem = self.listField.currentItem()
            currentItem.cmdType = self.sceneType.currentIndex()
            self.listField.currentItem().setText(assembleListString(self.sceneType.currentIndex(),
                                                                    currentItem.field0,
                                                                    currentItem.field1,
                                                                    currentItem.field2))
            self.changeCmdType()
        except:
            return
        finally:
            return

    def changeCmdType(self):
        try:
            for i in range(7):
                self.fieldLabels[i].setVisible(False)
                self.fields[i].setVisible(False)
            currentItem = self.listField.currentItem()
            match currentItem.cmdType:
                case 0:
                    self.fieldLabels[0].setText("Scene ID")
                    self.fields[0].setVisible(True)
                    self.fieldLabels[0].setVisible(True)
                case 1:
                    self.fieldLabels[0].setText("Starting X")
                    self.fieldLabels[1].setText("Starting Y")
                    self.fieldLabels[2].setText("Starting Z")
                    self.fieldLabels[3].setText("Ending X")
                    self.fieldLabels[4].setText("Ending Y")
                    self.fieldLabels[5].setText("Ending Z")
                    self.fieldLabels[6].setText("Movement Duration")
                    for i in range(7):
                        self.fields[i].setVisible(True)
                        self.fieldLabels[i].setVisible(True)
                case 2:
                    self.fieldLabels[0].setText("Sound ID")
                    self.fields[0].setVisible(True)
                    self.fieldLabels[0].setVisible(True)
                case 3:
                    self.fieldLabels[0].setText("Effect ID")
                    self.fieldLabels[1].setText("Position X")
                    self.fieldLabels[2].setText("Position Y")
                    self.fieldLabels[3].setText("Position Z")
                    for i in range(4):
                        self.fields[i].setVisible(True)
                        self.fieldLabels[i].setVisible(True)
                case 4:
                    pass
                case 5:
                    self.fieldLabels[0].setText("Shake Type")
                    self.fields[0].setVisible(True)
                    self.fieldLabels[0].setVisible(True)
        except:
            return
        finally:
            return


class MainForm(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # basic things
        self.setWindowTitle("NSMBW Movieditor")
        self.setWindowIcon(QtGui.QIcon("icon.ico"))
        self.setFixedSize(600, 440)

        self.createMenuStrip()

        self.widget = Widgets()
        self.setCentralWidget(self.widget)

        self.msg = None
        self.path = ""

        self.folderName = ""
        self.bins = []
        self.binNames = []
        self.targetBinName = ""

        self.show()

    def createMenuStrip(self):
        menub = self.menuBar()

        menub.setNativeMenuBar(False)

        # File Menu
        file = menub.addMenu("&File")

        # newfile = file.addAction("New")
        # newfile.setShortcut("Ctrl+N")
        # newfile.triggered.connect(self.newFile)

        open = file.addAction("Open...")
        open.setShortcut("Ctrl+O")
        open.triggered.connect(self.openFile)

        self.save = file.addAction("Save")
        self.save.setShortcut("Ctrl+S")
        self.save.triggered.connect(self.saveFile)
        self.save.setEnabled(False)

        self.saveAs = file.addAction("Save As...")
        self.saveAs.setShortcut("Ctrl+Shift+S")
        self.saveAs.triggered.connect(self.saveFileAs)
        self.saveAs.setEnabled(False)

        # Help Menu
        help = menub.addMenu("&Info")
        about = help.addAction("About")
        about.triggered.connect(self.aboutPressed)

    def aboutPressed(self):
        msg = QtWidgets.QMessageBox()
        msg.setText(aboutMsg)
        msg.setWindowTitle("About")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    def newFile(self):
        self.widget.listField.clear()
        self.save.setEnabled(False)

    def saveFileAs(self):
        """
        Save the file, but not in the same place
        """
        fresult = QtWidgets.QFileDialog.getSaveFileName(self, "Save Moviedata", "", "Moviedata Archive (*.arc)")

        if fresult[0] == "":
            return

        self.path = fresult[0]

        self.save.setEnabled(True)

        self.saveFile()

    def saveFile(self):
        """
        Save the file
        """
        newArchive = archive.U8()

        newArchive[self.folderName] = None

        for i in range(len(self.binNames)):
            newArchive[self.binNames[i]] = self.bins[i]

        finalDatas = struct.pack('>i', 0)
        data = None
        for i in range(self.widget.listField.count()):
            cmd = self.widget.listField.item(i)
            cmdData = []
            cmdData.append(cmd.frame)
            cmdData.append(cmd.cmdType + 1)
            match cmd.cmdType:
                case 0:
                    cmdData.append(cmd.field0)
                    for i in range(6):
                        cmdData.append(0)
                case 1:
                    cmdData.append(cmd.field0)
                    cmdData.append(cmd.field1)
                    cmdData.append(cmd.field2)
                    cmdData.append(cmd.field3)
                    cmdData.append(cmd.field4)
                    cmdData.append(cmd.field5)
                    cmdData.append(cmd.field6)
                case 2:
                    cmdData.append(cmd.field0)
                    for i in range(6):
                        cmdData.append(0)
                case 3:
                    cmdData.append(cmd.field0)
                    cmdData.append(cmd.field1)
                    cmdData.append(cmd.field2)
                    cmdData.append(cmd.field3)
                    cmdData.append(0x64)
                    for i in range(2):
                        cmdData.append(0)
                case 4:
                    for i in range(7):
                        cmdData.append(0)
                case 5:
                    cmdData.append(cmd.field0)
                    for i in range(6):
                        cmdData.append(0)
            if data is None:
                data = struct.pack('>iiiiiiiii', cmdData[0], cmdData[1], cmdData[2], cmdData[3], cmdData[4], cmdData[5],
                                   cmdData[6], cmdData[7], cmdData[8])
            else:
                data += struct.pack('>iiiiiiiii', cmdData[0], cmdData[1], cmdData[2], cmdData[3], cmdData[4],
                                    cmdData[5],
                                    cmdData[6], cmdData[7], cmdData[8])
            finalDatas += data

        while len(finalDatas) < 18004:
            finalDatas += struct.pack('>i', 0)
            data += struct.pack('>i', 0)

        newArchive[self.targetBinName] = data

        finalArc = newArchive._dump()

        f = open(self.path, 'wb')
        f.write(finalArc)
        f.close()

        checkFileFunctionality(self.widget.listField)

    def openFile(self):
        """
        Open the file
        """
        # open file dialog to get path
        result = QtWidgets.QFileDialog.getOpenFileName(self, "Open Moviedata...", "", "Moviedata Archive (*.arc)")

        # check if dialog was cancelled
        if result[0] == "":
            return

        # clear the list field and the data
        self.widget.listField.clear()

        # get only the path
        path = result[0]
        self.path = result[0]

        # Load file
        f = open(path, 'rb')
        dat = f.read()
        f.close()
        arc = archive.U8().load(dat)

        fileIndex, noNeed = QtWidgets.QInputDialog.getText(self, "BIN Name", "Enter the name of the wanted binary.")
        if getLast4CharsOfStr(fileIndex) != ".bin":
            fileIndex += ".bin"
        data = None
        for key, value in arc.files:
            if value is None:
                self.folderName = key
            elif key.endswith(fileIndex):
                data = arc[key]
                self.targetBinName = key
            else:
                self.bins.append(arc[key])
                self.binNames.append(key)

        if data is None:
            throwBinError(fileIndex)
            return

        value = []

        index = 0
        while True:
            earlyData = int.from_bytes(data[index:index + 4], "big", signed=True)
            value.append(earlyData)
            index += 4

            if len(value) == 9:
                if value[1] == 0:
                    checkFileFunctionality(self.widget.listField)
                    self.save.setEnabled(True)
                    self.saveAs.setEnabled(True)
                    self.widget.buttons.addButton.setEnabled(True)
                    return
                newCommand = CommandStruct()
                newCommand.frame = value[0]
                newCommand.cmdType = value[1] - 1
                match newCommand.cmdType:
                    case 0:
                        newCommand.field0 = value[2]
                    case 1:
                        newCommand.field0 = value[2]
                        newCommand.field1 = value[3]
                        newCommand.field2 = value[4]
                        newCommand.field3 = value[5]
                        newCommand.field4 = value[6]
                        newCommand.field5 = value[7]
                        newCommand.field6 = value[8]
                    case 2:
                        newCommand.field0 = value[2]
                    case 3:
                        newCommand.field0 = value[2]
                        newCommand.field1 = value[3]
                        newCommand.field2 = value[4]
                        newCommand.field3 = value[5]
                    case 4:
                        pass
                    case 5:
                        newCommand.field0 = value[2]
                newCommand.setText(assembleListString(newCommand.cmdType, newCommand.field0,
                                                      newCommand.field1, newCommand.field2))
                self.widget.listField.addItem(newCommand)
                value.clear()

        checkFileFunctionality(self.widget.listField)
        self.save.setEnabled(True)
        self.saveAs.setEnabled(True)
        self.widget.buttons.addButton.setEnabled(True)


app = QtWidgets.QApplication(sys.argv)

window = MainForm()

app.exec()
