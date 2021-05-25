import os
import sys
import pickle


def checkLab1():

    codeLab = 0 #Код завершения 0 - успешно, 1 - не успешно.
    textError = '' #Текст завершения.
    res1 = False
    res2 = True
    res3 = True
    amount = 0
    procent = 0.0
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    #print(NAME_DOCKER_VM_VOLUME)
    with open("/var/lib/docker/volumes/{}/_data/passwd".format(NAME_DOCKER_VM_VOLUME)) as passwd, open('/etc/trainerIBOS/trainerIBOS.task', 'rb') as task, open("/var/lib/docker/volumes/{}/_data/group".format(NAME_DOCKER_VM_VOLUME)) as gr:
        data = pickle.load(task)
        users = data[0]
        names = data[1]
        groups = data[2]
        connect = data[3]
        
        conn = {}
        for i in connect:
            x = i.split(':')
            if x[0] in conn:
                conn[x[0]].append(x[1])
            else:
                conn[x[0]] = [x[1]]
        
        
        
        # Проверка пользователей
        textError1 = '1. Ошибки добавления пользователей:\n'
        procent = 35.0
        usertmp = []
        for iusr in range(len(users)):
            for line in passwd:
                if (users[iusr] in line) and (names[iusr] in line):
                    amount += 1
                    usertmp.append(users[iusr])
            passwd.seek(0)
        if amount == len(users):
            res1 = True
        for i in range(len(users)):
            if users[i] not in usertmp:
                textError1 = textError1 + 'Не был добавлен пользователь {} c именем {}.\n'.format(users[i], names[i])
                procent -= 35.0/len(users)
        
        # Проверка групп
        textError2 = '2. Ошибки добавления групп:\n'
        procent = procent + 20.0
        textGroup = gr.read()
        res2 = True
        for i in groups:
            if i + ':' not in textGroup:
                res2 = False
                textError2 = textError2 + 'Не была создана группа с именем {}.\n'.format(i)
                procent -= 20.0/len(groups)
        
        # Проверка наличия пользователей в группах
        textError3 = '3. Ошибки добавления пользователей в группы:\n'
        gr.seek(0)
        amount = 0
        tmp_str = []
        gr_tmp = []
        for line in gr:
            tk = line.split(':')[0]
            if tk in groups:
                tmp_str.append(line)
                gr_tmp.append(tk)
                
        
        for igr in groups:
            if igr not in gr_tmp:
                for i in conn[igr]:
                    textError3 = textError3 + 'Пользователь {} не был добавлен в группу {}.\n'.format(i, igr)
                           
        est = True if len(tmp_str)>0 else False
        for line in tmp_str:
            x = line[:line.find(':')]
            for i in conn[x]:
                if i not in line:
                    est = False
                    textError3 = textError3 + 'Пользователь {} не был добавлен в группу {}.\n'.format(i, x)
                else:
                    procent = procent + 45.0/len(connect)
        res3 = True if est else False
        
        if res1 == False:
            textError = textError + textError1
        if res2 == False:
            textError = textError + textError2
        if res3 == False:
            textError = textError + textError3
            
        if res1 and res2 and res3:
            codeLab = 0
        else:
            codeLab = 1
        
        return codeLab, textError, procent

    
    
if __name__ == '__main__':  
    checkLab1()  
    
    
    
    