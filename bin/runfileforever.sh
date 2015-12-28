#!/bin/bash
set +m 
trap '' 2
stty susp undef

root=$(pwd)/
while true; do
	command=$(cat ${root}$1)
	eval "$command"
done
