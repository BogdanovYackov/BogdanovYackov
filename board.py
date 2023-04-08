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
        self.offset = np.array((0, -75))
        self.stretch = 25
        self.colors = [QColor(*c) for c in ((0, 0, 0), (255, 255, 255),
                             (255, 255, 0), (0, 255, 255), (0, 255, 0))]
        self.createWidgets()
        self.show()
        
    def addWidget(self, widget, offset, pos):
        self.widgets.append((widget, np.array(pos), np.array(offset)))
    def addLineEdit(self, name, pos, expr):
        QLE = Widgets.QLineEdit(self)
        if expr:
            QLE.setValidator(PyQt5.QtGui.QRegExpValidator(PyQt5.QtCore.QRegExp(expr), self))
        self.addWidget(QLE, (-60, 0), pos)
        self.addWidget(Widgets.QLabel(self), (-65-5*len(name), 3), pos)
        self.widgets[-1][0].setText(name)
        return QLE
    def addComboBox(self, name, pos, items):
        QCB = Widgets.QComboBox(self)
        QCB.addItems(items)
        shift = 3 * max(map(len, items))
        self.addWidget(QCB, (-5-shift, 0), pos)
        self.addWidget(Widgets.QLabel(self), (-15-5*len(name)-shift, 3), pos)
        self.widgets[-1][0].setText(name)
        return QCB
    def addPushButton(self, name, pos, event):
        self.addWidget(Widgets.QPushButton(name, self), (-30, 0), pos)
        self.widgets[-1][0].clicked.connect(event)
    def createWidgets(self):
        self.fileQLE = self.addLineEdit("file",  (0, -3), None)
        self.sizeXQLE = self.addLineEdit("sizeX", (0, -2), "[0-9]{0,2}")
        self.sizeYQLE = self.addLineEdit("sizeY", (0, -1), "[0-9]{0,2}")
        
        self.algorithm = self.addComboBox("Algorithm", (0, 0), ["Eller", "DFS", "Prim"])
        self.start = self.addComboBox("Start", (0, 1), ["Corner", "Random", "Further"])
        
        self.randomExit = Widgets.QPushButton("RandomExit", self)
        self.addWidget(self.randomExit, (-30, 0), (0, 2))
        self.randomExit.setCheckable(True)
        self.multiPlayer = Widgets.QPushButton("MultiPlayer", self)
        self.multiPlayer.clicked.connect(self.main.switchMultiPlayer)
        self.addWidget(self.multiPlayer, (-30, 0), (0, 3))
        self.multiPlayer.setCheckable(True)
        
        self.addPushButton("Start", (0, 4), lambda: self.main.switchMode(True))
        self.addPushButton("Continue", (0, 5), self.main.switchMode)
        self.addPushButton("Save", (0, 6), lambda: self.main.save(self.fileQLE.text()))
        self.addPushButton("Load", (0, 7), lambda: self.main.load(self.fileQLE.text()))
        self.addPushButton("Quit", (0, 8), self.main.close)
        self.moveWidgets()
    def moveWidgets(self):
        for widget, pos, offset in self.widgets:
            widget.move(*(np.array((self.width() // 2, self.height() // 2))
                          + self.offset + offset + pos * self.stretch))
        
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
                col = col if self.main.showSollution else col != 0
                self.drawRectangle(i, j, self.colors[col])
        self.drawRectangle(*self.main.position[0], QColor(255, 0, 0))
        if self.multiPlayer.isChecked():
            if (self.main.position[0] == self.main.position[1]).all():
                self.drawRectangle(*self.main.position[1], QColor(255, 0, 255))
            else:
                self.drawRectangle(*self.main.position[1], QColor(0, 0, 255))
        self.qp.end()
        self.update()
        
    def drawRectangle(self, x, y, c):
        self.qp.setBrush(c)
        self.qp.drawRect(x * self.cell[0], (self.shape[1]-1-y) * self.cell[1], *self.cell)
