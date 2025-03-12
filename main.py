import sys
import os
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QFont
from pyqtgraph import PlotWidget, FillBetweenItem, LegendItem
import numpy as np
from bootstrap import bootstrap

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
if getattr(sys, 'frozen', False):
    transition_probs_before5 = np.loadtxt(os.path.join(sys._MEIPASS, "data\\tran_probs_before_5d.txt"))
    transition_probs_after5 = np.loadtxt(os.path.join(sys._MEIPASS, "data\\tran_probs_after_5d.txt"))
else:
    transition_probs_before5 = np.loadtxt("data\\tran_probs_before_5d.txt")
    transition_probs_after5 = np.loadtxt("data\\tran_probs_after_5d.txt")

STATES = ["Смерть", "ИВЛ", "НИВЛ", "БП", "Выписка"]


class AreaPlotWidget(PlotWidget):
    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super(AreaPlotWidget, self).__init__(parent, background, plotItem, **kargs)
        self.oreder_plots = [4, 2, 1, 0, 3]
        self.plots = []
        self.fills = []
        self.legend = self.addLegend(brush=(50, 50, 50, 90),
                                     offset=(-50, 50),
                                     labelTextColor=(0, 0, 0))
        self.setInteractive(False)
        self.setLabel("left", "вероятность", color="black")
        self.setLabel("bottom", "время (дни)", color="black")
        title = self.getPlotItem().titleLabel.text
        self.setTitle(title, color="black")
        self.showGrid(x=True, y=True)

    def areaPlot(self, x, y, names, brushes=None):
        if brushes is None:
            brushes = [(70, 70, 70, 100),
                       (240, 10, 10, 100),
                       (240, 200, 10, 100),
                       (50, 50, 250, 100),
                       (50, 250, 50, 100)]
        y_shifted = np.zeros((len(x)), dtype=y.dtype)
        self.plots = []
        self.fills = []
        self.plots.append(self.plot(x, y_shifted))
        for i in range(y.shape[0]):
            y_shifted = y_shifted + y[self.oreder_plots[i]]
            self.plots.append(self.plot(x, y_shifted, pen=QColor(*brushes[i])))
            self.fills.append(FillBetweenItem(self.plots[i], self.plots[i + 1], brush=brushes[i]))
            self.addItem(self.fills[-1])
            self.legend.addItem(self.plots[i + 1], names[i])
        self.getPlotItem().setContentsMargins(15, 15, 15, 15)
        self.setXRange(0, len(x) - 1, padding=0)
        self.setYRange(0, 1, padding=0)


class CheckboxWindow(QWidget):
    def __init__(self, parent=None, initial_params=None):
        super(CheckboxWindow, self).__init__(parent)
        self.listCheckBox = []
        box_widget = QWidget()
        box_layout = QVBoxLayout()
        grid = QGridLayout()
        label = QLabel(text="Выберите хронические заболевания, наблюдающиеся у пациента")

        for i, v in enumerate(PARAMS):
            self.listCheckBox.append(QCheckBox(v))
            if initial_params is not None and initial_params[i]:
                self.listCheckBox[i].setChecked(initial_params[i])
            box_layout.addWidget(self.listCheckBox[i])

        self.button = QPushButton("Расчёт")
        box_widget.setLayout(box_layout)
        grid.addWidget(label, 0, 0)
        grid.addWidget(box_widget, 1, 0)
        grid.addWidget(self.button, 2, 0)
        self.setLayout(grid)


