import sys
import os
from math import ceil
from PyQt5 import QtWidgets, QtCore
from FormsTutor import Ui_mainWindow  
import csv
import socket
import paramiko 
from scp import SCPClient


class ExampleApp(QtWidgets.QMainWindow, Ui_mainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        try:
            os.mkdir('/tmp/trainerIBOStutor')
        except FileExistsError:
            pass
        self.pushButton.clicked.connect(self.ShowsResult)  
        self.pushButton_3.clicked.connect(self.ShowTrainer) 
        self.pushButton_2.clicked.connect(self.ToGoExam)
        
        self.checkBox.toggled.connect(self.checkBoxMethod1)
        self.checkBox_2.toggled.connect(self.checkBoxMethod1)
        self.checkBox_3.toggled.connect(self.checkBoxMethod1)
        
        self.checkBox_4.toggled.connect(self.checkBoxMethod2)
        self.checkBox_5.toggled.connect(self.checkBoxMethod2)
        self.checkBox_6.toggled.connect(self.checkBoxMethod2)
        
        self.tableWidget.setShowGrid(True)
        self.fileName = ''
        with open('/etc/trainerIBOStutor/tutorset.conf', 'r') as f:
            f.readline()
            for line in f:
                self.listWidget.addItem(line.rstrip())                                      

  
    def ShowTrainer(self):
        hosts = [i.text() for i in self.listWidget.selectedItems()]
        if len(hosts)>0:
            self.listWidget_2.clear()
            timeout = self.doubleSpinBox.value()/1000
            port = 22
            QtWidgets.QMessageBox.question(self, 'Внимание', "Проверка может занять до {} секунд! Дождитесь сообщения об завершении.".format(ceil(timeout*len(hosts))), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            for host in hosts:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(hostname=host, username='root', port=port)
                    stdin, stdout, stderr = ssh.exec_command('ls /tmp/trainerIBOS')
                    txt = ''
                    if 'runningtrainer.conf\n' in stdout.readlines():
                        stdin, stdout, stderr = ssh.exec_command('cat /tmp/trainerIBOS/runningtrainer.conf')
                        txt = stdout.readlines()[0]
                        self.listWidget_2.addItem(host + ' ' + txt)
                    else:
                        continue
                except:
                    pass
            QtWidgets.QMessageBox.question(self, 'Внимание', "Доступные компьютеры отображены.", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.question(self, 'Внимание', "Необходимо выбрать компьютеры!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        


    def ShowsResult(self):
        hosts = [i.text().split()[0] for i in self.listWidget_2.selectedItems()]
        user = 'root'
        port = 22
        ListResult = []
        timeout = self.doubleSpinBox.value()/1000
        self.tableWidget.setSortingEnabled(False)
        amountRow = 0
        for host in hosts:
            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.settimeout(timeout)
                conn.connect((host, port))
                conn.close()
            except:
                continue
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=user, port=port)
            stdin, stdout, stderr = ssh.exec_command('ls /etc/trainerIBOS/')
            if 'result.csv\n' in stdout.readlines():
                scp = SCPClient(ssh.get_transport())
                scp.get('/etc/trainerIBOS/result.csv', '/tmp/trainerIBOStutor/result.csv')
                with open('/tmp/trainerIBOStutor/result.csv', 'r') as fileResult:
                    csvreader = csv.reader(fileResult)
                    for i in csvreader:
                        amountRow += 1
                        ListResult.append(i)
                        self.tableWidget.setRowCount(amountRow)
            ssh.close()
        self.tableWidget.setRowCount(amountRow)
        for i in range(amountRow):
            for j in range(len(ListResult[0])):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(ListResult[i][j]))
        self.tableWidget.setSortingEnabled(True)

    
    
    
    def ToGoExam(self):
        hosts = [i.text().split()[0] for i in self.listWidget_2.selectedItems()]
        user = 'root'
        port = 22
        ListResult = []
        amountRow = 0
        with open('/tmp/trainerIBOStutor/exam.conf', 'w') as examFile:
            if self.checkBox.isChecked():
                examFile.write('a1 ')
            if self.checkBox_2.isChecked():
                examFile.write('a2 ')
            if self.checkBox_3.isChecked():
                examFile.write('a3 ')
            if self.checkBox_4.isChecked():
                examFile.write('b1 ')
            if self.checkBox_5.isChecked():
                examFile.write('b2 ')
            if self.checkBox_6.isChecked():
                examFile.write('b3 ')
        for host in hosts:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=host, username=user, port=port)
                
                stdin, stdout, stderr = ssh.exec_command('ls /tmp/trainerIBOS')
                txt = ''
                if 'runningtrainer.conf\n' not in stdout.readlines():
                    QtWidgets.QMessageBox.question(self, 'Внимание', "Тренажер на хосте {} не запущен.".format(host), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    continue
                
                scp = SCPClient(ssh.get_transport())
                scp.put('/tmp/trainerIBOStutor/exam.conf', '/tmp/trainerIBOS/exam.conf')
                ssh.close()
            except:
                continue
        os.remove('/tmp/trainerIBOStutor/exam.conf')
        
        
    def checkBoxMethod1(self):
        if not self.checkBox.isChecked() and not self.checkBox_2.isChecked() and not self.checkBox_3.isChecked():
            QtWidgets.QMessageBox.question(self, 'Внимание', "Хотя бы один режим сложности должен быть выбран!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            self.checkBox.setChecked(True)
            self.checkBox_2.setChecked(True)
            self.checkBox_3.setChecked(True)
    
    def checkBoxMethod2(self):
        if not self.checkBox_4.isChecked() and not self.checkBox_5.isChecked() and not self.checkBox_6.isChecked():
            QtWidgets.QMessageBox.question(self, 'Внимание', "Хотя бы один временной режим должен быть выбран!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            self.checkBox_4.setChecked(True)
            self.checkBox_5.setChecked(True)
            self.checkBox_6.setChecked(True)
    
    
def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp()  
    window.show()  
    app.exec_()  

if __name__ == '__main__':  
    main()  