import numpy as np
import PyQt5
import PyQt5.QtWidgets as Widgets
from PyQt5.QtGui import QColor

class Board(Widgets.QFrame):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.shape = [1] * 2
        self.widgets = []
        self.defaultSize = [600] * 2
        self.defaultSizeMenu = [200, 320]
        self.globalOffset = np.array((0, -150))
        self.stretch = 25
        self.colors = [QColor(*c) for c in (
            (0, 0, 0), (255, 255, 255), (255, 255, 0), (0, 255, 255), (0, 255, 0))]
        self.offset = {"pushButton":(-30, 0), "label":(-10, 3), "labelPerChar":(-5, 0),
                       "lineEdit":(-60, 0), "comboBox":(-5, 0), "comboBoxPerChar":(-3, 0)}
        for i in self.offset:
            self.offset[i] = np.array(self.offset[i])
        self.createWidgets()
        self.show()
        
    def addWidget(self, widget, offset, pos):
        self.widgets.append((widget, np.array(pos), np.array(offset)))
    def addLineEdit(self, name, pos, expr):
        QLE = Widgets.QLineEdit(self)
        if expr:
            QLE.setValidator(PyQt5.QtGui.QRegExpValidator(PyQt5.QtCore.QRegExp(expr), self))
        self.addWidget(QLE, self.offset["lineEdit"], pos)
        self.addWidget(Widgets.QLabel(self), self.offset["lineEdit"] + self.offset["label"] 
                       + self.offset["labelPerChar"] * len(name), pos)
        self.widgets[-1][0].setText(name)
        return QLE
    def addComboBox(self, name, pos, items):
        QCB = Widgets.QComboBox(self)
        QCB.addItems(items)
        shift = self.offset["comboBox"] + self.offset["comboBoxPerChar"] * len(name)
        self.addWidget(QCB, shift, pos)
        self.addWidget(Widgets.QLabel(self), shift + self.offset["label"]
                       + self.offset["labelPerChar"] * len(name), pos)
        self.widgets[-1][0].setText(name)
        return QCB
    def addPushButton(self, name, pos, event):
        self.addWidget(Widgets.QPushButton(name, self), self.offset["pushButton"], pos)
        self.widgets[-1][0].clicked.connect(event)
    def createWidgets(self):
        self.fileQLE = self.addLineEdit("file",  (0, 0), None)
        self.sizeXQLE = self.addLineEdit("sizeX", (0, 1), "[0-9]{0,2}")
        self.sizeYQLE = self.addLineEdit("sizeY", (0, 2), "[0-9]{0,2}")
        
        self.algorithm = self.addComboBox("Algorithm", (0, 3), ["Eller", "DFS", "Prim"])
        self.start = self.addComboBox("Start", (0, 4), ["Corner", "Random", "Further"])
        
        self.randomExit = Widgets.QPushButton("RandomExit", self)
        self.addWidget(self.randomExit, self.offset["pushButton"], (0, 5))
        self.randomExit.setCheckable(True)
        self.multiPlayer = Widgets.QPushButton("MultiPlayer", self)
        self.multiPlayer.clicked.connect(self.main.switchMultiPlayer)
        self.addWidget(self.multiPlayer, self.offset["pushButton"], (0, 6))
        self.multiPlayer.setCheckable(True)
        
        self.addPushButton("Start", (0, 7), lambda: self.main.switchMode(True))
        self.addPushButton("Continue", (0, 8), self.main.switchMode)
        self.addPushButton("Save", (0, 9), lambda: self.main.save(self.fileQLE.text()))
        self.addPushButton("Load", (0, 10), lambda: self.main.load(self.fileQLE.text()))
        self.addPushButton("Quit", (0, 11), self.main.close)
        self.moveWidgets()
    def moveWidgets(self):
        for widget, pos, offset in self.widgets:
            widget.move(*(np.array((self.width() // 2, self.height() // 2))
                          + self.globalOffset + offset + pos * self.stretch))
        
    def paintEvent(self, event):
        self.resize(self.main.width(), self.main.height())
        if not self.main.game:
            self.moveWidgets()
        elif self.main.cells:
            self.paint()
    def paint(self):
        self.cell = [self.main.width() // self.shape[0],  self.main.height() // self.shape[1]]
        self.cell = [min(self.cell)] * 2
        self.qp = PyQt5.QtGui.QPainter()
        self.qp.begin(self)
        self.qp.setPen(QColor(0, 0, 0, 0))
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                col = self.main.cells[i][j] + 1
                col = col if self.main.showSolution else col != 0
                self.drawRectangle(i, j, self.colors[col])
        self.drawRectangle(*tuple(self.main.position[0]), QColor(255, 0, 0))
        if self.multiPlayer.isChecked():
            if (self.main.position[0] == self.main.position[1]).all():
                self.drawRectangle(*tuple(self.main.position[1]), QColor(255, 0, 255))
            else:
                self.drawRectangle(*tuple(self.main.position[1]), QColor(0, 0, 255))
        self.qp.end()
        self.update()
        
    def drawRectangle(self, x, y, c):
        self.qp.setBrush(c)
        self.qp.drawRect(x * self.cell[0], (self.shape[1]-1-y) * self.cell[1], *self.cell)