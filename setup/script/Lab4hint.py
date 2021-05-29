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

def checkLab4Hint():
    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    # Суммарно 80
    res1 = True # 15 10 7
    res2 = True # 10 10 7 
    res3 = True # 45 45 45
    res4 = True # 10  5 5  
    res5 = True #    10 8
    res6 = True #       8
    
    amount = 0
    procent = 0.0
    container = clientDocker.containers.get('trainerIBOS')
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    
    with open('/tmp/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        diff = data[0]
        ip_addr = data[1]
        table = data[2]
        main_chain = data[3]
        second_chain = data[4]
        drop_protocol = data[5]
        prefix_drop = data[6]
        prefix_accept = data[7]
        mac_addr = data[8]
        ready = data[9]   
    
    result = container.exec_run('ip a show eth0')[1].decode()
    if 'inet {}/16'.format('172.17.0.2') in result:
        res1 = False
    if 'inet {}/16'.format(ip_addr) not in result:
        res1 = False
    result = container.exec_run('ip link show eth0')[1].decode()
    if 'state UP' not in result:
        res1 = False

    if 21 not in ready:
        res2 = False
        
    if 22 not in ready:
        res2 = False
        
    if 23 not in ready:
        res2 = False
    
    if 31 not in ready:
        res3 = False
    if 32 not in ready:
        res3 = False
        
    if 33 not in ready:
        res3 = False

    if 34 not in ready:
        res3 = False
        
    result = container.exec_run('systemctl status ulogd')[1].decode()
    if 'Active: active' not in result:
        res3 = False

    if 100 not in ready:
        MainPacketExist = False
        SecondPacketExist = False
        if os.path.exists("/var/lib/docker/volumes/{}/_data/log_network_lab.log".format('trainerIBOS_VOLUME2')):
            with open("/var/lib/docker/volumes/{}/_data/log_network_lab.log".format('trainerIBOS_VOLUME2'), 'r') as logs_file:
                tmpBool1 = True; tmpBool2 = True
                for line in logs_file:
                    if 'PROTO={}'.format(drop_protocol.upper()) in line: #Должен быть откинут с дропом
                        MainPacketExist = True
                        if tmpBool1 and prefix_drop not in line:
                            res4 = False
                            tmpBool1 = False
                    else:
                        SecondPacketExist = True
                        if tmpBool2 and prefix_accept not in line:
                            res4 = False
                            tmpBool2 = False
            
            if MainPacketExist == False:
                res4 = False
            if SecondPacketExist == False:
                res4 = False       
                 
                        
        else:
            res4 = False
            
        if res4==True:
            ready.append(100)
            with open('/etc/trainerIBOS/trainerIBOS.task', 'wb') as fil:
                pickle.dump([diff, ip_addr, table, main_chain, second_chain, drop_protocol, prefix_drop, prefix_accept, mac_addr, ready], fil)
    
    
    
    if diff >= 1:
        if 51 not in ready:
            res5 = False
        
        if 52 not in ready:
            res5 = False
        
    if diff == 2:
        result = container.exec_run('ip a show eth0')[1].decode()
        if 'link/ether {} brd'.format(mac_addr) not in result:
            res6 = False
    
    
    # -------------------- ШЕСТОЕ ЗАДАНИЕ ---------------------------------------------------------------------------------------------------------------------------
    
    print(res1, res2, res3, res4, res5, res6)
    if res1:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-1')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-2')
        sock.close() # Отправляяет соответствующее сообщение основной программе

    if res3:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-3')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res4:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-4')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res5 and diff > 0:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-5')
        sock.close() # Отправляяет соответствующее сообщение основной программе
        
    if res6 and diff == 2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab4-6')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    
    
if __name__ == '__main__':  
    checkLab4Hint()  
    
    

    
    
    
    
    
    
    