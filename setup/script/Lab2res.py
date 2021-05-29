import os
import sys
import pickle
import subprocess
import docker

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
                        

def checkLab2():
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
        textgr = gr.read().split('\n')
    
    
    # Проверка 1 задания ---------------- Добавление пользователей в группы
    max_ready1 = 20.0
    if diff == 2:
        max_ready1 = max_ready1 - 10
    procent = max_ready1
    textError1 = '1. Ошибки добавления пользователей в группы:\n'
    for line in textgr:
        name_group = line[0:line.find(':')]
        if name_group in groups:
            index_group = getIndex(name_group, groups)
            for user in users[index_group*2:index_group*2+2]:
                if user not in line:
                    res1 = False
                    textError1 = textError1 + 'Пользователь {} не был добавлен в группу {}.\n'.format(user, name_group)
                    procent = procent - max_ready1/len(users)
                    
    rights = {}
    dirs_sett = container.exec_run('ls /mnt -l')[1].decode().split('\n')[1:-1]
    for line in dirs_sett:
        line_split = mySplit(line)
        rights[line_split[-1]] = [line_split[0], line_split[2], line_split[3]]
    
    
    # Проверка 2 и 3 задания --------------------------- Установленные права и владельцы файлов
    if diff != 2:
        max_ready2 = 20.0
        procent = procent + max_ready2
        textError2 = '2. Ошибки настроенных прав для папок:\n'
    
    
        for dirr in dirs:
            #print(rights[dirr][0][1:], rights[dirr][0][1:] != 'rwxr-x---', rights[dirr][0][1:] != 'rwxr-x---+')
            if rights[dirr][0][1:] != 'rwxr-x---' and rights[dirr][0][1:] != 'rwxr-x---+':
                res2 = False
                textError2 = textError2 + 'Для каталога {} неверно настроены права доступа.\n'.format(dirr)
                procent = procent - max_ready2/len(dirs)
    
    max_ready3 = 30.0
    if diff == 2:
        max_ready3 = max_ready3 - 10
    procent = procent + max_ready3
    textError3 = '3. Ошибки назначения владельцев и групп для каталогов:\n'
    for i in range(len(dirs) - 1):
        if not (rights[dirs[i]][1] == users[i*2] and rights[dirs[i]][2] == groups[i]):
            res3 = False
            textError3 = textError3 + 'Для каталога {} неверно настроены владелец ({}) и группа ({}).\n'.format(dirs[i], rights[dirs[i]][1], rights[dirs[i]][2])
            procent = procent - max_ready3/(len(dirs)-1)
    
    
    
    res4 = True
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
                
        
        #print(d)
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
        
        
        # Проверка второго задания!!!!!!!!!
        max_ready2 = 10.0
        textError2 = '2. Ошибки настроенных прав для папок:\n'
        procent = procent + max_ready2
        for pap in dirs:
            #print(d[pap])
            try:
                if d[pap]['user'] != 'rwx' or d[pap]['group'] != 'r-x' or d[pap]['other'] != '---':
                    res2 = False
                    textError2 = textError2 + 'Для каталога {} неверно настроены права доступа.\n'.format(pap)
                    procent = procent - max_ready2/len(dirs)
            except KeyError:
                res2= False
                textError2 = textError2 + 'Для каталога {} неверно настроены права доступа.\n'.format(pap)
                procent = procent - max_ready2/len(dirs)
        
        
        textError4 = '4. Ошибки назначения POSIX ACL:\n'
        max_ready4 = 30.0
        procent = procent + max_ready4
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[-1])
            procent = procent - max_ready4 / 6
            
            
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[0])
            procent = procent - max_ready4 / 6
        
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[1])
            procent = procent - max_ready4 / 6   
            
            
            
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[-1] + '/text.txt')
            procent = procent - max_ready4 / 6 
            
            
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[0] + '/text.txt')
            procent = procent - max_ready4 / 6
        
        
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
            textError4 = textError4 + 'Неверно настроены ACL права для {}\n'.format(dirs[1] + '/text.txt')
            procent = procent - max_ready4 / 6
      
    # Проверка 5 задания ACL -------------------------------------------------------------------------------------------
    if res1 == False:
        textError = textError + textError1
    if res2 == False:
        textError = textError + textError2
    if res3 == False:
        textError = textError + textError3
    if res4 == False:
        textError = textError + textError4
    
    
    if res1 and res2 and res3 and res4:
        codeLab = 0
    else:
        codeLab = 1
    
    return codeLab, textError, procent
    
    
if __name__ == '__main__':  
    checkLab2()  
    
    

    
    
    
    
    
    
    