class GraphWindow(QWidget):
    def __init__(self, patient_params, parent=None):
        super(GraphWindow, self).__init__(parent)
        self.comorbidity = np.sum(patient_params * COEFFS)
        self.P_before5d = np.eye(len(STATES), dtype=float)
        self.P_after5d = np.eye(len(STATES), dtype=float)
        if self.comorbidity <= 0:
            self.comorbidity_label = QLabel("Индекс коморбидности φ = " + str(self.comorbidity)
                                            + ". Низкое значение")
            self.P_before5d[:3] = transition_probs_before5[:3]
            self.P_after5d[:3] = transition_probs_after5[:3]
        elif self.comorbidity <= 3:
            self.comorbidity_label = QLabel("Индекс коморбидности φ = " + str(self.comorbidity)
                                            + ". Среднее значение")
            self.P_before5d[:3] = transition_probs_before5[3:6]
            self.P_after5d[:3] = transition_probs_after5[3:6]
        else:
            self.comorbidity_label = QLabel("Индекс коморбидности φ = " + str(self.comorbidity)
                                            + ". Высокое значение")
            self.P_before5d[:3] = transition_probs_before5[6:]
            self.P_after5d[:3] = transition_probs_after5[6:]
        self.back_button = QPushButton("Назад")

        self.IV_radio = QRadioButton(text="ИВЛ")
        self.IV_radio.initial_state = [0.0, 0.0, 1.0, 0.0, 0.0]
        self.IV_radio.toggled.connect(self.onInitialStateChanged)

        self.NIV_radio = QRadioButton(text="НИВЛ")
        self.NIV_radio.initial_state = [0.0, 1.0, 0.0, 0.0, 0.0]
        self.NIV_radio.toggled.connect(self.onInitialStateChanged)

        self.no_IV_radio = QRadioButton(text="без вентиляции")
        self.no_IV_radio.setChecked(True)
        self.no_IV_radio.initial_state = [1.0, 0.0, 0.0, 0.0, 0.0]
        self.no_IV_radio.toggled.connect(self.onInitialStateChanged)
        self.initial_state = self.no_IV_radio.initial_state
        self.duration = 20

        self.label_state = QLabel(text="Начальное состояние пациента:")
        self.layout = QGridLayout()
        self.graph = AreaPlotWidget(background="white", title="Средний случай")
        self.low_graph = AreaPlotWidget(background=(220, 255, 220), title="Наилучший случай (95%)")
        self.high_graph = AreaPlotWidget(background=(255, 220, 220), title="Наихудший случай (95%)")
        self.plotAll()

        self.layout.addWidget(self.comorbidity_label, 0, 0, 1, 3)
        self.layout.addWidget(self.back_button, 0, 5)
        self.layout.addWidget(self.label_state, 1, 0)
        self.layout.addWidget(self.IV_radio, 1, 1)
        self.layout.addWidget(self.NIV_radio, 1, 2)
        self.layout.addWidget(self.no_IV_radio, 1, 3)
        self.layout.addWidget(self.graph, 2, 0, 1, 6)
        self.layout.addWidget(self.low_graph, 3, 0, 1, 3)
        self.layout.addWidget(self.high_graph, 3, 3, 1, 3)
        self.setLayout(self.layout)
    
    def plotStackedProbability(self, plotwidget, P_before5d, P_after5d, initial_state, duration):
        values = np.zeros((len(STATES), duration + 1), dtype=float)
        values[:, 0] = initial_state
        for i in range(1, 6):
            values[:, i] = np.dot(P_before5d.T, values[:, i - 1])
        for i in range(6, duration + 1):
            values[:, i] = np.dot(P_after5d.T, values[:, i - 1])
        plotwidget.getPlotItem().clear()
        plotwidget.areaPlot(np.arange(0, duration + 1), values, STATES)

    def plotAll(self):
        self.plotStackedProbability(self.graph,
                                    self.P_before5d, self.P_after5d,
                                    self.initial_state,
                                    self.duration)
        P_low, P_high = bootstrap(self.comorbidity, self.initial_state, self.duration)
        self.plotStackedProbability(self.low_graph,
                                    P_low[0], P_low[1],
                                    self.initial_state,
                                    self.duration)
        self.plotStackedProbability(self.high_graph,
                                    P_high[0], P_high[1],
                                    self.initial_state,
                                    self.duration)

    def onInitialStateChanged(self):
        radio = self.sender()
        if radio.isChecked():
            self.initial_state = radio.initial_state
            self.plotAll()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Stacked Probability Predictor")
        self.setGeometry(50, 100, 1700, 900)
        self.setFixedSize(1700, 900)
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


app = QApplication([])
font = QFont()
font.setWeight(25)
app.setStyleSheet("QLabel{font-size: 14pt;}")
main = MainWindow()
main.show()
app.exec()