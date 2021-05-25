FROM bos/debian4

COPY ./ProgrammOne.service /etc/systemd/system
COPY ./ProgrammTwo.service /etc/systemd/system
COPY ./ExecProgrammOne /mnt
COPY ./ExecProgrammTwo /mnt
COPY ./FileProgrammOne /mnt

RUN apt-get update && apt-get install rsyslog -y