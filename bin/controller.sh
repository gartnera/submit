#!/bin/bash
#block ctrl-z
set +m
#block ctrl-c
trap '' 2

function printHeader()
{
	clear
	starBox.py L 50 3 "Assignment: $1" "User: $2" "Submission $(($3 + 1)) of $4"
}

function buildNonBlockingCommand()
{
	res="clear;$1;blockForever"
}

function updateLeftCommand()
{
	termPid=$(cat "${assignRoot}LEFT_PID")
	echo -n $1 > "${assignRoot}LEFT_CMD"
	pkill -TERM -P $termPid
}

function updateTopCommand()
{
	termPid=$(cat "${assignRoot}TOP_PID")
	echo -n $1 > "${assignRoot}TOP_CMD"
	pkill -TERM -P $termPid
}

function dualCd()
{
	cd "$1"
	updateLeftCommand "cd $1;clear;ls -Rlth;blockForever"
}
function promptYesOrNo()
{
	while true; do
		read -n 1 -p "$1" yn
		case $yn in
			[Yy]*|"" ) return 1; break;;
			[Nn]* ) return 0; exit;;
			* ) echo "Please answer yes or no.";;
		esac
	done
}
function fileNamePrompt()
{
	promptYesOrNo "Do you wish to use $fileName? [Yn] "
	#0 if no, read filename again
	if [[ $? -eq 0 ]]; then
		while true; do
			read -e -p "Enter the file to open (tab to complete): " fileName
			#remove / ~ $ ..
			fileName=$(echo -n $fileName | tr -d '/' | tr -d '~' | tr -d '$')
			fileName=${fileName//..}

			if [[ ! -f $fileName ]]; then
				echo "$fileName is not valid"
			else
				break
			fi
		done
	fi
}

dirs=(*/)
assignRoot="$(pwd)/"

users=()
for dir in ${dirs[@]}; do
	users+=($(echo -n $dir | tr -d '/'))
done

i=0
numberOfUsers=${#users[@]}
userName=${users[$i]}
dualCd "${dirs[$i]}"

fileName=$(ls -t | head -n 1)

editor="vim -Z"

while true; do
	printHeader "$1" $userName $i $numberOfUsers
	echo "Enter the action you would like to take"
	echo "0) List All Files"
	echo "1) Open file"
	echo "2) Compile and run file"
	echo "3) Format current file and reopen"
	echo "4) Extract zip file"
	echo "5) [TODO] View bash history"
	echo "6) [TODO] View auth log"
	echo "7) [TODO] View process usage data"
	echo "8) [TODO] Extract and view user snapshot"
	echo "9) Exit"
	echo "n) Go to next user"
	echo "p) Go to previous user"
	echo -n "> "
	read -n 1 choice

	if [[ "$choice" == "0" ]]; then
		printHeader "$1" $userName $i $numberOfUsers
		cmd="ls -Rlth"
		buildNonBlockingCommand "$cmd"
		updateLeftCommand "$res"
	elif [[ "$choice" == "1" ]]; then
		printHeader "$1" $userName $i $numberOfUsers
		fileNamePrompt
		updateLeftCommand "$editor $fileName"
	elif [[ "$choice" == "2" ]]; then
		printHeader "$1" $userName $i $numberOfUsers
		fileNamePrompt

		#TODO: replace with real values
		compiler="gcc -lm"
		binName="./a.out"
		$compiler $fileName

		#TODO: drop privs
		eval "$binName"
	elif [[ "$choice" == "3" ]]; then
		updateLeftCommand "format -i $fileName; $editor $fileName"

	elif [[ "$choice" == "4" ]]; then
		printHeader "$1" $userName $i $numberOfUsers
		fileNamePrompt
		cmd="unzip $fileName"
		buildNonBlockingommand "$cmd"
		updateLeftCommand "$res"

	elif [[ "$choice" == "9" ]]; then
		updateTopCommand "exit"
		#TODO: don't kill server, kill session
		tmux kill-server

	elif [[ "$choice" == "p" ]]; then
		((--i));
		if [[ $i -lt 0 ]]; then
			echo -e "\nCan't go back any further!"
			read -p "Press enter to continue"
			((++i));
		else
			userName=${users[$i]}
			dualCd "../${dirs[$i]}"
			fileName=$(ls | head -n 1)
			updateTopCommand "grade-gui.py $userName"
		fi
	elif [[ "$choice" == "n" ]]; then
		((++i));
		if [[ $i -ge $numberOfUsers ]]; then
			echo -e "\nYou've reached the end"
			read -p "Press enter to continue"
			((--i));
		else
			userName=${users[$i]}
			dualCd "../${dirs[$i]}"
			fileName=$(ls | head -n 1)
			updateTopCommand "grade-gui.py $userName"
		fi
	fi
done
