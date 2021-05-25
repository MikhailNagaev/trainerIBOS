import os
import sys
import pickle
import subprocess
import docker
import re

clientDocker = docker.from_env()



def checkLab5():
    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    # Суммарно 70
    res1 = True # 15 10  5
    res2 = True # 20 20 15
    res3 = True # 15 15 10
    res4 = True # 20 15 10
    res5 = True #    10 10
    res6 = True #       20
    
    amount = 0
    procent = 0.0
    container = clientDocker.containers.get('trainerIBOS')
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    
    with open("/var/lib/docker/volumes/{}/_data/.bash_history".format(NAME_DOCKER_VM_VOLUME)) as gr, open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        diff = data[0]
        user = data[1]
        apt_get = data[2]
        service = data[3]
        priority = data[4]
        textBASH = []
        for line in gr:
            appLine = re.sub(r'\s+', ' ', line.rstrip())
            if appLine not in textBASH:
                textBASH.append(appLine)
    
    
    #print(textBASH)
    # -------------------- ПЕРВОЕ ЗАДАНИЕ -----------------------------------------
    if diff == 0:
        max_proc = 15
    elif diff == 1:
        max_proc = 10
    else:
        max_proc = 5
    
    procent = procent + max_proc
    
    textError1 = '1. Ошибки работы с системными журналами\n'
        
    res11 = False
    res121 = False; res122 = False
    res13 = False
    res23 = False
    res3 = False
    res41 = False; res42 = False; res43 = False; res44 = False; res45 = False
    res51 = False; res52 = False
    
    for command in textBASH:
        if 'ls ' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                text = result[1].decode()
                if 'syslog' in text and 'messages' in text:
                    res11 = True
                    continue
                    
        if ('cat ' in command or 'tail ' in command) and '/var/log/syslog' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res121 = True
                continue
            
        if ('cat ' in command or 'tail ' in command) and '/var/log/messages' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res122 = True
                continue    
        
        if ('cat ' in command or 'tail ' in command) and '/etc/rsyslog.conf' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res13 = True
                continue
        #-------------------------------
        if ('cat ' in command or 'tail ' in command) and '/var/log/auth.log' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res23 = True
                continue
                
        #-------------------------------
        if ('cat ' in command or 'tail ' in command) and '/var/log/apt/history.log' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res3 = True
                continue
                
        if 'journalctl' == command:
            res41 = True
            continue
            
        if 'journalctl' in command and '-p {}'.format(priority) in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res42 = True
                continue
                
        if 'journalctl' in command and '--since ' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res43 = True
                continue
       
        if 'journalctl' in command and '-k' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res44 = True
                continue
                
        if 'journalctl' in command and '--disk-usage' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res51 = True
                continue
        
        if 'journalctl' in command and '--vacuum-time=5days' in command:
            result = container.exec_run(command)
            if result[0] == 0:
                res52 = True
                continue
                
                
                
        
    if res11 == False:
        textError1 = textError1 + 'Не был просмотрен каталог /var/log на содержимое.\n'
        procent = procent - max_proc / 4
    if res121 == False:
        textError1 = textError1 + 'Не было просмотрено содержимое журнала syslog.\n'
        procent = procent - max_proc / 4
    if res122 == False:
        textError1 = textError1 + 'Не было просмотрено содержимое журнала messages.\n'
        procent = procent - max_proc / 4
    if res13 == False:
        textError1 = textError1 + 'Не были просмотрены конфигурационные настройки системных журналов.\n'
        procent = procent - max_proc / 4
        
    res1 = all([res11, res121, res122, res13])  
    
    
    
    
    
    if diff == 0:
        max_proc = 20
    elif diff == 1:
        max_proc = 20
    else:
        max_proc = 15
    
    procent = procent + max_proc
    
    textError2 = '2. Ошибки анализа auth.log\n'
    
    passwd = container.exec_run('cat /etc/passwd')[1].decode()
    
    
    if '{}:x'.format(user) not in passwd:
        res2 = False
        textError2 = textError2 + 'Не был создан пользователь {}.\nКак следствие не был осуществлен вход за данного пользователя, а также не был просмотрен (из-за его отсутствия) журнал auth.log\n'.format(user)
        procent -= max_proc
    
    else:
        
        auth = container.exec_run('cat /var/log/auth.log')[1].decode()
        if 'session opened for user {} by'.format(user) not in auth and 'session closed for user {}'.format(user) not in auth:
            res2 = False
            textError2 = textError2 + 'Не был осущетсвлен вход за пользователя {}. (Возможно, вы не завершили сесссию за данного пользователя).\n'.format(user)
            procent -= max_proc / 3
            
            
        if res23 == False:
            res2 = False
            textError2 = textError2 + 'Не был просмотрен auth.log.\n'
            procent -= max_proc/3
            
    
    if diff == 0:
        max_proc = 15
    elif diff == 1:
        max_proc = 15
    else:
        max_proc = 10
    
    procent = procent + max_proc
    
    textError3 = '3. Ошибки анализа apt/history.log\n'
    
    if res3 == False:
            textError3 = textError3 + 'Не был просмотрен apt/history.log\n'
            procent -= max_proc
    
    
    
    if diff == 0:
        max_proc = 20
    elif diff == 1:
        max_proc = 15
    else:
        max_proc = 10
    procent = procent + max_proc
    
    textError4 = '4. Ошибки управления журналами systemd - journald.\n'
    
    if res41 == False:
        res4 = False
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не был просмотрен журнал journald утилитой journalctl (без параметров)\n'
    
    if res42 == False:
        res4 = False
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не были просмотрено сообщения {} приоритета.\n'.format(priority)
    
    if res43 == False:
        res4 = False
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не были просмотрены сообщения за определнное время.\n'
    
    if res44 == False:
        res4 = False
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не были просмотрены сообщения ядра.\n'
       
    ls_res = container.exec_run('ls /var/log/journal')[0]
    cat_conf = container.exec_run('cat /etc/systemd/journald.conf')[1].decode()
    check_status = container.exec_run('systemctl status systemd-journald')
    
    
    if ls_res != 0 or check_status[0] != 0 or 'active (running)' not in  check_status[1].decode():
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не было настроено постоянное хранение журналов Journald.\n'
        res4 = False
        
    #print(cat_conf)
    
    if '\nSystemMaxUse=100M\n' not in cat_conf:
        procent = procent - max_proc / 6
        textError4 = textError4 + 'Не был настрое максимальный размер журнала Journald.\n'
        res4 = False
        
    #---------------------------------------------
    
    if diff >= 1:
        max_proc = 10
        procent = procent + max_proc
        textError5 = '5. Ошибки журналами systemd - journald.\n'
        
        if res51 == False:    
            res5 = False
            procent = procent - max_proc / 2
            textError5 = textError5 + 'Не был просмотрен размер журнала Journald.\n'
            
        if res52 == False:    
            res5 = False
            procent = procent - max_proc / 2
            textError5 = textError5 + 'Не была выполнена команда по оставлению только журналов, которые моложе 5 дней.\n'
        
    if diff == 2:
        max_proc = 20
        procent = procent + max_proc
        status = container.exec_run('systemctl status {}'.format(service))[1].decode()
        textError6 = '6. Ошибки исправления сервисов по журналу Journald.\n'
        if 'Active: inactive (dead)' not in status or '{}.service: Succeeded'.format(service) not in status:
            res6=False
            procent = procent - max_proc
            textError6 = textError6 + 'Не был успешно запущен сервис {}.\n'.format(service)
        
     
               
                    
    
        
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
    
    if res1 and res2 and res3 and res4 and res5 and res6:
        codeLab = 0
    else:
        codeLab = 1
    
    return codeLab, textError, procent
    
    
if __name__ == '__main__':  
    checkLab5()  
    
    

    
    
    
    
    
    
    