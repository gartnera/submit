#!/usr/bin/python
import sys

def printNStars(n):
    for i in range(n):
        sys.stdout.write("*")

if len(sys.argv) < 5:
    print "Usage: {} [C|L] <outer min width> <line stars> ...".format(sys.argv[0])
    print "\t [C|L]: specify either C (center) or L (left align)"
    print "\t <outer min width>: specify the minimum outer width of the box (0 to autoflow)"
    print "\t <line stars>: specify the number of stars that should appear on each side of the line"
    print "\t ...: replace with text to put in box. Surround each line with quotes."
    exit(-1)

if sys.argv[1] == "C" or sys.argv[1] == "c":
    center = True
else:
    center = False

borderMin = int(sys.argv[2])
lineStars = int(sys.argv[3])

args= sys.argv[4:]

maxLen = 0

for arg in args:
    l = len(arg)
    if l > maxLen:
        maxLen = l

starWidth = lineStars * 2 + 2

borderLen = maxLen + starWidth
if borderMin > borderLen:
    borderLen = borderMin
    maxLen = borderLen - starWidth


printNStars(borderLen)
sys.stdout.write("\n")

for arg in args:
    printNStars(lineStars)
    sys.stdout.write(" ")
    l = len(arg)
    if l < maxLen:
        if center:
            diff = maxLen -l
            side = diff/2
            for i in range(side):
                sys.stdout.write(" ")

            sys.stdout.write(arg)

            if diff % 2 != 0:
                side += 1
            for i in range(side):
                sys.stdout.write(" ")
        else:
            diff = maxLen -l
            sys.stdout.write(arg)
            for i in range(diff):
                sys.stdout.write(" ")


    else:
        sys.stdout.write(arg)
    sys.stdout.write(" ")
    printNStars(lineStars)
    sys.stdout.write("\n")


printNStars(borderLen)
sys.stdout.write("\n")
