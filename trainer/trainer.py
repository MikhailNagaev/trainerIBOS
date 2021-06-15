import sys 
from PyQt5 import QtWidgets, QtCore, QtGui
from interfacePyQt import Ui_MainWindow 
import os
from PyDocker import *
import csv
import socket
import random
sys.path.append('/etc/trainerIBOS/script')
from Lab1res import *
from Lab2res import *
from Lab3res import *
from Lab4res import *
from Lab5res import *
from Lab6res import *


portProgramm = 0 

def TimeToAsk(question, procent):
    isx = procent
    text = '*** Ошибки ответов на вопросы ***\n'
    res = True
    num = 1
    amount_question = len(question)
    for que in question:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Вопрос №" + str(num))
        num = num + 1
        msgBox.setText(que[0])
        amount = len(que[1])
        que[1] = random.sample(que[1], amount)
        for i in range(amount):
            msgBox.addButton(que[1][i], i)
            if que[1][i] == que[2]:
                indexTrue = i
        
        returnValue = msgBox.exec()
        if returnValue != indexTrue:
            res = False
            text = text + 'Неверный ответ на вопрос: \"{}\". Правильный ответ {}.\n'. format(que[0], que[2])
            procent = procent - isx/amount_question
            
            
    code = 0 if res else 1
        
    return code, text, procent



class BrowserHandler(QtCore.QObject): # Поток, ждущий сообщений от скриптов проверки.
    running = False
    slot = QtCore.pyqtSignal(str)
    def run(self):
        global portProgramm
        sock = socket.socket()
        sock.bind(('localhost', portProgramm))
        sock.listen(1)
        conn, addr = sock.accept()
        while True:
            data = conn.recv(1024)
            self.slot.emit(data.decode())
            conn, addr = sock.accept()
        conn.close() 



