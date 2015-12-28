#!/bin/bash
apt-get install pip tmux gcc python-dev

pip install jsonpickle npyscreen python-dateutil python-Levenshtein filemagic

touch /usr/bin/submit
touch /usr/bin/submit.py

chown submit:submit /usr/bin/submit /usr/bin/submit.py
