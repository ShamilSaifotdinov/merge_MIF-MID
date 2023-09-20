from PyQt5.QtCore import *
import traceback
from WorkerSignals import WorkerSignals

class Worker(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, fn, *args):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.signal = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Your code goes in this function
        '''
        try:
            self.fn(*self.args, self.signal.printer.emit)
        except:
            print("")
            self.signal.printer.emit("")
            print(traceback.format_exc())
            self.signal.printer.emit(traceback.format_exc())
        finally:
            self.signal.final.emit()