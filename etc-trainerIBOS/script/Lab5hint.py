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

def checkLab5Hint():
    
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
    NAME_DOCKER_VM = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    ready = []
    
    with open("/var/lib/docker/volumes/{}/_data/.bash_history".format(NAME_DOCKER_VM_VOLUME)) as gr, open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        diff = data[0]
        user = data[1]
        apt_get = data[2]
        service = data[3]
        priority = data[4]
        if len(data) >= 6:
            ready = data[5]
        textBASH = []
        for line in gr:
            appLine = re.sub(r'\s+', ' ', line.rstrip())
            if appLine not in textBASH:
                textBASH.append(appLine)
    
    # -------------------- ПЕРВОЕ ЗАДАНИЕ -----------------------------------------
    res11 = False
    res121 = False; res122 = False
    res13 = False
    res23 = False
    res3 = False
    res41 = False; res42 = False; res43 = False; res44 = False; res45 = False
    res51 = False; res52 = False
    
    for command in textBASH:
        
        if 1 not in ready:
        
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
        if 2 not in ready:
            if ('cat ' in command or 'tail ' in command) and '/var/log/auth.log' in command:
                result = container.exec_run(command)
                if result[0] == 0:
                    res23 = True
                    continue
                
        #-------------------------------
        if 3 not in ready:
            if ('cat ' in command or 'tail ' in command) and '/var/log/apt/history.log' in command:
                result = container.exec_run(command)
                if result[0] == 0:
                    res3 = True
                    continue
                
        if 4 not in ready:        
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
        
        if 5 not in ready:
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
                
    if 2 not in ready:
        passwd = container.exec_run('cat /etc/passwd')[1].decode()
        
        
        if '{}:x'.format(user) not in passwd:
            res2 = False
        else:
            auth = container.exec_run('cat /var/log/auth.log')[1].decode()
            if 'session opened for user {} by'.format(user) not in auth and 'session closed for user {}'.format(user) not in auth:
                res2 = False

            if res23 == False:
                res2 = False         
    if 4 not in ready:
        if res41 == False:
            res4 = False
        
        if res42 == False:
            res4 = False
        
        if res43 == False:
            res4 = False
        
        if res44 == False:
            res4 = False
        
    if 4 not in ready:   
        ls_res = container.exec_run('ls /var/log/journal')[0]
        cat_conf = container.exec_run('cat /etc/systemd/journald.conf')[1].decode()
        check_status = container.exec_run('systemctl status systemd-journald')
        
        
        if ls_res != 0 or check_status[0] != 0 or 'active (running)' not in  check_status[1].decode():
            res4 = False
            
        #print(cat_conf)
        
        if '\nSystemMaxUse=100M\n' not in cat_conf:
            res4 = False
        
    #---------------------------------------------
    
    if diff >= 1:
        if 5 not in ready:
            if res51 == False:    
                res5 = False
                
            if res52 == False:    
                res5 = False
        
    if diff == 2:
        if 6 not in ready:
            status = container.exec_run('systemctl status {}'.format(service))[1].decode()
            if 'Active: inactive (dead)' not in status or '{}.service: Succeeded'.format(service) not in status:
                res6=False
    
    res1 = all([res11, res121, res122, res13])      
    if 1 not in ready and res1 == True:
        ready.append(1)
    if 2 not in ready and res2 == True:
        ready.append(2)
    if 3 not in ready and res3 == True:
        ready.append(3)
    if 4 not in ready and res4 == True:
        ready.append(4)
    if 5 not in ready and res5 == True:
        ready.append(5)
    if 6 not in ready and res6 == True:
        ready.append(6)
   
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, user, apt_get, service, priority, ready], fil)
    
    #print(res1, res2, res3, res4, res5, res6)
    if res1:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-1')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-2')
        sock.close() # Отправляяет соответствующее сообщение основной программе

    if res3:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-3')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res4:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-4')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res5 and diff > 0:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-5')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res6 and diff == 2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab5-6')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    
    
if __name__ == '__main__':  
    checkLab5Hint()  
    
    

    
    
    
    
    
    
    