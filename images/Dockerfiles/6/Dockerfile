FROM bos/debian5

RUN echo "root:123ibst789DEB" | chpasswd

RUN rm /mnt/*

RUN apt-get update && apt-get install openssh-server -y

RUN sed -E 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config -i && sed -E 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config -i &&  ssh-keygen -A