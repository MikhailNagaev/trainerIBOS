import os
import sys
import pickle
import subprocess
import docker
import re

clientDocker = docker.from_env()



def checkLab6():
    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    #----------------------60 - Максимум!!!!!!!!!!!!!!!!!!!!!!!!
    
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    NAME_DOCKER_VM_VOLUME2 = 'trainerIBOS_VOLUME2'
    
    with open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        userMain = data[0]
        userSecond = data[1]
        fraze = data[2]
    
    with open("/etc/trainerIBOS/desc/Lab6/scp-file", 'r') as scpF:
        textSCP = scpF.read()
    
    res1 = False
    res2 = True
    try:
        with open("/var/lib/docker/volumes/{}/_data/{}/.bash_history".format(NAME_DOCKER_VM_VOLUME2, userMain)) as grMain:
            for line in grMain:
                if 'scp' in line and '/home/scp-file' in line and '{}@'.format('root') in line:
                    res1=True
                    break
    except:
        pass
    textSCPtmp = 'abc'
    try:
        with open("/var/lib/docker/volumes/{}/_data/scp-file".format(NAME_DOCKER_VM_VOLUME)) as grSecond:
            textSCPtmp = grSecond.read()
    except:
        res2 = False
        
    if textSCP != textSCPtmp:
        res2 = False
    
    
    frazeTMP = '-0-'
    res3 = False
    try:
        with open("/var/lib/docker/volumes/{}/_data/MyPhrase.txt".format(NAME_DOCKER_VM_VOLUME)) as grSecond:
            frazeTMP = grSecond.read()
    except:
        pass
        
    if frazeTMP.rstrip() ==fraze:
        res3 = True    
            
    
    procent = 60
    textError = 'Ошибки выполнения работы: \n'
    
    contSecond = clientDocker.containers.get('trainerIBOS')
    contMain = clientDocker.containers.get('IBOStrainer')
    
    result = contMain.exec_run('cat /etc/passwd')[1].decode()
    if '{}:'.format(userMain) not in result:
        textError = textError + 'Не был создан пользователь {} на основной машине.\nИз-за этого все остальные действия выполнялись не в сессии данного пользователя. Работа аннулирована.\n'.format(userMain)
        procent = 0
        
    result = contSecond.exec_run('cat /etc/passwd')[1].decode()
    if '{}:'.format(userSecond) not in result:
        textError = textError + 'Не был создан пользователь {} на удаленной машине.\nИз-за этого все остальные действия не могли быть выполнены корректно. Работа аннулирована.\n'.format(userSecond)
        procent = 0
    if res1 == False or res2 == False:
        textError = textError + 'Не была использована команда scp для копирования файла /home/scp-file на удаленную машину. Либо сам файл не соответствует оригиналу.\n'
        procent -= 10
        
    if res3 == False:
        textError = textError + 'На удаленной машине не был создан файл /home/MyPhrase.txt с следующим текстом: "{}".\n'.format(fraze)
        procent -= 15
    
    result = contMain.exec_run('ls /home/{}/.ssh'.format(userMain))[1].decode()
    
    if 'id_rsa' not in result or 'id_rsa.pub' not in result:
        textError = textError + 'Не была настроена автоматическая ssh-аутентификация по ключам. (Основная машина)\n'
        procent -= 20
        
    result = contSecond.exec_run('ls /home/{}/.ssh'.format(userSecond))[1].decode()
    
    if 'authorized_keys' not in result:
        textError = textError + 'Не была настроена автоматическая ssh-аутентификация по ключам. (Удаленная машина)\n'
        procent -= 20
        
        
    result = contSecond.exec_run('cat /etc/ssh/sshd_config')[1].decode()
    
    if '\nPermitRootLogin no' not in result:
        textError = textError + 'Не был включен запрет доступа root\n'
        procent -= 7
    
    if '\nPasswordAuthentication no' not in result:
        textError = textError + 'Не был включен запрет доступа по паролю\n'
        procent -= 7
    
    
    if procent == 60:
        codeLab = 0
    else:
        codeLab = 1
    
    if procent < 0:
        procent = 0
    
    print(procent)
    print(textError)
    
    
    return codeLab, textError, procent
    
    
if __name__ == '__main__':  
    checkLab6()  
    
    

    
    
    
    
    
    
    