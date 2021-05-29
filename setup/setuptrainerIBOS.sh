#/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "Данный скрипт должен быть запущен от пользователя root" 
   echo "This script must be run as root"
   exit 1
fi
echo "Требуется установить тренажер или программу централизованного управления тьютор? Для установки тренажера введите 'trainer', а для установки программы управления 'tutor'."
echo "Need to install a trainer or centralized management program? Enter 'trainer' to install the trainer, and 'tutor' to install the control program."
read enterText
if [ "$enterText" = "trainer" ]; then   #-------------------trainer  
echo "Установка / обновления python3 и PyQt5"
echo "Installing / upgrading python3 and PyQt5"
sudo apt install python3 -y;
sudo apt install python3-pyqt5 -y;
sudo apt install python3-docker -y;
sudo apt install curl -y;
echo "Установка / обновления docker"
echo "Installing / upgrading docker"
curl https://get.docker.com > /tmp/install.sh
chmod +x /tmp/install.sh
/tmp/install.sh
rm /tmp/install.sh
echo "Создание группы trainerIBOS и каталога в /etc/trainerIBOS/"
echo "Creating the trainerIBOS group and directories in /etc/trainerIBOS/"
sudo addgroup traineribos
mkdir /etc/trainerIBOS
chmod -R g+rwx /etc/trainerIBOS
sudo chgrp -R traineribos /var/lib/docker
sudo chgrp -R traineribos /var/lib/docker/volumes
chmod  g+rwx /var/lib/docker
chmod  g+rwx /var/lib/docker/volumes
echo "Копирование конфигурационных файлов, создание службы systemd"
echo "Copy conf files"
cp -r ./desc/ /etc/trainerIBOS/
cp -r ./script/ /etc/trainerIBOS/
cp -r ./units/ /etc/trainerIBOS/
cp ./port_time.conf /etc/trainerIBOS/
cp ./check_images.conf /etc/trainerIBOS/
cp ./trainerright.path /etc/systemd/system/
cp ./trainerright.service /etc/systemd/system/
sudo chgrp -R traineribos /etc/trainerIBOS
chmod -R g+rwx /etc/trainerIBOS
systemctl daemon-reload
systemctl enable trainerright.path
systemctl start trainerright.path
echo "Установка завершена. Добавьте пользователей в группы docker и traineribos"
echo "End setup. Add users to groups docker and traineribos"
exit 0
elif [ "$enterText" = "tutor" ]; then #-------------------trainer  
echo "Установка / обновления python3, PyQt5 и paramiko (scp)"
echo "Installing / upgrading python3, PyQt5 and paramiko (scp)"
sudo apt install python3 -y;
sudo apt install python3-pyqt5 -y;
sudo apt install python3-paramiko -y;
sudo apt install python3-scp -y;
echo "Создание каталога /etc/trainerIBOStutor"
echo "Creating directories /etc/trainerIBOStutor"
sudo addgroup traineribos
mkdir /etc/trainerIBOStutor
touch /etc/trainerIBOStutor/tutorset.conf
sudo chgrp -R traineribos /etc/trainerIBOStutor/tutorset.conf
chmod  ug+rwx /etc/trainerIBOStutor/tutorset.conf
echo "Установка завершена. Добавьте адреса в файл конфигурации /etc/trainerIBOStutor/tutorset.conf"
echo "End setup. Add address to file conf /etc/trainerIBOStutor/tutorset.conf"
else
echo "Неверный ввод команды"
echo "Invalid command"
fi