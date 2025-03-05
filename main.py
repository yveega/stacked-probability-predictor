import sys
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import numpy as np

PARAMS = ["Ишемическая болезнь сердца",
"Гипертония",
"Мерцательная аритмия",
"Инсульт",
"Тромбозы сосудов",
"Эмболии артерий",
"Анемия",
"Сахарный диабет 2 типа",
"ХБП 1 ст",
"ХБП 2 ст",
"ХБП 3 ст",
"ХБП 4 ст",
"ХБП 5 ст",
"Лёгочная гипертензия",
"Эмфизема легких",
"Жировой гепатоз печени",
"Рак",
"Метастатический рак",
"Болезнь Паркинсона",
"Аутоиммунные заболевания"]

COEFFS = np.array([1, 1, 1, 1, 1, 0, 1, 0, -4, -3, -2, 0, 0, 0, 1, -2, 0, 1, 0, -1])
print(len(COEFFS), len(PARAMS))


class CheckboxWindow(QWidget):
    def __init__(self, parent=None, initial_params=None):
        super(CheckboxWindow, self).__init__(parent)
        self.listCheckBox = []
        grid = QGridLayout()

        for i, v in enumerate(PARAMS):
            self.listCheckBox.append(QCheckBox(v))
            if initial_params is not None and initial_params[i]:
                self.listCheckBox[i].setChecked(initial_params[i])
            grid.addWidget(self.listCheckBox[i], i, 0)

        self.button = QPushButton("Check CheckBox")

        grid.addWidget(self.button,     len(PARAMS), 0, 1,2)
        self.setLayout(grid)


class GraphWindow(QWidget):
    def __init__(self, patient_params, parent=None):
        super(GraphWindow, self).__init__(parent)
        self.comorbidity = np.sum(patient_params * COEFFS)
        self.comorbidity_label = QLabel("Индекс коморбидности φ = " + str(self.comorbidity))
        self.back_button = QPushButton("Back")
        self.layout = QGridLayout()
        self.layout.addWidget(self.comorbidity_label, 0, 0)
        self.layout.addWidget(self.back_button, 1, 0)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(50, 100, 1700, 800)
        self.setFixedSize(1700, 800)
        self.patient_params = np.zeros((len(PARAMS)), dtype=np.bool)
        self.startCheckboxWindow()
    
    def startCheckboxWindow(self):
        self.CheckboxW = CheckboxWindow(initial_params=self.patient_params)
        self.setWindowTitle("Choose")
        self.setCentralWidget(self.CheckboxW)
        self.CheckboxW.button.clicked.connect(self.startGraphWindow)
        self.show()

    def startGraphWindow(self):
        self.read_params()
        self.GraphW = GraphWindow(self.patient_params)
        self.setWindowTitle("Graph")
        self.setCentralWidget(self.GraphW)
        self.GraphW.back_button.clicked.connect(self.startCheckboxWindow)
        self.show()
    
    def read_params(self):
        for i, checkbox in enumerate(self.CheckboxW.listCheckBox):
            self.patient_params[i] = bool(checkbox.checkState())
        print(self.patient_params)


app = QApplication([])
main = MainWindow()
main.show()
app.exec()