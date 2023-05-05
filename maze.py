import pip
try:
    import numpy as np
    import os
    import pickle
    import PyQt5
    import random
    import sys
except:
    for package in ['numpy', 'os', 'pickle', 'PyQt5', 'random', 'sys']:
        if hasattr(pip, 'main'):
            pip.main(['install', package])
        else:
            pip._internal.main(['install', package])
    import numpy as np
    import os
    import pickle
    import PyQt5
    import random
    import sys
import PyQt5.QtWidgets as Widgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class Maze(Widgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Maze')
        self.setWindowIcon(PyQt5.QtGui.QIcon("icon.png"))
        self.setFocusPolicy(Qt.StrongFocus)
        self.game = 0
        self.shape = [0] * 2
        self.defaultShape = [15] * 2
        self.cells = []
        self.showSollution = False
        self.position = [np.array((0, 0))] * 2
        self.dirs = tuple(map(np.array, ((1, 0), (0, 1), (-1, 0), (0, -1))))
        self.board = Board(self)
        self.renewSize()
        self.show()

    def switchMode(self, restart = False):
        restart |= self.game and not self.cells
        self.game = not self.game
        self.board.moveWidgets()
        for widget, pos, offset in self.board.widgets:
            widget.setHidden(self.game)
        start = not self.cells
        if restart or (start and not
                os.path.exists(os.path.abspath("saves/__last__.data"))):
            self.renewSize(True)
            self.generate()
        else:
            if start:
                self.load("__last__")
            self.renewSize(start)
    def center(self):
        screen = Widgets.QDesktopWidget().screenGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
    def renewSize(self, restart = False):
        if self.game:
            if restart:
                self.sizeX = self.board.sizeXQLE.text()
                self.sizeY = self.board.sizeYQLE.text()
                if self.sizeX == "" and self.sizeY == "":
                    self.shape = self.defaultShape
                elif self.sizeX == "":
                    self.shape = [max(1, int(self.sizeY))] * 2
                elif self.sizeY == "":
                    self.shape = [max(1, int(self.sizeX))] * 2
                else:
                    self.shape = [max(1, int(self.sizeX)), max(1, int(self.sizeY))]
                self.board.shape = (2 * self.shape[0] + 1, 2 * self.shape[1] + 1)
            self.resize(*self.board.defaultSize)
        else:
            self.resize(*self.board.defaultSizeMenu)
        self.center()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.switchMode()
        elif key == Qt.Key_F5:
            self.save("__quick__")
        elif key == Qt.Key_F9:
            self.load("__quick__")
        elif self.game:
            self.keyPressGame(key)
    def keyPressGame(self, key):
        if key == Qt.Key_Space:
            self.showSollution = not self.showSollution
        elif key == Qt.Key_Left:
            self.tryMove(-1, 0, 1)
        elif key == Qt.Key_Right:
            self.tryMove( 1, 0, 1)
        elif key == Qt.Key_Down:
            self.tryMove( 0,-1, 1)
        elif key == Qt.Key_Up:
            self.tryMove( 0, 1, 1)
        elif not self.board.multiPlayer.isChecked():
            pass
        elif key == Qt.Key_A:
            self.tryMove(-1, 0, 2)
        elif key == Qt.Key_D:
            self.tryMove( 1, 0, 2)
        elif key == Qt.Key_S:
            self.tryMove( 0,-1, 2)
        elif key == Qt.Key_W:
            self.tryMove( 0, 1, 2)
    
    def closeEvent(self, event):
        self.save("__last__")
        sys.exit()
    
    def save(self, name):
        if self.cells:
            if not os.path.exists("saves"):
                os.mkdir(path)
            with open(f"saves\\{name}.data", 'wb') as f:
                pickle.dump((self.cells, self.position, self.exit,
                             self.board.multiPlayer.isChecked()), f)
        
    def load(self, name):
        with open(f"saves\\{name}.data", 'rb') as f:
            self.cells, self.position, self.exit, multiPlayer = pickle.load(f)
        self.board.shape = (len(self.cells), len(self.cells[0]))
        self.shape = (len(self.cells) // 2, len(self.cells[0]) // 2)
        self.showSollution = False
        if multiPlayer != self.board.multiPlayer.isChecked():
            self.board.multiPlayer.toggle()
        if self.game:
            self.center()
        else:
            self.switchMode()

    def tryMove(self, x, y, player):
        pos = self.position[player - 1]
        npos = pos + np.array((x, y))
        if self.cells[npos[0]][npos[1]] >= 0:
            if self.cells[npos[0]][npos[1]] & player:
                self.cells[npos[0]][npos[1]] ^= player
            else:
                self.cells[pos[0]][pos[1]] ^= player
            self.position[player - 1] = npos
            if (npos == self.exit).all():
                self.switchMode()
        
    def check(self, pos):
        if (self.shape[0]*2 >= pos[0] >= 0) and (self.shape[1]*2 >= pos[1] >= 0):
            if self.cells[pos[0]][pos[1]] == -1:
                return 1
        return 0
    def generateExit(self):
        self.exit = (2*self.shape[0], 2*self.shape[1] - 1)
        if self.board.randomExit.isChecked():
            exit = random.randint(0, self.shape[0] + self.shape[1] - 1)
            if exit < self.shape[0]:
                self.exit = (2*exit+1, 2*self.shape[0]*random.randint(0, 1))
            else:
                self.exit = (2*self.shape[1]*random.randint(0, 1), 2*(exit-self.shape[0])+1)
        self.exit = np.array(self.exit)
        self.cells[self.exit[0]][self.exit[1]] = 0
    def generate(self):
        self.cells = [[-1]*(self.shape[1]*2+1) for i in range(self.shape[0]*2+1)]
        self.position = np.array((random.randint(1, self.shape[0])*2-1,
                                  random.randint(1, self.shape[1])*2-1))
        if self.board.algorithm.currentText() == "DFS":
            self.generateDFS()
        elif self.board.algorithm.currentText() == "Prim":
            self.generatePrim()
        else:
            self.generateEller()
        if self.board.start.currentText() == "Corner":
            self.position = np.array((1, 1))
        self.generateExit()
        self.position = [self.position, self.position]
        self.sollution(self.board.start.currentText() == "Further")
       
    def generateDFS(self):
        stack = [self.position]
        self.cells[self.position[0]][self.position[1]] = 0
        while stack:
            count = 0
            p = stack[-1]
            for d in self.dirs:
                count += self.check(p + 2 * d)
            if count == 0:
                del stack[-1]
            else:
                count = random.randint(1, count)
                for d in self.dirs:
                    n = p + 2 * d
                    count -= self.check(n)
                    if count == 0:
                        self.cells[n[0]][n[1]] = 0
                        self.cells[p[0]+d[0]][p[1]+d[1]] = 0
                        stack.append(n)
                        break

    def generatePrim(self):
        stack = [(self.position, self.position)]
        while stack:
            choice = random.randint(0, len(stack)-1)
            p = stack[choice]
            if self.check(p[1]):
                self.cells[p[0][0]][p[0][1]] = 0
                self.cells[p[1][0]][p[1][1]] = 0
                for d in self.dirs:
                    stack.append((p[1] + d, p[1] + 2 * d))
            del stack[choice]

    def generateEllerHEdjes(self, i, bottom = False):
        for j in range(self.shape[0] - 1):
            if (self.row[j] != self.row[j+1]) and (
                 random.randint(0, 1) or bottom):
                self.cells[i][2*j+2] = 0
                s = self.row[j+1]
                for k in self.sets[s]:
                    self.row[k] = self.row[j]
                self.sets[self.row[j]] |= self.sets[s]
                del self.sets[s]
    def generateEllerVEdjes(self, i):
        for s in self.sets:
            r = random.randint(0, 2**len(self.sets[s])-2)
            for j in self.sets[s]:
                self.cells[i][2*j+1] = -(r & 1)
                r //= 2
        for j in range(self.shape[0]):
            if self.cells[i][2*j+1]:
                self.sets[self.row[j]].remove(j)
                self.row[j] = self.n
                self.sets[self.n] = {j}
                self.n += 1
    def generateEller(self):
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.cells[2*i+1][2*j+1] = 0
        self.row = list(range(self.shape[0]))
        self.sets = dict([[i,{i}] for i in range(self.shape[0])])
        self.n = self.shape[0]
        for i in range(self.shape[1] - 1):
            self.generateEllerHEdjes(2 * i + 1)
        #    for j in range(self.shape[1]):
        #        self.cells[2*i+1][2*j+1] = self.row[j] + 1
            self.generateEllerVEdjes(2 * i + 2)
        self.generateEllerHEdjes(2 * self.shape[1] - 1, True)
        del self.n
        del self.row
        del self.sets

    def sollution(self, start = False):
        soll = [[0 for j in range(self.shape[1]*2+1)] for i in range(self.shape[0]*2+1)]
        stack = [self.exit]
        maxWay = []
        while stack:
            p = stack[-1]
            if (p == self.position).all() and not start:
                break
            if soll[p[0]][p[1]] == len(self.dirs):
                if start and len(stack) > len(maxWay):
                    maxWay = stack[:]
                del stack[-1]
                continue
            n = p + self.dirs[soll[p[0]][p[1]]]
            if (self.shape[0]*2 >= n[0] >= 0) and (self.shape[1]*2 >= n[1] >= 0):
                if (self.cells[n[0]][n[1]] == 0) and soll[n[0]][n[1]] == 0:
                    stack.append(n)
            soll[p[0]][p[1]] += 1
        if start:
            stack = maxWay
            self.position = stack[-1]
        del stack[-1]
        for p in stack:
            self.cells[p[0]][p[1]] = 1
        
    def switchMultiPlayer(self, restart = False):
        self.position[1] = self.position[0]
        if self.cells:
            c = 1 - self.board.multiPlayer.isChecked()
            for i in range(self.board.shape[0]):
                for j in range(self.board.shape[1]):
                    if self.cells[i][j] > c:
                        self.cells[i][j] ^= 2        



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

app = Widgets.QApplication(sys.argv)
Maze()
sys.exit(app.exec_())
