from tokenize import String
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Worker import Worker
from Merge import Merge

class Program(QWidget):
    src_folder = "test"
    result_folder = "test"

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        src_label = QLabel('Папка с MIF/MID', self)

        self.src_folder_input = QLineEdit(self.src_folder, self)
        self.src_folder_input.setReadOnly(True)

        src_button = QPushButton("...", self)
        src_button.clicked.connect(self.getSrcFolder)

        result_label = QLabel('Папка для сохранения', self)

        self.result_folder_input = QLineEdit(self.result_folder, self)
        self.result_folder_input.setReadOnly(True)

        result_button = QPushButton("...", self)
        result_button.clicked.connect(self.getResultFolder)

        self.process_file = QLabel("Ожидание...", self)
        self.start_button = QPushButton("Запуск", self)
        self.start_button.clicked.connect(self.start_process)

        self.log = QPlainTextEdit("Старт", self)
        self.log.setReadOnly(True)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(src_label, 0, 0)
        grid.addWidget(self.src_folder_input, 0, 1)
        grid.addWidget(src_button, 0, 2)

        grid.addWidget(result_label, 1, 0)
        grid.addWidget(self.result_folder_input, 1, 1)
        grid.addWidget(result_button, 1, 2)

        grid.addWidget(self.process_file, 2, 0)
        grid.addWidget(self.start_button, 2, 2)
        
        grid.addWidget(self.log, 3, 0, 4, 3)

        self.setLayout(grid)
        
        self.resize(600, 400)
        self.setWindowTitle('Merge MIF MIDs')
        self.show()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())    
    
    def getSrcFolder(self):
        self.src_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.src_folder_input.setText(self.src_folder)
    
    def getResultFolder(self):
        self.result_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.result_folder_input.setText(self.result_folder)

    def print_process(self, str):
        print(str)

    def start_process(self):
        self.process_file.setText("В процессе...")

        # Merge(self.src_folder, self.result_folder)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        print("Create Worker")
        self.worker = Worker(Merge, self.src_folder, self.result_folder)

        print("Add Button \"Отмена\"")
        self.worker.setAutoDelete(True)
        self.start_button.clicked.connect(self.stop_process)
        self.start_button.setText("Отмена")

        self.worker.signal.printer.connect(self.log.appendPlainText)
        self.worker.signal.final.connect(self.final_process)

        print("Start Worker")
        self.threadpool.start(self.worker)

    def stop_process(self):
        self.threadpool.cancel(self.worker.stop)

    def final_process(self):
        self.process_file.setText("Завершено!")
        QMessageBox.information(None, 'Завершено', "Готово!")

if __name__ == '__main__':

    app = QApplication(sys.argv)

    gui = Program()

    sys.exit(app.exec_())
