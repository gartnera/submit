#!/bin/bash -l

export HOME=/home/submit

firstUser=$(ls | head -n 1)

echo -n 'echo -n $$ > LEFT_PID; doNothing.sh' > LEFT_CMD
echo -n 'echo -n $$ > TOP_PID;'" grade-gui.py $firstUser" > TOP_CMD
echo -n 'echo -n $$ > BOTTOM_PID;'" controller.sh \"$1\"" > BOTTOM_CMD

tmuxinator start grade-view

rm LEFT_CMD
rm LEFT_PID
rm TOP_CMD
rm TOP_PID
rm BOTTOM_CMD
rm BOTTOM_PID