class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow): # Класс приложения
    def __init__(self):
       
        
        super().__init__()                 
        #ПРОВЕРКА =========== 
        lst_error = CheckImages()
        if len(lst_error) != 0:
            reply = QtWidgets.QMessageBox.question(self, 'Внимание!', "Было обнаружено что отсутствуют или не совпадают контрольные суммы следующих образов:\n{}\nНажмите да, чтобы провести автоматическое восстановление.\nНажмите нет,чтобы провести восстановление вручную.".format('\n'.join(lst_error)), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                QtWidgets.QMessageBox.question(self, 'Ожидание', "Нажмите OK и ожидайте, когда пройдет процесс восстановления.", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                resultLoad = LoadImages()
                lst_error = CheckImages()
                if resultLoad == 0 and len(lst_error) == 0:
                    QtWidgets.QMessageBox.question(self, 'Успех', "Docker-образы успешно восстановлены!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                else:
                    QtWidgets.QMessageBox.question(self, 'Неудача', "Следующие Docker-образы не были восстановлены:\n{}\nВосстановите их вручную или создайте новые из Dockerfile. Проверьте контрольные суммы.".format('\n'.join(lst_error)), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    sys.exit(0)
                    
            else:
                sys.exit(0)
                
        self.setupUi(self)
        self.pushButton.clicked.connect(self.GoToKnow)   # Задание нажатия на кнопку 
        self.comboBox.activated[int].connect(self.onChanged)      # Задание вывода при выборе в комбобокс
        self.pushButton_2.clicked.connect(self.EndLab)
        
        self.modeExam = []

        self.comboBox.activated[int].connect(self.EditTime)
        self.radioButton_7.toggled.connect(self.EditTime)
        self.radioButton_8.toggled.connect(self.EditTime)
        self.radioButton_9.toggled.connect(self.EditTime)
        self.radioButton_12.toggled.connect(self.GoToExam)  
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerShow)
        self.EditTime()
        self.Working = False
        
        
        self.action.triggered.connect(self.msgHelp)
        
        
        
        self.timerChekExam = QtCore.QTimer()
        self.timerChekExam.timeout.connect(self.timerEventCheckExam)
        self.timerChekExam.start(3500)
        global portProgramm
        
        try:
            os.mkdir('/tmp/trainerIBOS')
        except FileExistsError:
            pass
        
        with open('/tmp/trainerIBOS/runningtrainer.conf', 'w') as running:
            running.write('{} {}'.format(os.getlogin(), QtCore.QTime.currentTime().toString("hh:mm")))
        
        
        if os.path.exists('/tmp/trainerIBOS/exam.conf'):
            os.remove('/tmp/trainerIBOS/exam.conf')
        
        
        self.radioButton_12.setEnabled(False) #--------------------------------------------------------------------------------------------------------------------
        self.dictMessage = {} # Словарь для кодов сообщений
        self.timerKforFiles = []
        with open('/etc/trainerIBOS/port_time.conf', 'r') as FileTime:
            portProgramm = int(FileTime.readline())
            for i in FileTime:
                self.timerKforFiles.append(list(map(lambda x: int(x),i.split()[1:])))
        
        self.textEdit.setFont(QtGui.QFont ("Courier", 10))
        
        #------------------------------------------Создание потока
        self.thread = QtCore.QThread()
        self.browserHandler = BrowserHandler()
        self.browserHandler.moveToThread(self.thread)
        self.browserHandler.slot.connect(self.EnterCode)
        self.thread.started.connect(self.browserHandler.run)
        self.thread.start()
        #------------------------------------------Создание потока
       
        
        
        with open('/etc/trainerIBOS/desc/Lab1/Lab1-Desc.conf', 'r') as DesFile, open('/etc/trainerIBOS/desc/Lab1/Lab1-Code.conf', 'r') as CodeFile:  # Выбор первой лабы
                self.label_2.setText(DesFile.read())
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()

    
    def GoToExam(self):
        if self.radioButton_12.isChecked():
            self.groupBox_4.setEnabled(False)
            if 'a1' not in self.modeExam:
                self.radioButton_4.setEnabled(False)
            if 'a2' not in self.modeExam:
                self.radioButton_5.setEnabled(False)
            if 'a3' not in self.modeExam:
                self.radioButton_6.setEnabled(False)
            if 'b1' not in self.modeExam:
                self.radioButton_7.setEnabled(False)
            if 'b2' not in self.modeExam:
                self.radioButton_8.setEnabled(False)
            if 'b3' not in self.modeExam:
                self.radioButton_9.setEnabled(False)
            
            if self.radioButton_4.isEnabled():
                self.radioButton_4.setChecked(True)
            elif self.radioButton_5.isEnabled():
                self.radioButton_5.setChecked(True)
            else:
                self.radioButton_6.setChecked(True)
            if self.radioButton_7.isEnabled():
                self.radioButton_7.setChecked(True)
            elif self.radioButton_8.isEnabled():
                self.radioButton_8.setChecked(True)
            else:
                self.radioButton_9.setChecked(True)
            
            self.modeExam = []


	
    def GoToKnow(self): # Слот, выполняющийся при нажати на кнопку
        task = self.comboBox.currentIndex() # Получить индекс выбора и запустить соответствующую лабу
        if task == 5:
            self.radioButton_5.setChecked(True)
        
        self.timeStart = QtCore.QTime.currentTime()
        self.messageScriptCheck = []
        self.dictMessage = {}
        # Выбор уровня сложности
        if self.radioButton_4.isChecked():
            diff = 0
        elif self.radioButton_5.isChecked():
            diff = 1
        elif self.radioButton_6.isChecked():
            diff = 2
        
        train = True if self.radioButton_10.isChecked() else False
        self.Working = True
        
        
        if task == 0:
            deskLab = startTaskControlUserAndGroup(diff, train)
            with open('/etc/trainerIBOS/desc/Lab1/Lab1-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab1/Lab1-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        elif task == 1:
            deskLab = startChmodLab(diff, train)
            with open('/etc/trainerIBOS/desc/Lab2/Lab2-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab2/Lab2-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        elif task == 2:
            deskLab = startSystemdLab(diff, train)
            with open('/etc/trainerIBOS/desc/Lab3/Lab3-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab3/Lab3-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        elif task == 3:
            deskLab = startNetworkLab(diff, train)
            with open('/etc/trainerIBOS/desc/Lab4/Lab4-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab4/Lab4-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        elif task == 4:
            deskLab = startJournalLab(diff, train)
            with open('/etc/trainerIBOS/desc/Lab5/Lab5-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab5/Lab5-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        elif task == 5:
            deskLab = startSSHLab(diff, train)
            with open('/etc/trainerIBOS/desc/Lab6/Lab6-Code.conf', 'r') as CodeFile, open('/etc/trainerIBOS/desc/Lab6/Lab6-Hint.conf', 'r') as FileHint:
                for line in CodeFile:
                    x = line.split('=')
                    self.dictMessage[x[0]]=x[1].rstrip()
                hint = FileHint.read()
        
        # Вывести соответствующую информацию на экран
        self.textEdit.setText('')
        if self.radioButton_10.isChecked():
            self.textEdit.setText(hint)
        self.textEdit.append(deskLab)
        self.textEdit.append('')
        
        self.appEnabled(False)     # Выключить функционал    
        if not self.radioButton_7.isChecked(): # Запускаем таймер подсчета если нужно
            self.timer.start(1000)     # Запустить таймер
            self.time1 = QtCore.QTime(0,0,0)
      
    def onChanged(self, idexLab): # Вывод информации о содержании работы при выборе в комбобоксе
        if idexLab == 0:
            with open('/etc/trainerIBOS/desc/Lab1/Lab1-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())
        elif idexLab == 1:
            with open('/etc/trainerIBOS/desc/Lab2/Lab2-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())
        elif idexLab == 2:
            with open('/etc/trainerIBOS/desc/Lab3/Lab3-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())
        elif idexLab == 3:
            with open('/etc/trainerIBOS/desc/Lab4/Lab4-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())
        elif idexLab == 4:
            with open('/etc/trainerIBOS/desc/Lab5/Lab5-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())
        elif idexLab == 5:
            with open('/etc/trainerIBOS/desc/Lab6/Lab6-Desc.conf', 'r') as DesFile:
                self.label_2.setText(DesFile.read())

    #------------------------------------------Обработка текста из второго потока
    @QtCore.pyqtSlot(str)
    def EnterCode(self, mess):  
        if mess not in self.messageScriptCheck:
            self.messageScriptCheck.append(mess)
            if self.radioButton_10.isChecked():
                self.textEdit.append(self.dictMessage[mess])   
    #------------------------------------------Обработка текста из второго потока
    #------------------------------------------Функция выключения функционала
    def appEnabled(self, w):
        self.comboBox.setEnabled(w)
        self.groupBox_4.setEnabled(w)
        self.radioButton_4.setEnabled(w)
        self.radioButton_5.setEnabled(w)
        self.radioButton_6.setEnabled(w)
        self.radioButton_7.setEnabled(w)
        self.radioButton_8.setEnabled(w)
        self.radioButton_9.setEnabled(w)
        
        self.pushButton.setEnabled(w)
        self.pushButton_2.setEnabled(not w)
    #------------------------------------------Функция выключения функционала
    def timerShow(self): # Показ таймера
        self.time1 = self.time1.addSecs(1)
        self.label_3.setText('Текущее время: ' + self.time1.toString("hh:mm:ss"))
        if self.time1 == self.time2:
            self.textEdit.append('Время закончилось!')
            self.EndLab()
        

    def EditTime(self): # Изменение времени выполнения
        task = self.comboBox.currentIndex()
        if self.radioButton_7.isChecked():
            check = 0
        elif self.radioButton_8.isChecked():
            check = 1
        elif self.radioButton_9.isChecked():
            check = 2
        if check == 0:
            self.label_3.setText('Выполнение без учета времени')
            self.label_4.setText('')
        else:
            self.label_3.setText('Текущее время: ')
            minute =  self.timerKforFiles[task][check - 1] % 60
            hours = self.timerKforFiles[task][check - 1] // 60
            self.time2 = QtCore.QTime(hours,minute,0)
            self.label_4.setText('Времени на работу: ' + self.time2.toString("hh:mm:ss"))

    def EndLab(self):
        self.Working = False
        self.timer.stop()   
        task = self.comboBox.currentIndex()
        if task == 0:
            codeLab, text, procent = checkLab1()
        elif task == 1:
            codeLab, text, procent = checkLab2()
        elif task == 2:
            codeLab, text, procent = checkLab3()
        elif task == 3:
            codeLab, text, procent = checkLab4()
        elif task == 4:
            codeLab, text, procent = checkLab5()
        elif task == 5:
            codeLab, text, procent = checkLab6()
        
        train = True if self.radioButton_10.isChecked() else False   
        if task == 0:
            killTaskControlUserAndGroup(train)
        elif task == 1:
            dopProcent, que = killChmodLab(train)
            codeLabDop, textDop, procentDop = TimeToAsk(que, dopProcent)
            codeLab = codeLab + codeLabDop; text = text + textDop; procent = procent + procentDop
        elif task == 2:
            dopProcent, que = killSystemdLab(train)
            codeLabDop, textDop, procentDop = TimeToAsk(que, dopProcent)
            codeLab = codeLab + codeLabDop; text = text + textDop; procent = procent + procentDop
        elif task == 3:
            dopProcent, que = killNetworkLab(train)
            codeLabDop, textDop, procentDop = TimeToAsk(que, dopProcent)
            codeLab = codeLab + codeLabDop; text = text + textDop; procent = procent + procentDop
        elif task == 4:
            dopProcent, que = killJournalLab(train)
            codeLabDop, textDop, procentDop = TimeToAsk(que, dopProcent)
            codeLab = codeLab + codeLabDop; text = text + textDop; procent = procent + procentDop
        elif task == 5:
            dopProcent, que = killSSHLab(train)
            codeLabDop, textDop, procentDop = TimeToAsk(que, dopProcent)
            codeLab = codeLab + codeLabDop; text = text + textDop; procent = procent + procentDop
           
        
        
        
        
        if codeLab == 0:
            self.textEdit.append('Работа выполнена верно')
        else:
            self.textEdit.append('Вы ошиблись. Работа выполнена НЕ верно! Работа завершена на {} %.'.format(round(procent)))
            self.textEdit.append(text)
        if not self.radioButton_7.isChecked():
            self.textEdit.append('Время работы: ' + self.time1.toString("hh:mm:ss"))
        self.appEnabled(True)
        
        if self.radioButton_12.isChecked():
            if self.radioButton_4.isChecked():
                diffS = 'Простой уровень'
            elif self.radioButton_5.isChecked():
                diffS = 'Нормальный уровень'
            elif self.radioButton_6.isChecked():
                diffS = 'Сложный уровень'
            if self.radioButton_7.isChecked():
                timeS = 'Без учета времени'
            elif self.radioButton_8.isChecked():
                timeS = 'Норматив по времени'
            elif self.radioButton_9.isChecked():
                timeS = 'Уменьшенное время'
            if codeLab == 0:
                resString = 'Выполнена успешно'
            else:
                resString = '{}% выполнено'.format(round(procent))
            if self.radioButton_7.isChecked():
                dictResult = [os.getlogin(),QtCore.QDate.currentDate().toString('dd.MM.yyyy dddd'), self.comboBox.currentIndex(), resString, diffS, timeS, self.timeStart.toString("hh:mm:ss"),QtCore.QTime.currentTime().toString("hh:mm:ss"), '']
            else:
                dictResult = [os.getlogin(),QtCore.QDate.currentDate().toString('dd.MM.yyyy dddd'), self.comboBox.currentIndex(),resString, diffS, timeS,self.timeStart.toString("hh:mm:ss"),QtCore.QTime.currentTime().toString("hh:mm:ss"),self.time2.toString("hh:mm:ss") ]
            
            with open('/etc/trainerIBOS/result.csv', 'a') as FileResult:
                csvwriter = csv.writer(FileResult)
                csvwriter.writerow(dictResult)
        
        
        if self.radioButton_12.isChecked():
            self.radioButton_12.setEnabled(False)
            self.radioButton_10.setChecked(True)
            
            
    def msgHelp(self, event):
        QtWidgets.QMessageBox.question(self, 'Помощь.', '''Тренировка - режим, в котором даются подсказки по выполнению работы. Также данный режим поддерживает информирование пользователя о завершении пунктов задания.
Самоконтроль - режим, в котором результаты приводятся после завершения работы.
Экзамен - режим, в котором результат приводяться после завершения работы. Результаты выполнения будут сохранены.
По умолчанию данный режим недоступен. Открывается преподавателем.
Для начала работы в выпадающем списке выберите необходимую тему, установите необходимые параметры, после чего нажмите на кнопку \"Начать выполнение задания\".
Для досрочного завершения работы нажмите на кнопку \"Завершить выполнение работы\"
ВАЖНО! Не закрывайте консоль в процессе выполнения работы. Если консоль будет закрыта, необходимо начать выполнение работы заново.
Желаем успеха в обучении!''', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            
    def closeEvent(self, event):
        if self.Working == True:
            QtWidgets.QMessageBox.question(self, 'Внимание', "Работа не завершена! Сначала завершите выполнение!", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            event.ignore() 
        else:
            reply = QtWidgets.QMessageBox.question(self, 'Внимание', "Вы уверены, что необходимо выйти?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                os.remove('/tmp/trainerIBOS/runningtrainer.conf')
                self.thread.exit()
                event.accept()
            else:
                event.ignore() 
         
    def timerEventCheckExam(self):
        if os.path.exists('/tmp/trainerIBOS/exam.conf'):
            with open('/tmp/trainerIBOS/exam.conf', 'r') as fileExam:
                for i in fileExam.read().rstrip().split(' '):
                    self.modeExam.append(i)
            self.radioButton_12.setEnabled(True)
            os.remove('/tmp/trainerIBOS/exam.conf')

def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp()   
    window.show()
    app.exec_()

if __name__ == '__main__':  
    main()  