from concurrent.futures import thread
from email.mime import base
import threading
import traceback
from unittest import result
from PyQt5.QtCore import QSize,Qt
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLabel,QCheckBox,QBoxLayout,QVBoxLayout,QHBoxLayout,QPlainTextEdit,QLineEdit,QMessageBox,QComboBox,QRadioButton,QTextEdit
from PyQt5.QtGui import QPalette,QColor,QIcon,QFont,QSyntaxHighlighter,QTextCursor
from PyQt5.QtCore import pyqtSlot,QObject,QThread,pyqtSignal,QRunnable,QThreadPool,QProcess
import os
from threading import *
import sys
basedir = os.path.dirname(__file__)
from sqlalchemy import true


from Main import *
from MyLib import *
from env import *
from Queries import *
import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    



class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

    
class Worker(QThread):
    def __init__(self,fn,**kwargs):
        super(Worker,self).__init__()
        self.signals = WorkerSignals()
        self.fn = fn
        self.kwargs = kwargs
        

    @pyqtSlot()
    def run(self):
        try:
            self.fn(**self.kwargs)
        except:
            print("Something went wrong with the Qthread worker class")
               

class AnotherWindow(QWidget):
    
    def __init__(self,windowname):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.setWindowTitle(windowname)
        self.setWindowIcon(QIcon(os.path.join(basedir,'./images/import.png')))
        self.setFixedSize(560,540)
        self.layout.addWidget(self.label)
        self.worker = None
        self.isClosed = False
        # Query
        self.textinput = QPlainTextEdit()
        self.layout.addWidget(self.textinput)
        
    
        
        self.qhboxlayout1 = QHBoxLayout()
        self.IterativeRadiobtn1 = QRadioButton('All Locations')
        self.IterativeRadiobtn2 = QRadioButton('Current Locations')
        self.IterativeRadiobtn2.setChecked(True)
       
        self.qhboxlayout1.addWidget(self.IterativeRadiobtn1)
        self.qhboxlayout1.addWidget(self.IterativeRadiobtn2)
        
        self.layout.addLayout(self.qhboxlayout1)
        
        # Check boxes
        self.c1 = QCheckBox("type1",self)
        self.c2 = QCheckBox("type2",self)
        self.c3 = QCheckBox("type3",self)
        self.c4 = QCheckBox("type4",self)
        
        self.c1.setChecked(True)
        
        self.hboxlayoutchoices = QHBoxLayout()
        
    
        #adding checkboxes to layout
        self.checkboxlist = [self.c1,self.c2,self.c3,self.c4]
        for cbox in self.checkboxlist:
            self.hboxlayoutchoices.addWidget(cbox)
        self.layout.addLayout(self.hboxlayoutchoices)

        # filename 
        self.filename = QLineEdit()
        self.layout.addWidget(self.filename)
            
        # Combo box to show the filetype which need to be saved
        self.extensions = QComboBox()
        self.combodict = {'Excel 97-2003 Workbook (*.xls)':'xls','CSV UTF-8 (Comma delimited) (*.csv)':'csv'}
        self.extensions.addItems(self.combodict)
        self.layout.addWidget(self.extensions)
        
        # import button
        self.exportBtn = QPushButton('Import')
        self.layout.addWidget(self.exportBtn)    
    
        
        #import function when button clicked  
        self.exportBtn.clicked.connect(self.importExcel)   
        
        #setting layout
        self.setLayout(self.layout)
        

        
      
    def closeEvent(self,event):
        if self.worker is None:
            event.accept()
            self.isClosed = True
        elif self.worker.isRunning():
            self.close = QMessageBox.question(self,"QUIT","Are you sure want to stop process?",
                                     QMessageBox.Yes|QMessageBox.No)
            if self.close == QMessageBox.Yes:
                    self.worker.terminate()
                    event.accept()
                    self.isClosed = True
                    print("Process Terminated!")
            elif self.close == QMessageBox.No:
                event.ignore()
        elif self.worker.isFinished():
            event.accept()
            self.isClosed = True
        else:
            event.ignore()
           
      
    def RadioButtonCheck(self):
        if self.IterativeRadiobtn1.isChecked():
            return True
        if self.IterativeRadiobtn2.isChecked():
            return False
        
    
    def setWidgetsDisableorEnable(self,widgetlist,DisabledOrEnabled):
        
        for widget in widgetlist:
            widget.setEnabled(DisabledOrEnabled)

    def importExcel(self):
        self.cboxlist = []
        for cbox in self.checkboxlist:
            if cbox.isChecked():
                self.cboxlist.append(cbox.text())
        
        self.textinput.setReadOnly(True)
        self.filename.setReadOnly(True)
        
        self.setWidgetsDisableorEnable([self.exportBtn,self.extensions],False)
        self.setWidgetsDisableorEnable(self.findChildren(QCheckBox),False)
        self.setWidgetsDisableorEnable(self.findChildren(QRadioButton),False)
        
        self.saveFilename = self.filename.text()
        self.text = self.textinput.toPlainText()
        self.inputextension = self.extensions.currentText()
        self.getvalue = self.combodict.get(self.inputextension)
        self.truorfalse = self.RadioButtonCheck()
        self.kwargs = {'Query':self.text,'Filename':self.saveFilename,'choices':self.cboxlist,'FileExtension':self.getvalue,'IterativeOrNot':self.truorfalse}
        self.worker = Worker(SaveToExcel,**self.kwargs)
      
        self.worker.finished.connect(self.complete)
        self.worker.start()
  
    def complete(self):
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Status")
        self.msg.setText("Import Done!")
        self.msg.exec()
        self.setWidgetsDisableorEnable([self.exportBtn,self.extensions],True)
        self.setWidgetsDisableorEnable(self.findChildren(QCheckBox),True)
        self.setWidgetsDisableorEnable(self.findChildren(QRadioButton),True)
        self.filename.setReadOnly(False)
        self.textinput.setReadOnly(False)        
        self.exportBtn.setText("Import Again")
     
       



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setWindowIcon(QIcon(os.path.join(basedir,'./images/window_icon.png')))
        self.setFixedSize(360,360)

        self.windowlist = []
        #create qwidget because can't add qlayout to mainwindow
        self.wid = QWidget()

        #set qwidget as centralwidget
        self.setCentralWidget(self.wid)
        
        #create layout
        self.layout = QVBoxLayout()
        self.button2 = QPushButton('Query Import')
        self.button2.setFont(QFont('SansSerif',10))
        self.layout.addWidget(self.button2,2)
        self.button2.clicked.connect(self.runBtn)
        
        #add layout to central widget
        self.wid.setLayout(self.layout)
       

    def closeEvent(self,event):
        event.accept()
    
    def runBtn(self):
          
           self.w = AnotherWindow('Query Import')
           self.windowlist.append(self.w)
           for w in reversed(self.windowlist):
               if w.isClosed == True:
                   self.windowlist.remove(w)
               else:
                   w.show()

     

app = QApplication([])
app.processEvents()
window = MainWindow()
window.show()

app.exec()