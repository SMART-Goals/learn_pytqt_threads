import logging
import random
import sys
from time import sleep

from qtpy.QtCore import QMutex, QMutexLocker, QObject, QThread, Signal
from qtpy.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logging.basicConfig(format="%(message)s", level=logging.INFO)

balance = 100.00
mutex = QMutex()


class AccountManager(QObject):
    finished = Signal()
    updatedBalance = Signal()
    allThreadsFinished = Signal()

    def withdraw(self, person, amount):
        logging.info("%s wants to withdraw $%.2f...", person, amount)
        global balance
        with QMutexLocker(mutex):
            if balance - amount >= 0:
                sleep(random.randint(1, 4))
                balance -= amount
                logging.info("-$%.2f accepted", amount)
            else:
                logging.info("-$%.2f rejected", amount)
            logging.info("===Balance===: $%.2f", balance)
            self.updatedBalance.emit()
        self.finished.emit()


class Window(QMainWindow):
    allWithdrawalsFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.threads = []

    def setupUi(self):
        self.setWindowTitle("Account Manager")
        self.resize(200, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.button = QPushButton("Withdraw Money!")
        self.button.clicked.connect(self.startThreads)
        self.balanceLabel = QLabel(f"Current Balance: ${balance:,.2f}")
        layout = QVBoxLayout()
        layout.addWidget(self.balanceLabel)
        layout.addWidget(self.button)
        self.centralWidget.setLayout(layout)
        self.allWithdrawalsFinished.connect(lambda: self.button.setEnabled(True))

    def createThread(self, person, amount):
        thread = QThread()
        worker = AccountManager()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.withdraw(person, amount))
        worker.updatedBalance.connect(self.updateBalance)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        return thread

    def startThreads(self):
        self.button.setEnabled(False)
        self.threads.clear()
        people = {
            "Alice": random.randint(100, 10000) / 100,
            "Bob": random.randint(100, 10000) / 100,
        }
        self.threads = [
            self.createThread(person, amount)
            for person, amount in people.items()
        ]
        self.activeWithdrawalCount = len(self.threads)
        for thread in self.threads:
            thread.start()

    def updateBalance(self):
        self.balanceLabel.setText(f"Current Balance: ${balance:,.2f}")
        self.activeWithdrawalCount -= 1
        if self.activeWithdrawalCount == 0:
            self.allWithdrawalsFinished.emit()

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())


