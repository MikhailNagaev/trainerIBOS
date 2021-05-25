import subprocess
import os
import time
import random
import pickle
import tarfile
import docker
from docker.types import LogConfig

clientDocker = docker.from_env()
cont = 0
cont2 = 0
vol = 0
vol2 = 0
net = 0
#--------------ФУНКЦИИ ПРОВЕРКИ и настройка КОНТЕЙНЕРОВ!!!!--------------
def CheckImages():
    list_hash = dict()
    with open('/etc/trainerIBOS/check_images.conf', 'r') as FILE:
        FileImagesTar = FILE.readline().split('=')[1].rstrip()
        for line in FILE:
            lst = line.split('=')
            list_hash[lst[0]] = [lst[1].rstrip(), False]
    
    list_images = clientDocker.images.list()
    
    for image in list_images:
        if len(image.tags) == 1:
            name_image = image.tags[0].split(':')[0]
            if name_image in list_hash:
                if list_hash[name_image][0] == image.id:
                    list_hash[name_image][1] = True
    lst_error = []
    for key in list_hash:
        if list_hash[key][1] == False:
            lst_error.append(key)
    
    return lst_error
    
def LoadImages():
    with open('/etc/trainerIBOS/check_images.conf', 'r') as FILE:
        FileImagesTar = FILE.readline().split('=')[1].rstrip()
    if os.path.exists(FileImagesTar):    
        ImagesTar = open(FileImagesTar, 'rb')
        clientDocker.images.load(ImagesTar)
        return 0
    else:
        return 1
    
#-------------ФУНКЦИИ ПРОВЕРКИ и настройка КОНТЕЙНЕРОВ!!!!----------------


