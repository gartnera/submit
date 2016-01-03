#!/bin/bash
apt-get install pip tmux gcc python-dev ruby

gem install tmuxinator

pip install jsonpickle npyscreen python-dateutil python-Levenshtein python-magic

touch /usr/bin/submit
touch /usr/bin/submit.py

chown submit:submit /usr/bin/submit /usr/bin/submit.py
