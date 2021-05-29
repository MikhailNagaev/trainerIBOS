import os
import sys
import pickle
import subprocess
import docker
import re

clientDocker = docker.from_env()

def getIndexList(x, lst):
    for i in range(len(lst)):
        if x == lst[i]:
            return i
    return -1


def checkLab3():
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
    
    with open("/var/lib/docker/volumes/{}/_data/.bash_history".format(NAME_DOCKER_VM_VOLUME)) as gr, open('/tmp/trainerIBOS/trainerIBOS.task', 'rb') as task:
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
    if diff == 0:
        max_proc1 = 13
    elif diff == 1:
        max_proc1 = 10
    else:
        max_proc1 = 8
        
    procent = procent + max_proc1
    textError1 = '1. Ошибки проверки статуса служб:\n'
    lens = len(systemd_name)
    
    for i in range(2):
        if 'systemctl status {}'.format(systemd_name[i]) not in textBASH:
            procent = procent - max_proc1/lens
            textError1 = textError1 + 'Не был проверен статус службы {}\n'.format(systemd_name[i])
            res1=False
   
    for i in range(2, 4):
        if 'systemctl is-active {}'.format(systemd_name[i]) not in textBASH:
            procent = procent - max_proc1/lens
            textError1 = textError1 + 'Не была проверена активность службы {}\n'.format(systemd_name[i])
            res1=False
            
    for i in range(4, 6):
        if 'systemctl is-enabled {}'.format(systemd_name[i]) not in textBASH or 'systemctl is-failed {}'.format(systemd_name[i]) not in textBASH:
            procent = procent - max_proc1/lens
            textError1 = textError1 + 'Не была проверено автовыключение и/или корректность выполнения службы {}\n'.format(systemd_name[i])
            res1=False
   
   
   # -------------------- ПЕРВОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
   
   # -------------------- ВТОРОЕ ЗАДАНИЕ -----------------------------------------
    if diff == 0:
        max_proc2 = 14
    elif diff == 1:
        max_proc2 = 10
    else:
        max_proc2 = 9
    lens = len(type_unit) + 3
    
    procent = procent + max_proc2
    textError2 = '2. Ошибки обзора состояния системы:\n'
    if 'systemctl list-units' not in textBASH:
            procent = procent - max_proc2/lens
            textError2 = textError2 + 'Не был выведен список активных служб на экран.\n'
            res2=False
    if ('systemctl list-units -a' not in textBASH
    and 'systemctl list-units --all' not in textBASH
    and 'systemctl --all' not in textBASH
    and 'systemctl -a' not in textBASH
    and 'systemctl -a list-units' not in textBASH
    and 'systemctl --all list-units' not in textBASH):
            procent = procent - max_proc2/lens
            textError2 = textError2 + 'Не был выведен список всех служб на экран.\n'
            res2=False
    for i in range(2):
        if ('systemctl list-units -t {}'.format(type_unit[i]) not in textBASH
        and 'systemctl list-units --type {}'.format(type_unit[i]) not in textBASH
        and 'systemctl list-units --type={}'.format(type_unit[i]) not in textBASH
        and 'systemctl list-units -t={}'.format(type_unit[i]) not in textBASH
        and 'systemctl -t {} list-units'.format(type_unit[i]) not in textBASH
        and 'systemctl --type {} list-units'.format(type_unit[i]) not in textBASH):
            procent = procent - max_proc2/lens
            textError2 = textError2 + 'Не был выведен список активных служб типа {}.\n'.format(type_unit[i])
            res2=False
    if 'systemctl status' not in textBASH:
            procent = procent - max_proc2/lens
            textError2 = textError2 + 'Не были выведены зависимости служб на экран.\n'
            res2=False
   
   
   # -------------------- ВТОРОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
   
   # -------------------- ТРЕТЬЕ ЗАДАНИЕ -----------------------------------------
    if diff == 0:
        max_proc3 = 13
    elif diff == 1:
        max_proc3 = 10
    else:
        max_proc3 = 8
        
    procent = procent + max_proc3
    textError3 = '3. Ошибки работы со службами:\n'
    lens = 3
    
    if ('systemctl stop {}'.format(systemd_name[0]) not in textBASH
    or 'systemctl is-active {}'.format(systemd_name[0]) not in textBASH
    or 'systemctl start {}'.format(systemd_name[0]) not in textBASH):
        procent = procent - max_proc3/lens
        textError3 = textError3 + 'Не была проведена работа по отключению/проверке/запуску службы {}.\n'.format(systemd_name[0])
        res3=False
        
    if ('systemctl restart {}'.format(systemd_name[2]) not in textBASH
    or 'systemctl is-active {}'.format(systemd_name[2]) not in textBASH):
        procent = procent - max_proc3/lens
        textError3 = textError3 + 'Не была проведена работа по перезапуску и проверке службы {}.\n'.format(systemd_name[2])
        res3=False
        
    if ('systemctl disable {}'.format(systemd_name[4]) not in textBASH
    or 'systemctl is-enabled {}'.format(systemd_name[4]) not in textBASH
    or 'systemctl enable {}'.format(systemd_name[4]) not in textBASH):
        procent = procent - max_proc3/lens
        textError3 = textError3 + 'Не была проведена работа по отключению автовключения/проверке автовключения/запуску автовключения службы {}.\n'.format(systemd_name[4])
        res3=False
        
    # -------------------- ТРЕТЬЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    # -------------------- ЧЕТВЕРТОЕ ЗАДАНИЕ -----------------------------------------
    if diff == 0:
        max_proc4 = 30
    elif diff == 1:
        max_proc4 = 20
    else:
        max_proc4 = 15
    procent = procent + max_proc4
    textError4 = '4. Ошибки создания службы service:\n'
    resultStatus = container.exec_run('systemctl status TaskService.service')[1].decode().rstrip()
    if 'could not be found.' in resultStatus:
        res4=False
        textError4 = textError4 + 'Служба не найдена в системе systemd\n'
    else:
        resultStatus = resultStatus.split('\n')[0:3] + [resultStatus.split('\n')[7]]
        if ' loaded (/etc/systemd/system/TaskService.service;' not in resultStatus[1]:
            res4=False
            textError4 = textError4 + 'Юинт службы находится не в корректной папке.\n'
        if 'Active: active (running)' not in resultStatus[2]:
            res4=False
            textError4 = textError4 + 'Служба не активна.\n'
        elif '/mnt/programm1' not in resultStatus[3]:
            res4=False
            textError4 = textError4 + 'Служба запускает неверную программу.\n'
    resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
    if 'logs_programm1' in resultLs:
        resultCat = container.exec_run('cat /mnt/logs_programm1')[1].decode()
        if 'Programm working ' not in resultCat or ' seconds\n' not in resultCat:
            res4=False
            textError4 = textError4 + 'Файл logs_programm1 был создан не программой programm1.\n'
    else:
        textError4 = textError4 + 'Программа programm1 ни разу не была запущена службой.\n'
        res4=False
    if res4 == False:
        procent = procent - max_proc4
    
        
    
    # -------------------- ЧЕТВЕРТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    
    # -------------------- ПЯТОЕ ЗАДАНИЕ -----------------------------------------
    if diff >= 1: 
        max_proc5 = 20
        if diff == 2:
            max_proc5 = 15
        
        procent = procent + max_proc5
        textError5 = '5. Ошибки создания юнита timer:\n'
        
        resultStatus = container.exec_run('systemctl status TaskTimer.timer')[1].decode().rstrip()
        
        if 'could not be found.' in resultStatus:
            res5=False
            textError5 = textError5 + 'Юнит .timer не найдена в системе systemd\n'
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskTimer.timer;' not in resultStatus[1]:
                res5=False
                textError5 = textError5 + 'Юинт службы находится не в корректной папке.\n'
            if 'Active: active (running)' not in resultStatus[2] and 'Active: active (waiting)' not in resultStatus[2]:
                res5=False
                textError5 = textError5 + 'Юнит .timer не активна.\n'
            resultCat = container.exec_run('systemctl cat TaskTimer.timer')[1].decode().rstrip()
            if 'OnCalendar=*:*:0/10' not in resultCat:
                res5=False
                textError5 = textError5 + 'Неверно настроен юнит .timer. Необходимо, чтобы .service запускался каждые 20 секунд.\n'
    
        resultStatus = container.exec_run('systemctl status TaskTimer.service')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res5=False
            textError5 = textError5 + 'Юнит .service не найдена в системе systemd\n'
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskTimer.service;' not in resultStatus[1]:
                res5=False
                textError5 = textError5 + 'Юинт службы .service находится не в корректной папке.\n'
            if 'Active: active (running)' not in resultStatus[2] and 'Active: inactive (dead) since' not in resultStatus[2]:
                res5=False
                textError5 = textError5 + 'Служба .service не была запущена ни разу.\n'
            resultCat = container.exec_run('systemctl cat TaskTimer.service')[1].decode().rstrip()
            if '/mnt/programm2' not in resultCat:
                res5=False
                textError5 = textError5 + 'Неверно настроен юнит .service. Необходимо, чтобы .service запускал программу /mnt/programm2.\n'
    
    
    
        resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
        if 'logs_programm2' in resultLs:
            resultCat = container.exec_run('cat /mnt/logs_programm2')[1].decode()
            if 'Timer tick: ' not in resultCat:
                res5=False
                textError5 = textError5 + 'Файл logs_programm2 был создан не программой programm2.\n'
        else:
            textError5 = textError5 + 'Программа programm2 ни разу не была запущена службой.\n'
            res5=False
    
        if res5 == False:
            procent = procent - max_proc5
    
    # -------------------- ПЯТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    # -------------------- ШЕСТОЕ ЗАДАНИЕ -----------------------------------------
    if diff == 2: 
        max_proc6 = 15
        procent = procent + max_proc6
        
        textError6 = '6. Ошибки создания юнита path:\n'
        
        resultStatus = container.exec_run('systemctl status TaskPath.path')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res6=False
            textError6 = textError6 + 'Юнит .path не найдена в системе systemd\n'
        else:
            resultStatus = resultStatus.split('\n')
            if ' loaded (/etc/systemd/system/TaskPath.path;' not in resultStatus[1]:
                res6=False
                textError6 = textError6 + 'Юинт службы находится не в корректной папке.\n'
            if 'Active: active (waiting) since' not in resultStatus[2]:
                res6=False
                textError6 = textError6 + 'Юнит .path не активен.\n'
            resultCat = container.exec_run('systemctl cat TaskPath.path')[1].decode().rstrip()
            if '/mnt/text.txt' not in resultCat:
                res6=False
                textError6 = textError6 + 'Юнит .path не следит за файлом /mnt/text.txt.\n'
            else:
                resultListCat = resultCat.split('\n')
                index = -1
                for i in range(len(resultListCat)):
                    if '/mnt/text.txt' in resultListCat[i]:
                        index = i
                        break
                if 'PathChanged' not in resultListCat[index] and 'PathModified' not in resultListCat[index]:
                    res6=False
                    textError6 = textError6 + 'Неверно настроен юнит .path. Необходимо, чтобы .service запускался при изменении файла /mnt/text.txt.\n'
        
        
        resultStatus = container.exec_run('systemctl status TaskPath.service')[1].decode().rstrip()
        if 'could not be found.' in resultStatus:
            res6=False
            textError6 = textError6 + 'Юнит .service не найдена в системе systemd\n'
        else:
            resultStatus = resultStatus.split('\n')[0:3]
            if ' loaded (/etc/systemd/system/TaskPath.service;' not in resultStatus[1]:
                res6=False
                textError6 = textError6 + 'Юинт службы .service находится не в корректной папке.\n'
            if 'Active: active (running)' not in resultStatus[2] and 'Active: inactive (dead)' not in resultStatus[2]:
                res6=False
                textError6 = textError6 + 'Служба .service не была запущена ни разу.\n'
            resultCat = container.exec_run('systemctl cat TaskPath.service')[1].decode().rstrip()
            if '/mnt/programm3' not in resultCat:
                res6=False
                textError6 = textError6 + 'Неверно настроен юнит .service. Необходимо, чтобы .service запускал программу /mnt/programm3.\n'
                
        resultLs = container.exec_run('ls /mnt')[1].decode().split('\n')
        if 'logs_programm3' in resultLs:
            resultCat = container.exec_run('cat /mnt/logs_programm3')[1].decode()
            if 'File /mnt/text.txt has changed! Time:' not in resultCat:
                res6=False
                textError6 = textError6 + 'Файл logs_programm3 был создан не программой programm3.\n'
        else:
            textError6 = textError6 + 'Программа programm3 ни разу не была запущена службой.\n'
            res6=False
            
        if res6 == False:
            procent = procent - max_proc6
    
    # -------------------- ШЕСТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    if res1 == False:
        textError = textError + textError1
    if res2 == False:
        textError = textError + textError2
    if res3 == False:
        textError = textError + textError3
    if res4 == False:
        textError = textError + textError4
    if res5 == False:
        textError = textError + textError5
    if res6 == False:
        textError = textError + textError6
    
    #print(textError)
    #print(res1, res2, res3, res4, res5, res6)
    if res1 and res2 and res3 and res4 and res5 and res6:
        codeLab = 0
    else:
        codeLab = 1
    
    return codeLab, textError, procent
    
    
if __name__ == '__main__':  
    checkLab3()  
    
    

    
    
    
    
    
    
    