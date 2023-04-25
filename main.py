import PyQt5.QtWidgets as Widgets
import sys
import maze

app = Widgets.QApplication(sys.argv)
maze.Maze()
sys.exit(app.exec_())
