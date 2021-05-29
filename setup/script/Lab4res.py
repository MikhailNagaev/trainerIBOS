import os
import sys
import pickle
import subprocess
import docker
import re

clientDocker = docker.from_env()

def checkLab4():
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
    
    if diff == 0:
        max_proc = 15
    elif diff == 1:
        max_proc = 10
    else:
        max_proc = 7
        
    procent += max_proc
    textError1 = '1. Ошибки работы с IP адресами и интерфейсами:\n' 
    result = container.exec_run('ip a show eth0')[1].decode()
    if 'inet {}/16'.format('172.17.0.2') in result:
        res1 = False
        textError1 = textError1 + 'Не был удален адрес 172.17.0.2 интерфейса eth0.\n'
        procent -= (max_proc)/3
    
    if 'inet {}/16'.format(ip_addr) not in result:
        res1 = False
        textError1 = textError1 + 'Не был изменен адрес интерфейса eth0.\n'
        procent -= (max_proc)/3

    result = container.exec_run('ip link show eth0')[1].decode()
    if 'state UP' not in result:
        res1 = False
        textError1 = textError1 + 'Не был поднят интерфейс eth0.\n'
        procent -= (max_proc)/3
    
    if res1 != True:
        textError = textError + textError1
        
    if diff == 0:
        max_proc = 10
    elif diff == 1:
        max_proc = 10
    else:
        max_proc = 7
    
    procent += max_proc
    
    textError2 = '2. Ошибки создания таблиц и цепочек правил nftables:\n'
    if 21 not in ready:
        res2 = False
        textError2 = textError2 + 'Не была добавлена таблица {} семейства ip.\n'.format(table)
        procent -= (max_proc)/3
        
    if 22 not in ready:
        res2 = False
        textError2 = textError2 + 'Не была добавлена цепочка {} в таблицу {} семейства ip с параметрами: (type filter hook input priority 0; policy accept;)\n'.format(main_chain, table)
        procent -= (max_proc)/3
        
    if 23 not in ready:
        res2 = False
        textError2 = textError2 + 'Не была добавлена цепочка {} в таблицу {} семейства ip.\n'.format(second_chain, table)
        procent -= (max_proc)/3
    
    if res2 != True:
        textError = textError + textError2
    
    
    
    max_proc = 45
    procent += max_proc
    textError3 = '3. Ошибки создания правил nftables:\n'
    if 31 not in ready:
        res3 = False
        textError3 = textError3 + 'В цепочку {} не было добавлено правило перехода на цепочку {}\n'.format(main_chain, second_chain)
        procent -= (max_proc/4)
    if 32 not in ready:
        res3 = False
        textError3 = textError3 + 'В цепочку {} не было добавлено правило логирования легитимного трафика с префиксом {}.\n'.format(main_chain, prefix_accept)
        procent -= (max_proc/4)
    if 33 not in ready:
        res3 = False
        textError3 = textError3 + 'Не была добавлена цепочка {} в таблицу {} семейства ip.\n'.format(second_chain, table)
        procent -= (max_proc/4)
    if 34 not in ready:
        res3 = False
        textError3 = textError3 + 'В цепочку {} не было добавлено правило логирования запрещенного трафика с префиксом {}.\n'.format(second_chain, prefix_drop)
        procent -= (max_proc/4)
        
    result = container.exec_run('systemctl status ulogd')[1].decode()
    if 'Active: active' not in result:
        res3 = False
        textError3 = textError3 + 'Подсистема ulogd, необходимая для логирования в файл, не активна.\n'.format(second_chain, prefix_drop)
        
    if res3 != True:
        textError = textError + textError3
        
    if diff == 0:
        max_proc = 10
    elif diff >= 1:
        max_proc = 5
    
    textError4 = '4. Ошибки проверки настроенных правил и логирования:\n'
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
                        textError4 = textError4 + 'В файле log_network_lab.log пакеты {} не имеют префикса {}\n'.format(drop_protocol, prefix_drop)
                else:
                    SecondPacketExist = True
                    if tmpBool2 and prefix_accept not in line:
                        res4 = False
                        tmpBool2 = False
                        textError4 = textError4 + 'В файле log_network_lab.log легитимные пакеты не имеют префикса {}\n'.format(prefix_accept)
        
        if MainPacketExist == False:
            res4 = False
            textError4 = textError4 + 'В файле log_network_lab.log не отображены пакеты {}, которые должны были быть отброшеными. Возможно неврено настроены правила межсетевого экрана.\n'.format(drop_protocol)
        if SecondPacketExist == False:
            res4 = False
            textError4 = textError4 + 'В файле log_network_lab.log не отображены легитимные пакеты. Возможно неврено настроены правила межсетевого экрана.\n'.format(drop_protocol)        
             
                    
    else:
        res4 = False
        textError4 = textError4 + 'Файл log_network_lab.log не был создан службой ulogd.\n'
    
    if res4 == False:
        textError = textError + textError4
    else:
        procent += max_proc
    
    
    
    if diff >= 1:
        max_proc = 10
        if diff == 2:
            max_proc = 8
            
        procent += max_proc
        textError5 = '5. Ошибки удаления правил и цепочек в nftables:\n'
        if 51 not in ready:
            res5 = False
            textError5 = textError5 + 'Не удалено правило перехода на другую цепочку в цепочке {}.\n'.format(main_chain)
            procent -= (max_proc/2)
        
        if 52 not in ready:
            res5 = False
            textError5 = textError5 + 'Не удалена цепочка {}\n'.format(second_chain)
            procent -= (max_proc/2)
        
        if res5 != True:
            textError = textError + textError5
        
    if diff == 2:
        max_proc = 8
        textError6 = '6. Ошибки настройки MAC:\n'
        result = container.exec_run('ip a show eth0')[1].decode()
        if 'link/ether {} brd'.format(mac_addr) not in result:
            res6 = False
            textError6 = textError6 + 'Не был установлен MAC-адрес {} для интерфейса eth0.\n'.format(mac_addr)
        if res6 == False:
            textError = textError + textError6
        else:
            procent = procent + max_proc
        
    
    #print(res1, res2, res3, res4, res5, res6)
    #print(textError)
    #print(procent)
    
    if res1 and res2 and res3 and res4 and res5 and res6:
        codeLab = 0
    else:
        codeLab = 1
    
    return codeLab, textError, procent
    
    
if __name__ == '__main__':  
    checkLab4()  
    
    

    
    
    
    
    
    
    