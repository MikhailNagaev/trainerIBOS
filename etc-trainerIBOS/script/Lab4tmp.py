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


def checkLab4tmp():
    
    container = clientDocker.containers.get('trainerIBOS')
    
    with open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task:
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
    
    if 21 not in ready: # Проверка наличия таблицы
        result = container.exec_run('nft list table ip {}'.format(table))
        if result[0] == 0:
            ready.append(21)
    if 22 not in ready: # Проверка наличия цепочки главной
        result = container.exec_run('nft list chain ip {} {}'.format(table, main_chain))
        if result[0] == 0 and 'type filter hook input priority 0; policy accept;' in result[1].decode():
            ready.append(22)
    if 23 not in ready: # Проверка наличия цепочки второстепенной
        result = container.exec_run('nft list chain ip {} {}'.format(table, second_chain))
        if result[0] == 0 :
            ready.append(23)
            
    if 31 not in ready and 22 in ready: # Проверка правила прыжка 
        result = container.exec_run('nft list chain ip {} {}'.format(table, main_chain))
        if result[0] == 0:
            TEXT = result[1].decode()
            if '{} '.format(drop_protocol) in TEXT and (' jump ' in TEXT or ' goto ' in TEXT) and ' {}'.format(second_chain) in TEXT:
                ready.append(31)
                
    if 32 not in ready and 22 in ready: # Проверка логирования
        result = container.exec_run('nft list chain ip {} {}'.format(table, main_chain))
        if result[0] == 0:
            TEXT = result[1].decode()
            if 'log ' in TEXT and ' prefix ' in TEXT and ' group ' in TEXT and (prefix_accept in TEXT):
                ready.append(32)
                
    if 33 not in ready and 23 in ready: # Проверка правил удаления
        result = container.exec_run('nft list chain ip {} {}'.format(table, second_chain))
        if result[0] == 0:
            TEXT = result[1].decode()
            if 'drop\n' in TEXT:
                ready.append(33)
                
    if 34 not in ready and 23 in ready: # Проверка логирования в второстепенной цепочки 
        result = container.exec_run('nft list chain ip {} {}'.format(table, second_chain))
        if result[0] == 0:
            TEXT = result[1].decode()
            if 'log ' in TEXT and ' prefix ' in TEXT and ' group' in TEXT and (prefix_drop in TEXT):
                ready.append(34)
                
    if diff >= 1:
        
        if 51 not in ready and 22 in ready and 31 in ready and 32 in ready:
            result = container.exec_run('nft list chain ip {} {}'.format(table, main_chain))
            if result[0] == 0:
                TEXT = result[1].decode()
                if 'jump ' not in TEXT and 'goto ' not in TEXT and ' {}'.format(second_chain) not in TEXT:
                    ready.append(51)
        
        if 52 not in ready and 23 in ready and 33 in ready and 34 in ready and 51 in ready:
            result = container.exec_run('nft list chain ip {} {}'.format(table, second_chain))
            if result[0] != 0:
                ready.append(52)
                
            
    
    #print(ready)    
    
    with open('/etc/trainerIBOS/trainerIBOS.task', 'wb') as fil:
        pickle.dump([diff, ip_addr, table, main_chain, second_chain, drop_protocol, prefix_drop, prefix_accept, mac_addr, ready], fil)
    
    
    
    
    
    
    
    
if __name__ == '__main__':  
    checkLab4tmp()  
    
    

    
    
    
    
    
    
    