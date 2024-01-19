# standard imports
import sys
from time import sleep
from typing import Optional

# third-party imports
from qtpy.QtCore import QObject, Qt, QThread, Signal
from qtpy.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)


class Worker(QObject):
    finished_signal = Signal()
    progress_signal = Signal(int, int)

    def __init__(self, n=5):
        super().__init__()
        self.maximum = n

    def run(self):
        for i in range(self.maximum):
            sleep(1)
            self.progress_signal.emit(i + 1, self.maximum)  # signal triggering execution of Window.reportProgress()
        self.finished_signal.emit()  # signal triggering clean up steps


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Resources attributes
        self.thread: Optional[QThread] = None
        self.worker: Optional[Worker] = None

        # Model attributes
        self.clicksCount = 0

        # UI attributes
        self.centralWidget = None
        self.countBtn = None
        self.long_running_button = None
        self.clicksLabel = None
        self.stepLabel = None
        self.progressBar = None

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Freezing GUI")
        self.resize(300, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.clicksLabel = QLabel("Counting: 0 clicks", self)
        self.clicksLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.progressBar = QProgressBar(self)
        self.stepLabel = QLabel("Long-Running Step: 0")
        self.stepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.countBtn = QPushButton("Click me!", self)
        self.countBtn.clicked.connect(self.countClicks)
        self.long_running_button = QPushButton("Long-Running Task!", self)
        self.long_running_button.clicked.connect(self.runLongTask)

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.clicksLabel)
        layout.addWidget(self.countBtn)
        layout.addStretch()
        layout.addWidget(self.stepLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.long_running_button)
        self.centralWidget.setLayout(layout)

    def countClicks(self):
        self.clicksCount += 1
        self.clicksLabel.setText(f"Counting: {self.clicksCount} clicks")

    def reportProgress(self, current, maximum):
        self.stepLabel.setText(f"Long-Running Step: {current}")
        self.progressBar.setValue(int(100 * current / maximum))

    def runLongTask(self):
        # instantiation of resources
        steps = 8
        self.thread = QThread()
        self.worker = Worker(steps)
        self.worker.moveToThread(self.thread)

        # signals and slots: communication between worker and main threads
        self.worker.progress_signal.connect(self.reportProgress)

        # signals and slots: setup
        self.thread.started.connect(self.worker.run)

        # signals and slots: teardown
        self.worker.finished_signal.connect(self.worker.deleteLater)
        self.worker.finished_signal.connect(self.thread.quit)
        self.thread.finished.connect(lambda: self.long_running_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.stepLabel.setText("Long-Running Step: 0"))
        self.thread.finished.connect(self.thread.deleteLater)

        # begin execution
        self.long_running_button.setEnabled(False)  # prevent user from running additional long tasks
        self.thread.start()






app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
