import os
import sys
import socket
import pickle
import subprocess
import docker



with open('/etc/trainerIBOS/port_time.conf', 'r') as f:
    portProgramm = int(f.readline())
    
    
    
clientDocker = docker.from_env()

def getIndex(item, LIST):
    for i in range(len(LIST)):
        if item == LIST[i]:
            return i
def mySplit(string):
    lst = []
    startIND = 0
    endIND = 0
    for i in range(len(string)):
        if string[i] == ' ' and string[i-1] != ' ':
            endIND = i
            lst.append(string[startIND:endIND])
        if string[i] != ' ' and string[i-1] == ' ':
            startIND = i
    lst.append(lst.append(string[endIND+1:]))
    return lst[:-1]
                        

def checkLab2Hint():
    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    res1 = True
    res2 = True
    res3 = True
    res4 = True
    amount = 0
    procent = 0.0
    container = clientDocker.containers.get('trainerIBOS')
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    with open("/var/lib/docker/volumes/{}/_data/group".format(NAME_DOCKER_VM_VOLUME)) as gr, open('/tmp/trainerIBOS/trainerIBOS.task', 'rb') as task:
        data = pickle.load(task)
        diff = data[0]
        users = data[1]
        groups = data[2]
        dirs = data[3]
        if len(data) > 4:
            ready = data[4]
        else:
            ready = []
        textgr = gr.read().split('\n')
    
    
    # Проверка 1 задания ---------------- Добавление пользователей в группы
    
    
    if 1 not in ready:
        for line in textgr:
            name_group = line[0:line.find(':')]
            if name_group in groups:
                index_group = getIndex(name_group, groups)
                for user in users[index_group*2:index_group*2+2]:
                    if user not in line:
                        res1 = False
        
        if res1 == True:
            ready.append(1)
                    
    rights = {}
    dirs_sett = container.exec_run('ls /mnt -l')[1].decode().split('\n')[1:-1]
    for line in dirs_sett:
        line_split = mySplit(line)
        rights[line_split[-1]] = [line_split[0], line_split[2], line_split[3]]
    
    if 2 not in ready:
    # Проверка 2 и 3 задания --------------------------- Установленные права и владельцы файлов
        if diff != 2:
        
            for dirr in dirs:
                #print(rights[dirr][0][1:], rights[dirr][0][1:] != 'rwxr-x---', rights[dirr][0][1:] != 'rwxr-x---+')
                if rights[dirr][0][1:] != 'rwxr-x---' and rights[dirr][0][1:] != 'rwxr-x---+':
                    res2 = False
            if res2 == True:
                ready.append(2)
            
    if 3 not in ready:
        for i in range(len(dirs) - 1):
            if not (rights[dirs[i]][1] == users[i*2] and rights[dirs[i]][2] == groups[i]):
                res3 = False
        if res3 == True:
            ready.append(3)
    
    
    
    # Проверка 5 задания ACL -------------------------------------------------------------------------------------------
    if diff == 2:
        
        d = dict(); d[dirs[-1]] = dict(); d[dirs[0]] = dict(); d[dirs[1]] = dict(); d[dirs[2]] = dict(); d[dirs[-1] + '/text.txt'] = dict(); d[dirs[0] + '/text.txt'] = dict(); d[dirs[1] + '/text.txt'] = dict()
        # Проверка папки
        for i in range(len(dirs)):
            acl = container.exec_run('getfacl -p /mnt/{}'.format(dirs[i]))[1].decode().split('\n')
            d[dirs[i]]['other'] = acl[-3][-3:]
            if acl[-4][:4] == 'mask':
                acl = acl[3:-4]
                for indacl in acl:
                    if 'user::' in indacl:
                        d[dirs[i]]['user'] = indacl.rstrip()[-3:]
                        continue
                    if 'group::' in indacl:
                        d[dirs[i]]['group'] = indacl.rstrip()[-3:]
                        continue
                    usr = indacl.split(':')[1]
                    rgt = indacl.split(':')[2].rstrip()
                    if len(rgt) > 3:
                        rgt = rgt[0:3]
                    d[dirs[i]][usr] = rgt
            else:
                acl = acl[3:5]
                for indacl in acl:
                    usr = indacl.split('::')[0]
                    rgt = indacl.split('::')[1].rstrip()
                    if len(rgt) > 3:
                        rgt = rgt[0:3]
                    d[dirs[i]][usr] = rgt
                
        
        print(d)
        # Проверка файлов
        acl = container.exec_run('getfacl -p /mnt/{}/text.txt'.format(dirs[-1]))[1].decode().split('\n')
        if acl[-4][:4] == 'mask':
            acl = acl[3:-4]
            for indacl in acl:
                if 'user::' not in  indacl and 'group::' not in indacl:
                    usr = indacl.split(':')[1]
                    rgt = indacl.split(':')[2].rstrip()
                    if len(rgt) > 3:
                        rgt = rgt[0:3]
                    d[dirs[-1] + '/text.txt'][usr] = rgt
        
        acl = container.exec_run('getfacl -p /mnt/{}/text.txt'.format(dirs[0]))[1].decode().split('\n')
        if acl[-4][:4] == 'mask':
            acl = acl[3:-4]
            for indacl in acl:
                if 'user::' not in  indacl and 'group::' not in indacl:
                    usr = indacl.split(':')[1]
                    rgt = indacl.split(':')[2].rstrip()
                    if len(rgt) > 3:
                        rgt = rgt[0:3]
                    d[dirs[0] + '/text.txt'][usr] = rgt
                    
                    
        acl = container.exec_run('getfacl -p /mnt/{}/text.txt'.format(dirs[1]))[1].decode().split('\n')
        if acl[-4][:4] == 'mask':
            acl = acl[3:-4]
            for indacl in acl:
                if 'user::' not in  indacl and 'group::' not in indacl:
                    usr = indacl.split(':')[1]
                    rgt = indacl.split(':')[2].rstrip()
                    if len(rgt) > 3:
                        rgt = rgt[0:3]
                    d[dirs[1] + '/text.txt'][usr] = rgt
        
        if 2 not in ready:
        # Проверка второго задания!!!!!!!!!
            for pap in dirs:
                if d[pap]['user'] != 'rwx' or d[pap]['group'] != 'r-x' or d[pap]['other'] != '---':
                    res2 = False
            if res2 == True:
                ready.append(2)
        
        
        if 4 not in ready:
            # Проверка
            tmp = True
            try:
                if len(d[dirs[-1]]) == 7:
                    if d[dirs[-1]][users[0]] != '-w-':
                        tmp = False
                    if d[dirs[-1]][groups[0]] != 'r-x':
                        tmp = False
                    if d[dirs[-1]][groups[1]] != 'r-x':
                        tmp = False
                    if d[dirs[-1]][groups[2]] != 'r-x':
                        tmp = False
                else:
                    tmp = False
            except KeyError:
                tmp = False
                
            if tmp == False:
                res4 = False
              
                
                
            tmp = True
            try:
                if len(d[dirs[0]]) == 5:
                    if d[dirs[0]][users[3]] != 'rwx':
                        tmp = False
                    if d[dirs[0]][groups[1]] != 'r--':
                        tmp = False
                else:
                    tmp = False
            
            except KeyError:
                tmp = False
            
            if tmp == False:
                res4 = False
            
            tmp = True
            try:
                if len(d[dirs[1]]) == 5:
                    if d[dirs[1]][users[1]] != 'rwx':
                        tmp = False
                    if d[dirs[1]][groups[0]] != 'r--':
                        tmp = False
                else:
                    tmp = False
            except KeyError:
                tmp = False
            
            
            if tmp == False:
                res4 = False 
                
                
                
            tmp = True
            try:
                if len(d[dirs[-1] + '/text.txt']) == 9:
                    if d[dirs[-1] + '/text.txt'][users[0]] != 'rw-':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][users[1]] != 'r--':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][users[2]] != 'rw-':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][users[3]] != 'r--':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][users[4]] != 'rw-':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][users[5]] != 'r--':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][groups[0]] != 'r--':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][groups[1]] != 'rw-':
                        tmp = False
                    if d[dirs[-1] + '/text.txt'][groups[2]] != 'r--':
                        tmp = False

                else:
                    tmp = False
            except KeyError:
                tmp = False
            
            
            if tmp == False:
                res4 = False 
                
                
            tmp = True
            try:
                if len(d[dirs[0] + '/text.txt']) == 2:
                    if d[dirs[0] + '/text.txt'][users[2]] != 'r--':
                        tmp = False
                    if d[dirs[0] + '/text.txt'][users[3]] != 'rw-':
                        tmp = False
                else:
                    tmp = False
            except KeyError:
                tmp = False
                
            if tmp == False:
                res4 = False
            
            
            tmp = True
            try:
                if len(d[dirs[1] + '/text.txt']) == 2:
                    if d[dirs[1] + '/text.txt'][users[0]] != 'r--':
                        tmp = False
                    if d[dirs[1] + '/text.txt'][users[1]] != 'rw-':
                        tmp = False
                else:
                    tmp = False
            except KeyError:
                tmp = False
                
            if tmp == False:
                res4 = False
            if res4 == True:
                ready.append(4)
    # Проверка 5 задания ACL -------------------------------------------------------------------------------------------
    
    NAME_DOCKER_VM = 'trainerIBOS'
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, users, groups, dirs, ready], fil)
        
        
    print(res1, res2, res3, res4)
    if res1:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab2-1')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab2-2')
        sock.close() # Отправляяет соответствующее сообщение основной программе

    if res3:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab2-3')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    if res4 and diff == 2:
        sock = socket.socket()
        sock.connect(('localhost', portProgramm))
        sock.send(b'codeLab2-5')
        sock.close() # Отправляяет соответствующее сообщение основной программе
    
    
if __name__ == '__main__':  
    checkLab2Hint()  
    
    

    
    
    
    
    
    
    