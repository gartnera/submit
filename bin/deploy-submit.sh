#!/bin/bash

### build grading components ###
cd ~/bin

#binary to block forever. need dedicated binary so we can kill it to continue (without killing parent shell
gcc blockForever.c -o blockForever
#we need a binary to elevate priviledges all the way to submit.
gcc elevate.c -DCMD='"/home/submit/bin/grade-master.sh"' -o  grade-master-wrapper

### build components to deploy ###
cd ~/deploy

#build binary wrapper
#gcc lib/sds.c submit.c -o submit

#build new binary wrapper
gcc argv-rebuilder.c -o submit

#copy to bin
cp submit /usr/bin/submit

#no need to keep binary around
rm submit

#give suid
chmod +s /usr/bin/submit

#deploy the python script
python -m py_compile submit.py
cp submit.py /usr/bin/submit.py
#prevent others from reading submit.py
chmod 770 /usr/bin/submit.py

#make tmp dir
mkdir -p /tmp/submit
chmod 772 /tmp/submit

cd ~
#make the content directory. this is where all class data and user submission go
mkdir content
