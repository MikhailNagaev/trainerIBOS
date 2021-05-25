import os
import sys
import pickle
import subprocess
import docker
import re
import socket

with open('/etc/trainerIBOS/port_time.conf', 'r') as f:
    portProgramm = int(f.readline())

clientDocker = docker.from_env()

def getIndexList(x, lst):
    for i in range(len(lst)):
        if x == lst[i]:
            return i
    return -1


def checkLab3Hint():
    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    # Суммарно 70
    res1 = True # 13 10 8
    res2 = True # 14 10 9
    res3 = True # 13 10 8
    res4 = True # 30 20 15
    res5 = True #    20 15
    res6 = True #       15
    
    amount = 0
    procent = 0.0
    container = clientDocker.containers.get('trainerIBOS')
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    
    with open("/var/lib/docker/volumes/{}/_data/.bash_history".format(NAME_DOCKER_VM_VOLUME)) as gr, open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        diff = data[0]
        systemd_name = data[1]
        systemd_nameOFdesc = data[2]
        type_unit = data[3]
        if len(data) > 4:
            ready = data[4]
        textBASH = []
        for line in gr:
            if 'systemctl' in line:
                textBASH.append(re.sub(r'\s+', ' ', line.rstrip()))
    
    
    #print(textBASH)
    # -------------------- ПЕРВОЕ ЗАДАНИЕ -----------------------------------------
    lens = len(systemd_name)
    
    for i in range(2):
        if 'systemctl status {}'.format(systemd_name[i]) not in textBASH:
            res1=False
   
    for i in range(2, 4):
        if 'systemctl is-active {}'.format(systemd_name[i]) not in textBASH:
            res1=False
            
    for i in range(4, 6):
        if 'systemctl is-enabled {}'.format(systemd_name[i]) not in textBASH or 'systemctl is-failed {}'.format(systemd_name[i]) not in textBASH:
            res1=False
   
   
   # -------------------- ПЕРВОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
   
   # -------------------- ВТОРОЕ ЗАДАНИЕ -----------------------------------------
    lens = len(type_unit) + 3
    if 'systemctl list-units' not in textBASH:
            res2=False
    if ('systemctl list-units -a' not in textBASH
    and 'systemctl list-units --all' not in textBASH
    and 'systemctl -a list-units' not in textBASH
    and 'systemctl --all list-units' not in textBASH):
            res2=False
    for i in range(2):
        if ('systemctl list-units -t {}'.format(type_unit[i]) not in textBASH
        and 'systemctl list-units --type {}'.format(type_unit[i]) not in textBASH
        and 'systemctl -t {} list-units'.format(type_unit[i]) not in textBASH
        and 'systemctl --type {} list-units'.format(type_unit[i]) not in textBASH):
            res2=False
    if 'systemctl status' not in textBASH:
            res2=False
   
   
   # -------------------- ВТОРОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
   
   # -------------------- ТРЕТЬЕ ЗАДАНИЕ -----------------------------------------
    lens = 3
    
    if ('systemctl stop {}'.format(systemd_name[0]) not in textBASH
    or 'systemctl is-active {}'.format(systemd_name[0]) not in textBASH
    or 'systemctl start {}'.format(systemd_name[0]) not in textBASH):
        res3=False
        
    if ('systemctl restart {}'.format(systemd_name[2]) not in textBASH
    or 'systemctl is-active {}'.format(systemd_name[2]) not in textBASH):
        res3=False
        
    if ('systemctl disable {}'.format(systemd_name[4]) not in textBASH
    or 'systemctl is-enabled {}'.format(systemd_name[4]) not in textBASH
    or 'systemctl enable {}'.format(systemd_name[4]) not in textBASH):
        res3=False
        
    # -------------------- ТРЕТЬЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    # -------------------- ЧЕТВЕРТОЕ ЗАДАНИЕ -----------------------------------------
    
    resultStatus = container.exec_run('systemctl status TaskService.service')[1].decode().rstrip()
    if 'could not be found.' in resultStatus:
        res4=False
    else:
        resultStatus = resultStatus.split('\n')[0:3] + [resultStatus.split('\n')[7]]
        if ' loaded (/etc/systemd/system/TaskService.service;' not in resultStatus[1]:
            res4=False
        if 'Active: active (running)' not in resultStatus[2]:
            res4=False
        elif '/mnt/programm1' not in resultStatus[3]:
            res4=False
    resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
    if 'logs_programm1' in resultLs:
        resultCat = container.exec_run('cat /mnt/logs_programm1')[1].decode()
        if 'Programm working ' not in resultCat or ' seconds\n' not in resultCat:
            res4=False
    else:
        res4=False
    
        
    
    # -------------------- ЧЕТВЕРТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    
    # -------------------- ПЯТОЕ ЗАДАНИЕ -----------------------------------------
    if diff >= 1: 
        
        resultStatus = container.exec_run('systemctl status TaskTimer.timer')[1].decode().rstrip()
        
        if 'could not be found.' in resultStatus:
            res5=False
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskTimer.timer;' not in resultStatus[1]:
                res5=False
            if 'Active: active (running)' not in resultStatus[2] and 'Active: active (waiting)' not in resultStatus[2]:
                res5=False
            resultCat = container.exec_run('systemctl cat TaskTimer.timer')[1].decode().rstrip()
            if 'OnCalendar=*:*:0/10' not in resultCat:
                res5=False
    
        resultStatus = container.exec_run('systemctl status TaskTimer.service')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res5=False
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskTimer.service;' not in resultStatus[1]:
                res5=False
            if 'Active: active (running)' not in resultStatus[2] and 'Active: inactive (dead) since' not in resultStatus[2]:
                res5=False
            resultCat = container.exec_run('systemctl cat TaskTimer.service')[1].decode().rstrip()
            if '/mnt/programm2' not in resultCat:
                res5=False
    
        resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
        if 'logs_programm2' in resultLs:
            resultCat = container.exec_run('cat /mnt/logs_programm2')[1].decode()
            if 'Timer tick: ' not in resultCat:
                res5=False
        else:
            res5=False
    
    
    # -------------------- ПЯТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    # -------------------- ШЕСТОЕ ЗАДАНИЕ -----------------------------------------
    if diff == 2: 
        resultStatus = container.exec_run('systemctl status TaskPath.path')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res6=False
        else:
            resultStatus = resultStatus.split('\n')
            if ' loaded (/etc/systemd/system/TaskPath.path;' not in resultStatus[1]:
                res6=False
            if 'Active: active (waiting) since' not in resultStatus[2]:
                res6=False
            resultCat = container.exec_run('systemctl cat TaskPath.path')[1].decode().rstrip()
            if '/mnt/text.txt' not in resultCat:
                res6=False
            else:
                resultListCat = resultCat.split('\n')
                index = -1
                for i in range(len(resultListCat)):
                    if '/mnt/text.txt' in resultListCat[i]:
                        index = i
                        break
                if 'PathChanged' not in resultListCat[index] and 'PathModified' not in resultListCat[index]:
                    res6=False
        
        resultStatus = container.exec_run('systemctl status TaskPath.service')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res6=False
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskPath.service;' not in resultStatus[1]:
                res6=False
            if 'Active: active (running)' not in resultStatus[2] and 'Active: inactive (dead)' not in resultStatus[2]:
                res6=False
            resultCat = container.exec_run('systemctl cat TaskPath.service')[1].decode().rstrip()
            if '/mnt/programm3' not in resultCat:
                res6=False
                
        resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
        if 'logs_programm3' in resultLs:
            resultCat = container.exec_run('cat /mnt/logs_programm3')[1].decode()
            if 'File /mnt/text.txt has changed! Time:' not in resultCat:
                res6=False
        else:
            res6=False
            
    # -------------------- ШЕСТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    print(res1, res2, res3, res4, res5, res6)
    if res1:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-1')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-2')
        sock.close() # Отправляяет соответствующее сообщение основной программе

    if res3:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-3')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res4:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-4')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res5 and diff > 0:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-5')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res6 and diff == 2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab3-6')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    
    
if __name__ == '__main__':  
    checkLab3Hint()  
    
    

    
    
    
    
    
    
    