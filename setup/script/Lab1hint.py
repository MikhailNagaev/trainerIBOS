import socket
import os
import sys
import pickle

with open('/etc/trainerIBOS/port_time.conf', 'r') as f:
    portProgramm = int(f.readline())


def CheckGroup(s, usr):
    for i in usr:
        if i not in s:
            return False
    return True

res1 = False
res2 = True
res3 = True
amount = 0
NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
#print(NAME_DOCKER_VM_VOLUME)
with open("/var/lib/docker/volumes/{}/_data/passwd".format(NAME_DOCKER_VM_VOLUME)) as passwd, open('/tmp/trainerIBOS/trainerIBOS.task', 'rb') as task, open("/var/lib/docker/volumes/{}/_data/group".format(NAME_DOCKER_VM_VOLUME)) as gr:
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
    #print(conn) ###
    for iusr in range(len(users)):
        for line in passwd:
            if (users[iusr] in line) and (names[iusr] in line):
                amount += 1
        passwd.seek(0)
    if amount == len(users):
        res1 = True
    res2 = CheckGroup(gr.read(), groups)
    gr.seek(0)
    amount = 0
    tmp_str = []
    for line in gr:
        if line.split(':')[0] in groups:
            tmp_str.append(line)
    #print(tmp_str) ###
    est = True if len(tmp_str)>0 else False
    for line in tmp_str:
        x = line[:line.find(':')]
        for i in conn[x]:
            print('est') ###
            if i not in line:
                est = False
    res3 = True if est else False
    if amount == len(connect):
        res1 = True

print(res1, res2, res3) ###
if res1:
    sock = socket.socket()
    sock.connect(('localhost', portProgramm))
    sock.send(b'codeLab1-1')
    sock.close() # Отправляяет соответствующее сообщение основной программе
    
if res2:
    sock = socket.socket()
    sock.connect(('localhost', portProgramm))
    sock.send(b'codeLab1-2')
    sock.close() # Отправляяет соответствующее сообщение основной программе

if res3:
    sock = socket.socket()
    sock.connect(('localhost', portProgramm))
    sock.send(b'codeLab1-3')
    sock.close() # Отправляяет соответствующее сообщение основной программе
    