import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import script


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Low-Pollution Route Planner')

        self.input1_label = QLabel('Start:')
        self.input1_text = QLineEdit()
        self.input2_label = QLabel('End:')
        self.input2_text = QLineEdit()

        self.run_button = QPushButton('Find Route')
        self.run_button.clicked.connect(self.run_script)

        self.figure_canvas = FigureCanvas(plt.Figure())

        # Layout setup
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        hbox1.addWidget(self.input1_label)
        hbox1.addWidget(self.input1_text)

        hbox2.addWidget(self.input2_label)
        hbox2.addWidget(self.input2_text)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.run_button)
        vbox.addWidget(self.figure_label)
        vbox.addWidget(self.figure_canvas)

        self.setLayout(vbox)

    def run_script(self):
        # Get inputs
        start = self.input1_text.text()
        end = self.input2_text.text()

        try:
            fig, ax = your_script.run(start, end)

            self.figure_canvas.figure.clear()

            ax.plot()
            self.figure_canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error running script: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())