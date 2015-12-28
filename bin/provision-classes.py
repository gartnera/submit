#!/usr/bin/python

import os
import sys
import json
import pwd
import grp
import uuid

def menu():
    print ("0) Save and exit")
    print ("1) Add class")
    print ("2) Delete class")
    print ("3) Edit class")
    print ("4) Print Classes")
    sys.stdout.write("> ")
    choice = sys.stdin.readline().rstrip('\n')
    return int(choice)

def printClasses(classes, count=False):
    for i, c in enumerate(classes):
        adminUsername = pwd.getpwuid(c["AdminUid"]).pw_name
        groupName = grp.getgrgid(c["StudentGid"]).gr_name

        if count:
            sys.stdout.write("{}) ".format(i))

        print c["ClassName"]
        print "\tDirectory: {}".format(c["DirName"])
        print "\tAdmin Username: {} [{}]".format(adminUsername, c["AdminUid"])
        print "\tStudent Group: {} [{}]".format(groupName, c["AdminUid"])

def addClasses(classes):
    c = editClass(None)
    classes.append(c)

def editClasses(classes):
    printClasses(classes, count=True)

    print "Enter the number of the class you want to edit"
    sys.stdout.write("> ")
    choice = int(sys.stdin.readline().rstrip('\n'))

    c = editClass(classes[choice])
    classes[choice] = c

def delClasses(classes):
    printClasses(classes, count=True)

    print "Enter the number of the class you want to delete"
    sys.stdout.write("> ")
    choice = int(sys.stdin.readline().rstrip('\n'))

    del classes[choice]

def editClass(c):
    if c == None:
        c = {}
        c["ClassName"] = ""
        c["DirName"] = str(uuid.uuid4())
        c["AdminUid"] = 0
        c["StudentGid"] = 0

    print "Enter the class name [{}]:".format(c["ClassName"])
    name = sys.stdin.readline().rstrip('\n')
    if name:
        c["ClassName"] = name

    print "Enter the directory name [{}]:".format(c["DirName"])
    name = sys.stdin.readline().rstrip('\n')
    if name:
        c["DirName"] = name

    print "Enter admin uid [{}]:".format(c["AdminUid"])
    uid = sys.stdin.readline().rstrip('\n')
    if uid:
        c["AdminUid"] = int(uid)

    print "Enter student gid [{}]:".format(c["StudentGid"])
    gid = sys.stdin.readline().rstrip('\n')
    if gid:
        c["StudentGid"] = int(gid)

    return c

#move to the home dir
os.chdir("..")

#if classes.json exists load
if os.path.exists("classes.json"):
    with open("classes.json") as f:
        classes = json.load(f)

#otherwise create
else:
    classes = []

while True:
    choice = menu()
    if choice == 0:
        break
    elif choice == 1:
        addClasses(classes)
    elif choice == 2:
        delClasses(classes)
    elif choice == 3:
        editClasses(classes)
    elif choice == 4:
        printClasses(classes)

#create any folders, as needed
for c in classes:
    path = "content/{}".format(c["DirName"])
    if not os.path.exists(path):
        os.makedirs(path)

#write out json
with open("classes.json", "w") as f:
    json.dump(classes, f)