def copy_to(src, dst):
    name, dst = dst.split(':')
    container = clientDocker.containers.get(name)

    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)
    tar = tarfile.open(src + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(src + '.tar', 'rb').read()
    container.put_archive(os.path.dirname(dst), data)



def startTaskControlUserAndGroup(diff, train): # Первое задание на создание групп и пользователей
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    global cont
    global vol
    
    vol = clientDocker.volumes.create('trainerIBOS_VOLUME')
    
    volumes_dict = {NAME_DOCKER_VM_VOLUME : {'bind':'/etc','mode':'rw'}}
    
    cont = clientDocker.containers.run('bos/debian1', '/bin/bash', detach=True, name=NAME_DOCKER_VM, hostname='USER-GROUP-MACHINE', volumes=volumes_dict, remove=True, tty = True)
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    
    
    USER_NAME = []
    USER_LOGIN = []
    GROUP_NAME = []
    USERS = []
    amountUsers = 3 * (diff + 1) #3 6 9
    amountGroup = (diff + 1) + 1 #2 3 4
    amountConnection = (diff + 1) * 4 #4 8 12
    
    # Создание задания
    with open('/etc/trainerIBOS/desc/Lab1/Lab1-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            USERS.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            GROUP_NAME.append(fil.readline())
    
    USERS = [i.rstrip() for i in random.sample(USERS, amountUsers)]
    USER_LOGIN = [i.split(":")[0].rstrip() for i in USERS]
    USER_NAME = [i.split(":")[1].rstrip() for i in USERS]
    
    GROUP_NAME = [i.rstrip() for i in random.sample(GROUP_NAME, amountGroup)]
    
    CONNECTION = []
    
    tmp_usr = USER_LOGIN.copy(); random.shuffle(tmp_usr)
    i = 0
    for j in tmp_usr:
        CONNECTION.append(GROUP_NAME[i % amountGroup] + ':' + j)
        i += 1
    for j in random.sample(tmp_usr, amountConnection - amountUsers):
        y = random.choice(GROUP_NAME) + ':' + j
        while (y in CONNECTION):
            y = random.choice(GROUP_NAME) + ':' + j
        CONNECTION.append(y) 

    # Запись задания в соответствующий файл
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
         pickle.dump([USER_LOGIN, USER_NAME, GROUP_NAME, CONNECTION], fil)
    
    #ДЛЯ ТРЕНИРОВКИ
    if train:
    
        try:
            os.mkdir('{}/.config/systemd/'.format(os.getenv('HOME')))
            os.mkdir('{}/.config/systemd/user/'.format(os.getenv('HOME')))
        except FileExistsError:
            pass
        # Создание юнитов systemd на проверку
        with open('/etc/trainerIBOS/units/Lab1.path', 'r') as r, open('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format(NAME_DOCKER_VM_VOLUME))

        with open('/etc/trainerIBOS/units/Lab1.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab1hint.py'))

        # Иницилизация юнитов systemd
        os.system('systemctl --user daemon-reload')
        os.system('systemctl --user start {}.path'.format(NAME_DOCKER_VM))
    
    #ДЛЯ ТРЕНИРОВКИ
    l = len(USER_LOGIN)
    USERS2 = ['{:<25}: {}'.format(USER_LOGIN[i], USER_NAME[i]) for i in range(l)]
    CONNECTION2 = ['{:<25}: {}'.format(i.split(':')[0],i.split(':')[1]) for i in CONNECTION]
    
    # Формирование задания.
    deskLab = "Задание:\n1.Создать пользователей c логинами:именами\n" + '\n'.join(USERS2) + '\n2.Создать группы\n' + '\n'.join(GROUP_NAME) + '\n3. Добавить в группы пользователей\n' + '\n'.join(CONNECTION2)
    return deskLab

def killTaskControlUserAndGroup(train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = NAME_DOCKER_VM + '_VOLUME'
    
    cont.remove(force=True)
    vol.remove(force=True)
    if train:
        os.system('systemctl --user stop {}.path'.format(NAME_DOCKER_VM))
        os.system('systemctl --user stop {}.service'.format(NAME_DOCKER_VM))
        os.system('systemctl --user daemon-reload')
        os.remove('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM))
        os.remove('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM))
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def startChmodLab(diff, train): # Первое задание на создание групп и пользователей
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    NAME_DOCKER_VM_VOLUME_TWO = 'trainerIBOS_VOLUME_mnt'
    
    USER_LOGIN = []
    GROUP_NAME = []
    DIR_NAME = []
    amountUsers = 4 if diff == 0 else 6 #4 6 6
    amountGroup = 2 if diff == 0 else 3 #2 3 3
    amountDir = 3 if diff == 0 else 4 #3 4 4
    
    # Создание задания
    with open('/etc/trainerIBOS/desc/Lab2/Lab2-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            USER_LOGIN.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            GROUP_NAME.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            DIR_NAME.append(fil.readline())
    
    USERS = [i.rstrip() for i in random.sample(USER_LOGIN, amountUsers)]
    GROUPS = [i.rstrip() for i in random.sample(GROUP_NAME, amountGroup)]
    DIRS = [i.rstrip() for i in random.sample(DIR_NAME, amountDir)]
    
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, USERS, GROUPS, DIRS], fil)
    
    #ДЛЯ ТРЕНИРОВКИ
    if train:
        pass
    
    sokor_USER = ['u'+str(i+1) for i in range(amountUsers)]
    sokor_GROUP = ['g'+str(i+1)for i in range(amountGroup)]
    sok_USER = ['u'+str(i+1) + ' : ' + USERS[i] for i in range(amountUsers)]
    sok_GROUP = ['g'+str(i+1) + ' : ' + GROUPS[i] for i in range(amountGroup)]
    USER_GROUP = ['{:<30}{}'.format(USERS[i], GROUPS[i // 2]) for i in range(amountUsers)]
    first_table = '{:<30}{:<10}{:<10}{}'.format('Каталог', 'Владелец', 'Группа', 'Остальные') + '\n'
    first_table = first_table + '\n'.join(['{:<30}{:<10}{:<10}{}'.format(i, 'rwx', 'r-x', '---') for i in DIRS])
    USER_DIR = ['{:<30}{}'.format(USERS[i*2], DIRS[i]) for i in range(amountDir-1)]
    GROUP_DIR = ['{:<30}{}'.format(GROUPS[i], DIRS[i]) for i in range(amountDir-1)]
    tmp = '{:<24}' + '{:<4}' * (6 if diff == 0 else 9)
    
    second_table = tmp.format('Каталог', *sokor_USER, *sokor_GROUP) + '\n'
    
    if diff == 2:
        prava = ['-w-'] +  ['   ' for i in range(amountUsers-1)] +  ['r-x' for i in range(amountGroup)]
        second_table = second_table + tmp.format(DIRS[-1], *prava) + '\n'
        prava = ['   ', '   ', '   ', 'rwx'] +  ['   ' for i in range(amountUsers-4)] + ['   ', 'r--'] +  ['   ' for i in range(amountGroup-2)]
        second_table = second_table + tmp.format(DIRS[0], *prava) + '\n'
        prava = ['   ', 'rwx'] +  ['   ' for i in range(amountUsers-2)] + ['r--'] +  ['   ' for i in range(amountGroup-1)]
        second_table = second_table + tmp.format(DIRS[1], *prava) + '\n'
        
        prava = []
        for i in range(amountUsers//2):
            prava.append('rw-')
            prava.append('r--')
        for i in range(amountGroup):
            prava.append('r--' if i % 2 == 0 else 'rw-')
        second_table = second_table + tmp.format(DIRS[-1] + '/text.txt', *prava) + '\n'
        prava = ['   ', '   ', 'r--', 'rw'] +  ['   ' for i in range(amountUsers-4)] +  ['   ' for i in range(amountGroup)]
        second_table = second_table + tmp.format(DIRS[0] + '/text.txt', *prava) + '\n'
        prava = ['r--', 'rw-'] +  ['   ' for i in range(amountUsers-2)] + ['   ' for i in range(amountGroup)]
        second_table = second_table + tmp.format(DIRS[1] + '/text.txt', *prava) + '\n'
    
    
    global cont
    global vol
    global vol2
    
    vol = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME)
    vol2 = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME_TWO)
    
    #volumes_dict = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME:{'bind':'/etc','mode':'rw'}, NAME_DOCKER_VM_VOLUME_TWO:{'bind':'/mnt','mode':'rw'}}
    volumes_dict = {NAME_DOCKER_VM_VOLUME:{'bind':'/etc','mode':'rw'}, NAME_DOCKER_VM_VOLUME_TWO:{'bind':'/mnt','mode':'rw'}}
    
    cont = clientDocker.containers.run('bos/debian2', '/bin/bash', detach=True, name=NAME_DOCKER_VM, hostname='chmodLab', volumes=volumes_dict, remove=True, tty = True)
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    
    #cont = clientDocker.containers.run('ibst/bos/debian2', detach=True, name=NAME_DOCKER_VM, hostname='chmodLab',volumes=volumes_dict, privileged=True, remove=True)
    
    #os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    
    
    if train:
    
        try:
            os.mkdir('{}/.config/systemd/'.format(os.getenv('HOME')))
            os.mkdir('{}/.config/systemd/user/'.format(os.getenv('HOME')))
        except FileExistsError:
            pass
        # Создание юнитов systemd на проверку
        with open('/etc/trainerIBOS/units/Lab2.path', 'r') as r, open('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format(NAME_DOCKER_VM_VOLUME, NAME_DOCKER_VM_VOLUME_TWO, DIRS[0], DIRS[1], DIRS[2], DIRS[3] if amountDir == 4 else ''))

        with open('/etc/trainerIBOS/units/Lab2.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab2hint.py'))

        # Иницилизация юнитов systemd
        os.system('systemctl --user daemon-reload')
        os.system('systemctl --user start {}.path'.format(NAME_DOCKER_VM))
    
    
    
    with open('/etc/trainerIBOS/start_script.sh', 'w') as stsc:
        stsc.write('#/bin/bash\n')
        for i in USERS:
            stsc.write('useradd -s /bin/bash {}\n'.format(i))
        for i in GROUPS:
            stsc.write('addgroup {}\n'.format(i))
        for i in DIRS:
            stsc.write('mkdir /mnt/{}\n'.format(i))
            stsc.write('touch /mnt/{}/text.txt\n'.format(i))
        
    copy_to('/etc/trainerIBOS/start_script.sh', '{}:/home/start_script.sh'.format(NAME_DOCKER_VM))
    cont.exec_run('chmod 777 /home/start_script.sh')
    cont.exec_run('sh /home/start_script.sh')
    os.remove('/etc/trainerIBOS/start_script.sh')
    
    #Создание вопросов
    que = []
    que.append(['Может ли просмотреть содержимое каталога {} пользователь {} (POSIX ACL - не учитывается)?'.format(DIRS[1], USERS[3]),                           ['Да', 'Нет'],                      'Да'])
    que.append(['Какой из пользователей не может просматривать содержимое каталога {} (POSIX ACL - не учитывается)?'.format(DIRS[-2]),                           [USERS[-1], USERS[-2], USERS[-3]],   USERS[-3]])
    que.append(['При доступе пользователя {} к каталогу {} по каким правам доступа он будет допущен (POSIX ACL - не учитывается)?'.format(USERS[1], DIRS[0]),    ['Владелец', 'Группа', 'Остальные'],'Группа'])
    if diff == 2:
        que.append(['Может ли просмотреть содержимое каталога {} пользователь {} (с учетом POSIX ACL)?'.format(DIRS[-1], USERS[0]),                           ['Да', 'Нет'],                      'Нет'])
        que.append(['Может ли просмотреть содержимое файла {}/text.txt пользователь {} (с учетом POSIX ACL)?'.format(DIRS[-1], USERS[0]),                           ['Да', 'Нет'],                      'Да'])
        que.append(['Может ли просмотреть содержимое файла {}/text.txt пользователь {} (с учетом POSIX ACL)?'.format(DIRS[-1], USERS[1]),                           ['Да', 'Нет'],                      'Да'])
        que.append(['Может ли просмотреть содержимое каталога {} пользователь {} (с учетом POSIX ACL)?'.format(DIRS[-1], USERS[1]),                           ['Да', 'Нет'],                      'Да'])
        que.append(['Может ли изменить содержимое файла {}/text.txt пользователь {} (с учетом POSIX ACL)?'.format(DIRS[-1], USERS[0]),                           ['Да', 'Нет'],                      'Нет'])
        que.append(['Может ли изменить и просмотреть содержимое файла {}/text.txt пользователь {} (с учетом POSIX ACL)?'.format(DIRS[0], USERS[3]),                           ['Да', 'Нет'],                      'Да'])
        que.append(['Кто из пользователей имеет доступ к каталогу {} (с учетом POSIX ACL)?'.format(DIRS[-1]),                           ['Все', 'Никто', USERS[0], USERS[1], USERS[3], USERS[4]],                      'Все'])
        que.append(['Может ли пользователь {} просмотреть содержимое каталога {} (с учетом POSIX ACL)?'.format(USERS[2], DIRS[0]),                           ['Да', 'Нет'],                      'Да'])
        que.append(['Может ли пользователь {} просмотреть содержимое файла {}/text.txt (с учетом POSIX ACL)?'.format(USERS[2], DIRS[0]),                           ['Да', 'Нет'],                      'Нет'])
        que.append(['Какой командой можно просмотреть настроенные права POSIX ACL?',    ['setfacl','ls -a', 'ls -l', 'getfacl'],'getfacl'])
        que.append(['Какой параметр команды setfacl позволяет удалить все настроенные ACL-права?',    ['-b','-a', '-x', '-R'],'-b'])
        que.append(['Какой параметр команды setfacl позволяет удалить конкретные ACL-права?',    ['-b','-a', '-x', '-R'],'-x'])
        
    que.append(['Кто может просмотреть содержимое каталога {} (POSIX ACL - не учитывается)?'.format(DIRS[-1]),    ['Все', 'Никто', USERS[0], USERS[1], USERS[2], USERS[3]],'Никто'])
    que.append(['Какой командой можно просмотреть настроенные права файлов в каталоге?',    ['ls -l','ls -a','ls','chmod', 'chown', 'chgrp'],'ls -l'])
    que.append(['Какой параметр команд настройки прав доступа используется для рекурсивной настройки прав вложенных подпапок и файлов?',    ['-b','-a', '-l', '-R'],'-R'])
    que.append(['Что означают права 750?',    ['rwxr-x---','rwxrwx---', '---r-xrwx', 'rw-------'],'rwxr-x---'])
    que.append(['Что означают права 410?',    ['rw---x---','r----x---', '---r-x---', 'rw-------'],'r----x---'])
    que.append(['Что означают права 123?',    ['-wx-w----','rwxr-x---', '-----x-wx', '--x-w--wx'],'--x-w--wx'])
                
    
    
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump(random.sample(que, 6), fil)
    
    
    
    if diff != 2:
        deskLab = 'Все необходимые пользователи и группы уже созданы.\nЗадание:\n1.Добавить пользователей в группы (пользователь:группа):\n' + '\n'.join(USER_GROUP) + '\n2.Назначить права доступа по следующей матрице доступа:\n' + first_table + '\n3. Назначить следующих владельцев для каталогов:\n' + '\n'.join(USER_DIR) + '\nНазначить следующие группы для каталогов:\n' + '\n'.join(GROUP_DIR)+ '\n4.Проверить назначенные права за каждого пользователя. (Данный пункт проверяется перечнем вопросов в конце работы).'  
    else:
        deskLab = 'Все необходимые пользователи и группы уже созданы.\nЗадание:\n1.Добавить пользователей в группы (пользователь:группа):\n' + '\n'.join(USER_GROUP) + '\n2.Назначить права доступа по следующей матрице доступа:\n' + first_table + '\n3. Назначить следующих владельцев для каталогов:\n' + '\n'.join(USER_DIR) + '\nНазначить следующие группы для каталогов:\n' + '\n'.join(GROUP_DIR)+ '\n4.Проверить назначенные права за каждого пользователя. (Данный пункт проверяется перечнем вопросов в конце работы).\n5.Сокращения пользователей:\n' + '\n'.join(sok_USER) + '\nСокращение групп:\n' + '\n'.join(sok_GROUP) + '\nНазначить следующие ACL права на файлы и каталоги:\n' + second_table + '6. Проверить назначенные права для каждого пользователя. (Данный пункт проверяется перечнем вопросов в конце работы).'                              
    return deskLab
    ##/bin/bash

def killChmodLab(train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = NAME_DOCKER_VM + '_VOLUME'
    global cont; global vol; global vol2
    cont.remove(force=True)
    
    vol.remove(force=True)
    vol2.remove(force=True)
    
    if train:
        os.system('systemctl --user stop {}.path'.format(NAME_DOCKER_VM))
        os.system('systemctl --user stop {}.service'.format(NAME_DOCKER_VM))
        os.system('systemctl --user daemon-reload')
        os.remove('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM))
        os.remove('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM))
    
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'rb') as fil:
        que = pickle.load(fil)
    dopProcent = 30.0
    os.remove('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM))
    return dopProcent, que
    
    
def startSystemdLab(diff, train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    
    global cont; global vol; global vol2
    
    vol = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME)
    
    volumes_dict = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME:{'bind':'/root','mode':'rw'}}
    
    cont = clientDocker.containers.run('bos/debian3', detach=True, name=NAME_DOCKER_VM, hostname='systemdLab',volumes=volumes_dict, privileged=True, remove=True, environment=['PROMPT_COMMAND=history -a'])
    
    #----------------------------------============================  Формирование и сохранение задания  ----------------------------------============================
    
    SYSTEMD_NAME = []
    SYSTEMD_NAMEofDESC = []
    TYPE_UNIT = []
    amountSystemdName = 6
    amountSystemdNameofDesc = 3
    amountTypeUnit = 2
    
    # Создание задания
    with open('/etc/trainerIBOS/desc/Lab3/Lab3-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            SYSTEMD_NAME.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            SYSTEMD_NAMEofDESC.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            TYPE_UNIT.append(fil.readline())
    
    SYSTEMD_NAME = [i.rstrip() for i in random.sample(SYSTEMD_NAME, amountSystemdName)]
    SYSTEMD_NAMEofDESC = [[i.split('=')[0], i.split('=')[1].rstrip()] for i in random.sample(SYSTEMD_NAMEofDESC, amountSystemdNameofDesc)]
    TYPE_UNIT = [i.rstrip() for i in random.sample(TYPE_UNIT, amountTypeUnit)]
    
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, SYSTEMD_NAME, SYSTEMD_NAMEofDESC, TYPE_UNIT], fil)
    
    #----------------------------------============================  Формирование и сохранение задания  ----------------------------------============================
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    # PROMPT_COMMAND=history -a
    
    
    
    que = []
    que.append(['Какой командой можно запустить службу?',                                              ['start', 'enable', 'go', 'run'],        'start'])
    que.append(['Какой командой можно просмотреть все активные модули?',                               ['ls','shows-units','list','list-units'],      'list-units'])
    que.append(['Какой командой можно просмотреть зависимости модулей?',                               ['systemctl status','systemctl list-units --addict','systemctl state',' systemctl addictions'],    'systemctl status'])
    que.append(['Какой командой можно активировать автовключение модуля?',                             ['start','go','auto-on','enable'],      'enable'])
    que.append(['Какой командой можно перезапустить модуль?',                                          ['re','restart','relol','rerun'],      'restart'])
    que.append(['Какой флаг нужен для вывода модулей по типу?',                                        ['--type','--kind','--cast','--class'],      '--type'])
    que.append(['Какого типа модулей нет в systemd?',                                                  ['path','mount','target','file'],      'file'])
    que.append(['Какой тип модулей может использоваться для отложенного запуска приложений?',          ['service','time','comm-time','timer'],      'timer'])
    que.append(['Какой раздел может быть в каждом юните systemd?',                                              ['Service','Scope','Unit','Mount'],      'Unit'])
    que.append(['Какая команда должна быть введена после каждого изменения модулей для их корректной работы?',  ['restart-systemd','daemon-reload','restart-system','reload'],      'daemon-reload'])
    que.append(['Какой директивы нет для раздела [Service]?',                                          ['ExecStart','ExecStartPre','ExecRestart','ExecStop'],      'ExecRestart'])
    
    tmp_name = [i[0] for i in SYSTEMD_NAMEofDESC]
    tmp_desc = [i[1] for i in SYSTEMD_NAMEofDESC]
    
    que_dop = []
    for i in range(amountSystemdNameofDesc):
        que_dop.append(['Какому модулю соответствует данное описание: {}?'.format(tmp_desc[i]),tmp_name, tmp_name[i]])
    
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump(random.sample(que, 3) + que_dop, fil)
    
    
    #ДЛЯ ТРЕНИРОВКИ
    if train:
    
        try:
            os.mkdir('{}/.config/systemd/'.format(os.getenv('HOME')))
            os.mkdir('{}/.config/systemd/user/'.format(os.getenv('HOME')))
        except FileExistsError:
            pass
        # Создание юнитов systemd на проверку
        with open('/etc/trainerIBOS/units/Lab3.path', 'r') as r, open('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format(NAME_DOCKER_VM_VOLUME))

        with open('/etc/trainerIBOS/units/Lab3.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab3hint.py'))

        # Иницилизация юнитов systemd
        os.system('systemctl --user daemon-reload')
        os.system('systemctl --user start {}.path'.format(NAME_DOCKER_VM))
    
    #ДЛЯ ТРЕНИРОВКИ
    
    
    
    deskLab = '''1. Проверка статуса служб:
1.1 Проверить статус следующих служб:

{0}

1.2 Проверить активность следующих служб (с помощью соответствующей команды):

{1}

1.3 Проверить автоквключение и успешность их выполнения следующих служб:

{2}

2. Обзор состояния системы:
2.1 Вывести список активных служб на экран.
2.2 Вывести список всех служб на экран.
2.3 Вывести список активных служб следующих типов:

{3}

2.4 Найти имена служб по следующим описаниям (например, с помощью утилиты grep):

{4}

Обратите внимание!!! Проверка пункта 2.4 не выполняется автоматически. Вместо этого в конце работы будут заданы вопросы, в которых необходимо сопоставить описание службы и её имени.
2.5 Вывести все зависимости служб.
3. Работа со службами:
3.1 Отключите службу, проверьте её активность соответствующей командой, после чего включите службу {5}.
3.2 Перезапустите службу {6}, после чего проверьте её активность.
3.3 Отключите автовключение службы, проверьте автовключение соответствующей командой, после чего включите автовключение службы и проверьте соответствующей командой. Наименование службы: {7}.
4. Создайте свою службу (.service) с именем:
    TaskService.service;
для программы programm1, которая находится в папке /mnt. В этой же папке для этой программы есть текстовый файл-инструкция readme1. Запустите данную службу. Проверьте её работу. Проверьте наличие новой службы в перечне активных служб.
'''.format('\n'.join(SYSTEMD_NAME[0:2]),'\n'.join(SYSTEMD_NAME[2:4]), '\n'.join(SYSTEMD_NAME[4:]), '\n'.join(TYPE_UNIT), '\n'.join([i[1] for i in SYSTEMD_NAMEofDESC]), SYSTEMD_NAME[0], SYSTEMD_NAME[2], SYSTEMD_NAME[4])
    if diff > 0:
        deskLab = deskLab + '''5. Создайте свой юнит .timer и соотвутствующий юнит .service c именами:
    TaskTimer.timer;
    TaskTimer.service;
которые должны каждые 10 секунд запускать программу programm2, которая находится в папке /mnt. В этой же папке для этой программы есть текстовый файл-инструкция readme2. Запустите данную службу. Проверьте её работу. Проверьте наличие новой службы в перечне служб.
'''
    if diff == 2:
        deskLab = deskLab + '''6. Создайте свой юнит .path и соотвутствующий юнит .service с именами:
    TaskPath.path;
    TaskPath.service;
которые при изменении файла /mnt/text.txt (данный файл необходимо создать) должны запускать программу programm3, которая находится в папке /mnt. В этой же папке для этой программы есть текстовый файл-инструкция readme3. Запустите данную службу. Проверьте её работу. Проверьте наличие новой службы в перечне служб.
'''
    
    return deskLab
    
def killSystemdLab(train):
    NAME_DOCKER_VM = 'trainerIBOS'
    global cont; global vol
    cont.remove(force=True)
    vol.remove(force=True)
    
    if train:
        os.system('systemctl --user stop {}.path'.format(NAME_DOCKER_VM))
        os.system('systemctl --user stop {}.service'.format(NAME_DOCKER_VM))
        os.system('systemctl --user daemon-reload')
        os.remove('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM))
        os.remove('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM))
    
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'rb') as fil:
        que = pickle.load(fil)
    dopProcent = 30.0
    os.remove('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM))
    return dopProcent, que


def startNetworkLab(diff, train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    
    NAME_DOCKER_VM2  = 'trainerIBOS2'
    
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    NAME_DOCKER_VM_VOLUME2 = 'trainerIBOS_VOLUME2'
    
    IP_ADDRS=[]
    TABLE_NAMES=[]
    MAIN_CHAINS_NAMES=[]
    SECOND_CHAINS_NAMES=[]
    DROP_NAMES=[]
    PREFIXS=[]
    MAC_ADDRS=[]
    
    
     # Создание задания
    with open('/etc/trainerIBOS/desc/Lab4/Lab4-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            IP_ADDRS.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            TABLE_NAMES.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            MAIN_CHAINS_NAMES.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            SECOND_CHAINS_NAMES.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            DROP_NAMES.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            PREFIXS.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            MAC_ADDRS.append(fil.readline())
    
    ip_addr = random.choice(IP_ADDRS).rstrip()
    table = random.choice(TABLE_NAMES).rstrip()
    main_chain = random.choice(MAIN_CHAINS_NAMES).rstrip()
    second_chain = random.choice(SECOND_CHAINS_NAMES).rstrip()
    drop_protocol = random.choice(DROP_NAMES).rstrip()
    prefix = random.choice(PREFIXS).rstrip()
    prefix_drop=prefix.split(':')[0]
    prefix_accept=prefix.split(':')[1]
    mac_addr = random.choice(MAC_ADDRS).rstrip()
    
    global cont; global vol; global vol2; global cont2
    
    vol = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME)
    vol2 = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME2)
    
    volumes_dict = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME:{'bind':'/root','mode':'rw'}, NAME_DOCKER_VM_VOLUME2:{'bind':'/mnt', 'mode':'rw'}}
    
    cont = clientDocker.containers.run('bos/debian4', detach=True, name=NAME_DOCKER_VM, hostname='NetworkLabNum4',volumes=volumes_dict, privileged=True, remove=True, environment=['PROMPT_COMMAND=history -a'])
    
    cont.exec_run('ip link set dev eth0 down')
    cont.exec_run('mkdir /run/ulog')
    cont.exec_run('touch /run/ulog/ulogd.pid')
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, ip_addr, table, main_chain, second_chain, drop_protocol, prefix_drop, prefix_accept, mac_addr, [0]], fil)
    
    
    try:
        os.mkdir('{}/.config/systemd/'.format(os.getenv('HOME')))
        os.mkdir('{}/.config/systemd/user/'.format(os.getenv('HOME')))
    except FileExistsError:
        pass
    
    with open('/etc/trainerIBOS/units/Lab4.path', 'r') as r, open('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
        w.write(r.read().format(NAME_DOCKER_VM_VOLUME))
    
    if train:
        with open('/etc/trainerIBOS/units/Lab4train.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab4hint.py', '/etc/trainerIBOS/script/Lab4tmp.py'))
    else:
        with open('/etc/trainerIBOS/units/Lab4No.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab4tmp.py'))

        # Иницилизация юнитов systemd
    os.system('systemctl --user daemon-reload')
    os.system('systemctl --user start {}.path'.format(NAME_DOCKER_VM))
    
    
    
    deskLab = '''1. Управление IP-адресами, интерфейсами и таблицей маршрутизации:
1.1 Просмотреть IP-адрес интерфейса eth0.
1.2 Удалить  IP-адрес 172.17.0.2.
1.3 Добавить к данному интерфейсу eth0 IP-адрес {0}.
1.4 Включить интерфейс eth0.
1.5 Проверить состояние интерфейса eth0.
1.6 Проверить таблицу маршрутизации.
2. Добавление таблицы и цепочек межсетевого экрана nftables:
2.1 Добавьте таблицу {1} семейства ip (ipv4):
2.2 Добавьте в созданную таблицу цепочки {2} и {3}.
Цепочка {2} должна иметь тип filter, хук input, приоритет 0, политику accept.
3. Добавьте правила фильтрации для входящих пакетов в цепочку {2}, чтобы пакеты {4} не проходили межсетевой экран.
Добавьте логирование, используя цепочку {3} для логирования принятых пакетов с префиксом {5} и отброшенных пакетов с префиксом {6}.
Цепочка {2} должна содержать правило перехода на цепочку {3} в случае, если входящий пакет {4}, а также правило логирования принятых пакетов.
Цепочка {3} должна содержать правило логирования не легитимных пакетов ({4}), а также правило отбрасывания таких пакетов.
Логи должны записываться в файл /mnt/log_network_lab.log с помощью системы ulogd. 
4. Проверьте настроенные правила с помощью утилиты hping3, отправляя пакеты с хост-системы (ОС компьютера) на адрес {0}.
Проверьте, что файл /mnt/log_network_lab.log имеет необходимые записи.
'''.format(ip_addr, table, main_chain, second_chain, drop_protocol, prefix_accept, prefix_drop)
    if diff >= 1:
        deskLab = deskLab + '''5. Удалить из цепочки {1} правило перехода на цепочку {0}. Удалить цепочку {0}. Проверить, что теперь весь трафик попадает в систему.
'''.format(second_chain, main_chain)
    if diff == 2:
        deskLab = deskLab + '''6. Просмотрите ARP-таблицу в хост системе. Просмотрите информацю о интерфейсах в контейнере NetWorkLabNum4. Замените MAC-адрес интерфеса eth0 в контейнере на {}.
Отправьте несколько ICMP-запросов с хост системы в контейнер. Просмотрите ARP-таблицу.
'''.format(mac_addr)
    
    
    que = []
    que.append(['Какой командой можно просмотреть IP-адреса, которые связаны с сетевыми интерфейсами компьютера?',['ip a', 'ip adr', 'ip show', 'ip show address'],        'ip a'])
    que.append(['Как просмотреть IP адреса, только по конкретному интерфейса, например, интерфейса eth0?',['ip show eth0','ip a show dev eth0','ip link','ip link eth0'],      'ip a show dev eth0'])
    que.append(['Какой командой можно просмотреть список интерфейсов?',                                ['ip show link','ip sh','ip li','ip links'],    'ip li'])
    que.append(['Какой командой можно отключить интерфейс?',                                           ['ip','ip link','ip l down enp0s3','ip link set dev enp0s3 down'],      'ip link set dev enp0s3 down'])
    
    que.append(['Какая команда утилиты ip может использоваться для управления таблицей маршрутизации?',['addr','routable','link','route'],      'route'])
    que.append(['Какая команда утилиты ip может использоваться для управления ARP-таблицей?',          ['trp','hping','neigh','arp'],      'neigh'])
    
    que.append(['Какая команда утилиты ip может использоваться для установки MAC-адреса интерфейсу?',  ['addr','routable','link','route'],      'link'])
    que.append(['Какая система фильтрации пакетов рассматривалась в данной работе?',  ['nftables','nft','iptable','chains', 'ip'],      'nftables'])
    que.append(['Какое семейство объединяет протоколы IPv4 и IPv6?',  ['inet','IPv4-6','ipv4','ip', 'ip4v6', 'intern'],      'inet'])
    que.append(['Какое семейство применяется для фильтрации пакетов IP версии 4?',  ['inet','IPv4','ipv4','ip', 'ip4v6'],      'ip'])
    que.append(['Какая команда утилиты nft используется для просмотра настроенных элементов?',  ['list','show','sh','check', 'elements'],      'list'])
    que.append(['Какая концепция элементов используетсяв nftables?',  ['Слои, цепочки, правила','Таблица, правила','Слои, правила', 'Таблицы, цепочки, правила'],      'Таблицы, цепочки, правила'])
    que.append(['Какой параметр цепочки указывает направление обрабатываемых пакетов?',  ['type','policy','priority','hook', 'accept'],      'hook'])
    que.append(['Какая команда утилиты nft используется для стирания всех правил в таблице/цепочке?',  ['del','flush','delete','remove', 'rm'],      'flush'])
    que.append(['Какие ключевые слова могут использоваться для перехода на другую цепь с текущего правила?',  ['jmp/goto','to/goto','goto','jump', 'to', 'jump/goto', 'jmp', 'transit/jmp', 'transit'],      'jump/goto'])
    
    que.append(['Какого решения к пакету нет в nftables?',  ['drop','jump','accept','break'],      'break'])
    que.append(['Какая система используется для записи логов в файл?',  ['ulogd','logd','ulog','loggin', 'logger', 'ul'],      'ulogd'])
    
    que.append(['Какой набор аргументов может использоваться для параметра ip при создании правила?',  ['protocol, saddr, daddr','saddr, sport, protocol','sport, dport','protocol, version', 'saddr, daddr, dport, sport'],      'protocol, saddr, daddr'])
    
    que.append(['Как добавить правило НЕ в конец цепочки, а после другого правила?',  ['Используя handle','Нельзя добавить правила НЕ в конец цепочки','Используя ulogd','Используя fish',],      'Используя handle'])
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump(random.sample(que, 6), fil)
    
    return deskLab

def killNetworkLab(train):
    NAME_DOCKER_VM = 'trainerIBOS'
    global cont; global vol; global vol2; global cont2
    cont.remove(force=True)
    vol.remove(force=True)
    vol2.remove(force=True)
    
    os.system('systemctl --user stop {}.path'.format(NAME_DOCKER_VM))
    os.system('systemctl --user stop {}.service'.format(NAME_DOCKER_VM))
    os.system('systemctl --user daemon-reload')
    os.remove('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM))
    os.remove('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM))
    
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'rb') as fil:
        que = pickle.load(fil)
    dopProcent = 20.0
    os.remove('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM))
    return dopProcent, que
    
def startJournalLab(diff, train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    global cont; global vol; global vol2; global cont2
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    
    USERS = []
    APT_PR = []
    SERV = []
    PRIOR = [3,4,5,6,7]
   
    with open('/etc/trainerIBOS/desc/Lab5/Lab5-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            USERS.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            APT_PR.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            SERV.append(fil.readline())
    
    user = random.choice(USERS).rstrip()
    apt_get = random.choice(APT_PR).rstrip()
    service = random.choice(SERV).rstrip()
    priority = random.choice(PRIOR)
    
    
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([diff, user, apt_get, service, priority], fil)
    
    vol = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME)
    
    volumes_dict = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME:{'bind':'/root','mode':'rw'}}
    
    
    cont = clientDocker.containers.run('bos/debian5', detach=True, name=NAME_DOCKER_VM, hostname='JournalLABS',volumes=volumes_dict, privileged=True, remove=True, environment=['PROMPT_COMMAND=history -a'])
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM))
    
    #ДЛЯ ТРЕНИРОВКИ
    if train:
    
        try:
            os.mkdir('{}/.config/systemd/'.format(os.getenv('HOME')))
            os.mkdir('{}/.config/systemd/user/'.format(os.getenv('HOME')))
        except FileExistsError:
            pass
        # Создание юнитов systemd на проверку
        with open('/etc/trainerIBOS/units/Lab5.path', 'r') as r, open('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format(NAME_DOCKER_VM_VOLUME))

        with open('/etc/trainerIBOS/units/Lab5.service', 'r') as r, open('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM), 'w+') as w:
            w.write(r.read().format('/etc/trainerIBOS/script/Lab5hint.py'))

        # Иницилизация юнитов systemd
        os.system('systemctl --user daemon-reload')
        os.system('systemctl --user start {}.path'.format(NAME_DOCKER_VM))
    
    #ДЛЯ ТРЕНИРОВКИ
    
    
    
    
    deskLab = '''======!!!ЗАМЕЧАНИЕ!!!====== 
В данной работе не изменяйте текущий каталог! Оставайтесь в корне системы. Это необходимо для корректной проверки выполнения задания.
======!!!ЗАМЕЧАНИЕ!!!======
    
1. Работа с системными журналами:
1.1 Просмотрите журналы в каталоге /var/log.
1.2 Просмотрите записи журналов syslog и messages утилитами cat и tail.
1.3 Просмотрите файл конфигурации rsyslog.conf, рассмотрите основные настройки.
2. Анализ журнала auth.log.
2.1 Добавьте нового пользователя {0}.
2.2 Выполните вход пользователя {0} в систему.
2.3 Вернитесь к суперпользователю root. Просмотрите наличие журнала auth.log в каталоге /var/log. Просмотрите данный журнал.
3. Анализ журнала apt/history.log.
Проанализируте журнал apt/history.log. Найдите информацию о установке утилиты {1}. Об установке данной утилиты будут заданы вопросы.
4. Управление журналами systemd - journald.
4.1 Просмотр журналов journald с помощью утилиты journalctl.
4.2 Просмотрите сообщения {2} приоритета.
4.3 Просмотрите сообщения за предыдущие 10 минут.
4.4 Просмотрите сообщения ядра.
4.5 Настройте постоянное хранение журналов journald. Установите максимальный размер 100 Мб.
'''.format(user, apt_get, priority)
    if diff >= 1:
        deskLab = deskLab + '''5. Проверьте размер журнала journald. Выполните команду, которая позволит оставить только журналы, которые младше 5 дней.
'''
    if diff == 2:
        deskLab = deskLab + '''6. Перезапустите демон systemd. Запустите сервис systemd {}. Данный сервис будет запущен с ошибкой. Решите проблему, из-за которой не запускается сервис. Запустите сервис, чтобы он успешно завершился.
'''.format(service)

    d = {'acl':'2','nano':'1','nftables':'4','tcpdump':'5','ulogd':'6'}

    que = []
    que.append(['Какая утилита не применяется для просмотра логов?',['cat', 'tail', 'check'],        'check'])
    que.append(['Какой параметр необходим для утилиты journalctl для просмотра сообщений ядра?',['-k', '-t', '-a', '-p kernel', '-p', '-u'],        '-k'])
    que.append(['Какой по счёту была установлена программа {}?'.format(apt_get),['2', '3', '4', '5', '6'],        d[apt_get]])
    que.append(['Указывается ли в журнале auth.log информация о создании пользователей?',['Да', 'Нет', 'Зависит от типа пользователя'],        'Да'])
    que.append(['Что указывается для сессий пользователя в журнале auth.log?',['Время начала и продолжительность', 'Время конца и продолжительность', 'Время начала и конца'],        'Время начала и конца'])
    que.append(['Какие параметры утилиты journalctl используется для фильтрации событий по дате/времени?',['--since/--until', '--date', '--dtime', '--before/--after', '--date-time', '--start/--end', '-d'],        '--since/--until'])
    que.append(['Как называется служба, которая контролирует журналирование journald?',['systemd-journalctl', 'journalctl', 'systemd-journald', 'systemd-journal', 'journald', 'journald-service'],        'systemd-journald'])
    que.append(['Какой флаг утилиты journalctl позволяет просмотреть события, связанные с службой systemd?',['-k', '-t', '-a', '-p', '-u'],        '-u'])
    que.append(['Каково назначение журнала apt/history.log',['Хронология установки программ', 'История команд, введенных в консоль', 'Хронология загрузки системы'],        'Хронология установки программ'])
    
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump(random.sample(que, 6), fil)


    return deskLab
    
def killJournalLab(train):
    NAME_DOCKER_VM = 'trainerIBOS'
    global cont; global vol; global vol2; global cont2
    cont.remove(force=True)
    vol.remove(force=True)
    if train:
        os.system('systemctl --user stop {}.path'.format(NAME_DOCKER_VM))
        os.system('systemctl --user stop {}.service'.format(NAME_DOCKER_VM))
        os.system('systemctl --user daemon-reload')
        os.remove('{0}/.config/systemd/user/{1}.path'.format(os.getenv('HOME'), NAME_DOCKER_VM))
        os.remove('{0}/.config/systemd/user/{1}.service'.format(os.getenv('HOME'), NAME_DOCKER_VM))
   
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'rb') as fil:
        que = pickle.load(fil)
    dopProcent = 30.0
    os.remove('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM))
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    return dopProcent, que   
   
def startSSHLab(diff, train):
    NAME_DOCKER_VM  = 'trainerIBOS'
    NAME_DOCKER_VM2  = 'IBOStrainer'
    
    USERS = []
    FRAZE = []
   
    with open('/etc/trainerIBOS/desc/Lab6/Lab6-names.conf', 'r') as fil:
        N = int(fil.readline())
        for i in range(N):
            USERS.append(fil.readline())
        N = int(fil.readline())
        for i in range(N):
            FRAZE.append(fil.readline())
    
    usr = random.sample(USERS, 2)
    userMain = usr[0].rstrip()
    userSecond = usr[1].rstrip()
    
    fraze = random.choice(FRAZE).rstrip()
    
    with open('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump([userMain, userSecond, fraze], fil)
    
    
    global cont; global vol; global vol2; global cont2; global net
    
    for netw in clientDocker.networks.list():
        if netw.name == 'network-lab':
            netw.remove()
    NAME_DOCKER_VM_VOLUME = 'trainerIBOS_VOLUME'
    NAME_DOCKER_VM_VOLUME2 = 'trainerIBOS_VOLUME2'      
    vol = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME)
    vol2 = clientDocker.volumes.create(NAME_DOCKER_VM_VOLUME2)
    
    volumes_dict = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME:{'bind':'/home','mode':'rw'}}
    volumes_dict2 = {'/sys/fs/cgroup':{'bind':'/sys/fs/cgroup','mode':'ro'}, NAME_DOCKER_VM_VOLUME2:{'bind':'/home','mode':'rw'}}
    
    net = clientDocker.networks.create("network-lab", driver="bridge")
    
    cont = clientDocker.containers.run('bos/debian6',  detach=True,  name=NAME_DOCKER_VM, hostname='remote-SSH-LABS-remote',volumes=volumes_dict, privileged=True, remove=True,  network='network-lab', environment=['PROMPT_COMMAND=history -a'])
    
    cont2 = clientDocker.containers.run('bos/debian6',  detach=True, name=NAME_DOCKER_VM2, hostname='SSH-LABS',volumes=volumes_dict2, privileged=True, remove=True, network='network-lab', environment=['PROMPT_COMMAND=history -a'])
    
    copy_to('/etc/trainerIBOS/desc/Lab6/scp-file', '{}:/home/scp-file.txt'.format(NAME_DOCKER_VM2))
    
    cont.exec_run('chmod -R 400 /etc/ssh')
    cont.exec_run('chmod -R 4755 /bin/su')
    cont2.exec_run('chmod -R 4755 /bin/su')
    cont2.exec_run('chmod -R 400 /etc/ssh')
    
    os.system('x-terminal-emulator -e docker exec -it {} bash'.format(NAME_DOCKER_VM2))
    
    deskLab = '''Имя текущей машины: SSH-LABS; Имя удаленной машины: remote-SSH-LABS-remote.
Пароль от root на удаленной и текущей машине: 123ibst789DEB
IP адрес удаленной машины отличается от IP адреса текущей машины лишь крайним правым октетом. Данный октет меньше на 1. (Просматривать интерфейс eth0).
Если адрес текущей машины: 123.123.123.3, то адрес удаленной машины: 123.123.123.2.

Создайте на основной машине пользователя {0} с домашним каталогом. Войдите в систему за этого пользователя. Все дальнейшие действия производите в сессии пользователя {0}.
    
С помощью scp скопируйте файл /home/scp-file с основной машины на удаленную машину с тем же именем.

Подключитесь к удаленной машине по ssh для пользователя root.

На удаленной машине создайте файл /home/MyPhrase.txt, в котором должна быть одна строка "{1}" (без кавычек).

Создайте пользователя {2} на удаленной машине с домашним каталогом.

Настройте автоматическую SSH-авторизацию по ключам для пользователей {0}->{2}.

Запретите доступ по паролю на удаленную машину. Запретите доступ root на удаленную машину. Проверьте заданные настройки.
'''.format(userMain, fraze, userSecond)
    
    que = []
    que.append(['Что означает аббревиатура SSH?',['Safety Shell', 'Security Shell', 'Secure Shell'],        'Secure Shell'])
    que.append(['Что такое SSH?',['Протокол безопасного удаленного доступа', 'Программа для удаленного доступа', 'Стандарт удаленного доступа'],        'Протокол безопасного удаленного доступа'])
    que.append(['Какое ПО в Linux отвечает за поддержку SSH?',['OpenSSH', 'ProgrammSSH', 'SecuritySSH', 'xSHH', 'RFC4251', 'mainSSH'],        'OpenSSH'])
    que.append(['Какое порт используется SSH по умолчанию?',['22', '60', '7', 'port-SSH', '81', 'port-remote', '75', 'port-telnet'],        '22'])
    que.append(['Как называется файл с конфигурацией для SSH?',[ 'ConfigFileSsh', 'ConfigFileSsh', 'ssh_config', 'ConfigFileSecurity', 'sshd.conf', 'ssh.conf', 'sshd_config'],        'sshd_config'])
    que.append(['С точки зрения безопасности запрет на удаленный root-доступ необходим?',[ 'Не имеет значения', 'Да', 'Нет'],        'Да'])
    que.append(['С точки зрения безопасности выбор стандартного порта для SSH-сервера оправдано?',[ 'Не имеет значения', 'Да', 'Нет'],        'Нет'])
    que.append(['С точки зрения безопасности ограничение списка IP-адресов, с которых разрешён доступ (например, с помощью nftables) оправдано?',[ 'Не имеет значения', 'Да', 'Нет'],        'Да'])
    que.append(['Какой параметр ssh позволяет удаленно подключиться к компьютеру с нестандартным портом сервера?',[ '-p', '-q', '-r', '-u', '-o', '-b', '-f'],        '-p'])
    que.append(['Какая команда генерирует пары ключей для аутентификации по ключам?',[ 'sshd-keygen', 'ssh-keygen', 'keygen-ssh', 'ssh-keys', 'sshd-keys', 'scp-keygen'],        'ssh-keygen'])
    que.append(['Какая утилита, работая по протоколу SSH, копирует файлы на удаленный компьютер?',[ 'scp', 'ssh-copy', 'ssc', 'ssh-keys', 'copy-sshd', 'scopyng'],        'scp'])
    que.append(['Какая утилита используется для переноса публичного ключа на удаленную машину?',[ 'ssh-copy-key', 'ssh-copy-id', 'ssh-copy-pub', 'ssh-pub-key', 'ssh-pub-copy', 'ssh-copy'],        'ssh-copy-id'])
    que.append(['После изменения файла конфигурации ssh необходимо ли перезагрузить службу ssh?',[ 'Необходимо', 'Не нужно перезагружать службу'],        'Необходимо'])
    que.append(['В каком файле можно изменить порт сервера ssh?',[ 'ConfigFileSsh', 'ConfigFileSsh', 'ssh_config', 'ConfigFileSecurity', 'sshd.conf', 'ssh.conf', 'sshd_config'],        'sshd_config'])
    que.append(['При удаленном доступе по SSH нужно именно IP-адрес удаленной машины?',[ 'Да, только IP-адрес', 'Нет, ещё можно по имени компьютера', 'Нет, ещё можно по PID компьютра'],        'Нет, ещё можно по имени компьютера'])
    
    
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'wb') as fil:
        pickle.dump(random.sample(que, 8), fil)
    
    return deskLab

def killSSHLab(train):
    NAME_DOCKER_VM = 'trainerIBOS'
    global cont; global vol; global vol2; global cont2; global net
    cont.remove(force=True)
    cont2.remove(force=True)
    vol.remove(force=True)
    vol2.remove(force=True)
    net.remove()
    with open('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM), 'rb') as fil:
        que = pickle.load(fil)
    dopProcent = 40.0
    os.remove('/etc/trainerIBOS/{}.question'.format(NAME_DOCKER_VM))
    os.remove('/etc/trainerIBOS/{}.task'.format(NAME_DOCKER_VM))
    return dopProcent, que  