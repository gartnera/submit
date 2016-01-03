import os
import uuid
import shutil
import sys
import jsonpickle
import datetime
import pwd
import json
import dateutil.parser
import subprocess
import magic

TMP_DIR = "/tmp/submit/"

######## Class to manage suid status #######
class SuidManager:
    def __init__(self):
        self.euid = os.geteuid()
        self.uid = os.getuid()

    def dropPerms(self):
        os.seteuid(os.getuid())

    def resumePerms(self):
        os.setuid(self.euid)

####### Begin Function Declarations #######
def printUsage(progName):
    print "Usage:\t{} <filename>".format(progName)
    print "\t-l List upcoming assignments"
    print "\t-m Admin your classes (teacher only)"

def copyFileToTmp(origName):
    newName = TMP_DIR + str(uuid.uuid4())
    shutil.copyfile(origName, newName)
    return newName

def cdAndCopyToTmp(userPath, fileName):
    #if user has provided file, do work to copy it to tmp

    m = SuidManager()
    #save class path (/home/submit/content/.../)
    classPath = os.getcwd()
    #drop to orignal user
    m.dropPerms()
    #return to user path (to grab file)
    os.chdir(userPath)
    res = magic.from_file(fileName)

    if "ASCII text" not in res and "Zip archive data" not in res:
        print "You may only submit a text file (source code) or a zip file"
        print "Please check your submission"
        exit(-1)

    #copy file, returns new path
    tmpFilePath = copyFileToTmp(fileName)
    #return to our old uid (should be submit)
    m.resumePerms()

    #return to submit home dir
    os.chdir(classPath)

    return tmpFilePath

def loadClasses():
    try:
        with open ("classes.json", "r") as classFile:
            classString=classFile.read()
    except:
        classString = ""

    if classString == "":
        print "Unable to load classes"
        exit(-1)
    else:
        classes = json.loads(classString)

    adminClasses = []
    studentClasses = []
    for c in classes:
        #get real group id of user
        gid = os.getgid()
        #if gid matches, add to studentClasses
        if c["StudentGid"] == gid:
            studentClasses.append(c)

        #get real uid
        uid = os.getuid()
        #if uid matches, add to adminClasses
        if c["AdminUid"] == uid:
            adminClasses.append(c)
    return (adminClasses, studentClasses)

def promptForStudentClass(studentClasses):
    #if no classes, notify and exit
    if len(studentClasses) == 0:
        print "Sorry, you aren't enrolled in any classes"
        exit(-2)
    #if only one class, default to it
    if len(studentClasses) == 1:
        c = studentClasses[0]
    #else print and prompt
    else:
        for i, c in enumerate(studentClasses):
            print "{}: {}".format(i, c["ClassName"])
        print "Enter the number of the class you want to submit to:"
        sys.stdout.write("> ")
        choice = sys.stdin.readline().rstrip('\n')
        c = studentClasses[int(choice)]

    return c

def promptForManageClass(adminClasses):
    #if no classes, notify and exit
    if len(adminClasses) == 0:
        print "Sorry, you aren't registered as admin"
        exit(-2)
    #if only one class, default to it
    if len(adminClasses) == 1:
        c = adminClasses[0]
    #else print and prompt
    else:
        for i, c in enumerate(adminClasses):
            print "{}: {}".format(i, c["ClassName"])
        print "Enter the number of the class you want to manage:"
        sys.stdout.write("> ")
        choice = sys.stdin.readline().rstrip('\n')
        c = adminClasses[int(choice)]

    return c

def printAllAssignments(assigns):
    for i, assign in enumerate(assigns):
        print "{})\tName: {}".format(i, assign['displayName'])
        print "\tEnd Date: {}".format(assign['endDate'].strftime("%A (%D) at %I:%M %p"))

def printSubmittableAssignments(assigns):
    assignmentPrinted = False
    j = 0
    submittableAssignOffset = None
    for i, assign in enumerate(assigns):
        if assign['endDate'] > datetime.datetime.now():
            if submittableAssignOffset == None:
                submittableAssignOffset = i
            print "{})\tName: {}".format(j, assign['displayName'])
            print "\tEnd Date: {}".format(assign['endDate'].strftime("%A (%D) at %I:%M %p"))
            assignmentPrinted = True
            j = j + 1
    if assignmentPrinted == False:
        print "No Assignments"
    return submittableAssignOffset

def printUpcomingAssignments(assigns):
    assignmentPrinted = False
    i = 0
    for assign in assigns:
        if assign['endDate'] > datetime.datetime.now():
            if i > 2:
                break
            print "{} ends on {}".format(assign['displayName'], assign['endDate'].strftime("%A (%D) at %I:%M %p"))
            assignmentPrinted = True
            i = i + 1
    if assignmentPrinted == False:
        print "No Upcoming Assignments"

def loadAndPrintAllClasses(classes):
    for i, c in enumerate(classes):
        os.chdir(c["DirName"])
        try:
            with open ("assignments.json", "r") as assignFile:
                assignString=assignFile.read()
        except:
            assignString=""

        if assignString == "":
            assigns = []
        else:
            assigns = jsonpickle.decode(assignString)
        os.chdir("..")
        print "Upcoming Assignments for {}".format(c["ClassName"])
        printUpcomingAssignments(assigns)
        if i < len(classes) - 1:
            print ""

def moveOld(userFileName):
    oldName = userFileName + ".old"
    if os.path.exists(userFileName):
        #recurse if old already exists
        moveOld(oldName)
        shutil.move(userFileName, oldName)

def submitAssignment(assigns, index, submittableAssignOffset, tmpFilePath, userFilePath):
    try:
        assign = assigns[index + submittableAssignOffset]

        #no longer needed, users only given choice to submit current assignments
        #if assign['endDate'] < datetime.datetime.now():
        #    print("Sorry, but this assignment has closed")
        #    return

        assignFolder = assign["folderName"]

        try:
            os.mkdir(assignFolder)
        except:
            pass
        os.chdir(assignFolder)
        try:
            os.mkdir(username)
        except:
            pass
        os.chdir(username)
        userFileName = os.path.basename(userFilePath)
        if assignFolder != "late":
            #duplicate logic
            moveOld(userFileName)

            shutil.copyfile(tmpFilePath, userFileName)
        else:
            #Late assignment logic
            print "Do not submit assignments here unless you've recieved permission from the instructor."
            print "Type YES in uppercase to confirm you've recieved permission:"
            answer = sys.stdin.readline().rstrip('\n')
            if answer != "YES":
                return
            print "Enter the name of the assignment you wish to submit:"
            name = sys.stdin.readline().rstrip('\n')
            name = name + ".c"
            #duplicate logic
            moveOld(name)
            shutil.copyfile(tmpFilePath, name)

        os.remove(tmpFilePath)
        print ("Thanks for the submission!")
        exit()
    except IndexError:
        print "Invalid Selection"
        return

######## Admin Functions ########


def deleteAssignments(assigns):
    printAllAssignments(assigns)
    print "Enter the number of the assignment you wish to delete: "
    sys.stdout.write("> ")

    try:
        choice = sys.stdin.readline().rstrip('\n')
    except KeyboardInterrupt:
        return
    assigns.pop(int(choice))

def editAssignments(assigns):
    if len(assigns) == 0:
        print "Please create an assignment first"
        return
    printAllAssignments(assigns)
    print "Enter the number of the assignment you wish to edit: "
    sys.stdout.write("> ")

    try:
        choice = int(sys.stdin.readline().rstrip('\n'))
    except KeyboardInterrupt:
        return
    assign = assigns[choice]

    print "Enter the display name [{}]:".format(assign["displayName"])
    name = sys.stdin.readline().rstrip('\n')
    if name:
        assign["displayName"] = name


    endDate = assign["endDate"]
    print "Enter the end date (MM/DD/YY) [{}]:".format(assign['endDate'].strftime("%D"))
    endDateStr = sys.stdin.readline().rstrip('\n')
    if endDateStr:
        nEndDate = dateutil.parser.parse(endDateStr)
        endDate = nEndDate.replace(hour=endDate.hour, minute=endDate.minute, second=59)

    print "Enter the end time (hh:mm AM/PM) [{}]:".format(assign['endDate'].strftime("%I:%M %p"))
    endTime = sys.stdin.readline().rstrip('\n')
    if endTime:
        endTime = dateutil.parser.parse(endTime)
        endDate = endDate.replace(hour=endTime.hour, minute=endTime.minute, second=59)

    assign["endDate"] = endDate


    assigns[choice] = assign
    assigns.sort(key=lambda a: a["endDate"])

def addAssignments(assigns):
    try:
        newAssign = {}
        print "Enter the name:"
        newAssign["displayName"] = sys.stdin.readline().rstrip('\n')

        print "Enter the folder name:"
        newAssign["folderName"] = sys.stdin.readline().rstrip('\n')

        os.mkdir(newAssign["folderName"])

        print "Enter the end date (MM-DD-YY hh:mm AM/PM):"
        endDate = sys.stdin.readline().rstrip('\n')
        endDate = dateutil.parser.parse(endDate)
        endDate = endDate.replace(second=59)

        newAssign["endDate"] = endDate

        assigns.append(newAssign)
        assigns.sort(key=lambda a: a["endDate"])

    except KeyboardInterrupt:
        return

def saveAssignments(assigns):
    assignString = jsonpickle.encode(assigns)
    with open ("assignments.json", "w") as assignFile:
        assignFile.truncate()
        assignFile.write(assignString)

    sys.exit()

def tarballAssignments(assigns):
    printAllAssignments(assigns)
    print "Enter the number of the assignment you wish to tarball/export to your home directory:"
    sys.stdout.write("> ")

    try:
        choice = int(sys.stdin.readline().rstrip('\n'))
    except KeyboardInterrupt:
        return
    assign = assigns[choice]
    print "Enter the name of the tarball (without .tar.gz):"
    sys.stdout.write("> ")

    try:
         outputName = "~/" + sys.stdin.readline().rstrip('\n') + ".tar.gz"
         outputName = os.path.expanduser(outputName)
    except KeyboardInterrupt:
        return

    tmpName = "/tmp/" + str(uuid.uuid4()) + ".tar.gz"
    command = "tar cfz {} {}".format(tmpName, assign["folderName"])
    os.system(command)

    m = SuidManager()
    m.dropPerms()
    shutil.copyfile(tmpName, outputName)
    m.resumePerms()

    os.remove(tmpName)
    print "{} tarball exported to {}".format(assign["displayName"], outputName)

def gradeAssignments(assigns):
    printAllAssignments(assigns)
    print "Enter the number of the assignment you wish to grade:"
    sys.stdout.write("> ")

    try:
        choice = int(sys.stdin.readline().rstrip('\n'))
    except KeyboardInterrupt:
        return
    assign = assigns[choice]

    os.chdir(assign["folderName"])

    if len(os.listdir(".")) < 2:
        print "Sorry, you can't grade this assignment. It has no submissions or is missing grading information."
        os.chdir("..")
        return

    #transfer control to master.sh (opens grading views)
    cmd = ["/home/submit/bin/grade-master-wrapper", assign["displayName"]]
    subprocess.call(cmd)

    print "Enter the name of json to export (without .json) (enter to skip):"
    sys.stdout.write("> ")

    try:
        outputName = sys.stdin.readline().rstrip('\n')
    except KeyboardInterrupt:
        return

    if outputName:
        outputPath = "~/" + outputName + ".json"
        outputPath = os.path.expanduser(outputPath)
        tmpName = "/tmp/" + str(uuid.uuid4()) + ".json"
        shutil.copyfile("grades.json", tmpName)

        m = SuidManager()
        m.dropPerms()
        moveOld(outputPath)
        shutil.copyfile(tmpName, outputPath)
        m.resumePerms()

        os.remove(tmpName)
        print "{} grades exported to {}".format(assign["displayName"], outputPath)

    os.chdir("..")

def editRubricAssignments(assigns):
    printAllAssignments(assigns)
    print "Enter the number of the assignment you wish to create or edit a rubric for:"
    sys.stdout.write("> ")

    choice = int(sys.stdin.readline().rstrip('\n'))
    assign = assigns[choice]

    editRubric(assign)

def editRubric(assign):
    os.chdir(assign["folderName"])

    #if exists, load
    if os.path.exists("grades.json"):
        with open("grades.json") as f:
            j = json.load(f)
            t = j["Template"]

    #if not, create
    else:
        #full json object
        j = {}

        #template object
        t = {}
        t["TotalPoints"] = 0
        t["CorrectPoints"] = 0
        t["Comments"] = ""
        t["Rubric"] = []

    #TODO: warn if grading already started
    t["Rubric"] = editRubricTemplate(t["Rubric"])

    j["Template"] = t

    with open("grades.json", "w") as f:
        json.dump(j, f)

    os.chdir("..")


def printRubricItems(r, number):
    total = 0
    count = 0
    for idx, i in enumerate(r):
        points = i["PossiblePoints"]
        if number:
            sys.stdout.write("{}) ".format(idx))
        print "{} [{}]".format(i["Text"], points)

def editRubricItem(item):
    #init item if it dosen't exist
    if item == None:
        item = {}
        item["Text"] = ""
        item["PossiblePoints"] = 1
        item["Correct"] = False

    print "Enter the text of the rubric option [{}]:".format(item["Text"])
    text = sys.stdin.readline().rstrip('\n')
    if text:
        item["Text"] = text

    print "Enter the number of points for the rubric option [{}]:".format(item["PossiblePoints"])
    points = sys.stdin.readline().rstrip('\n')
    if points:
        item["PossiblePoints"] = int(points)

    return item

def editRubricMenuPrompt():
    print "1) Add rubric item"
    print "2) Edit rubric item"
    print "3) Delete rubric item"
    print "4) List rubric items"
    print "5) Finish editing"
    sys.stdout.write("> ")
    choice = sys.stdin.readline().rstrip('\n')
    return int(choice)

def editRubricTemplate(r):
    while True:
        choice = editRubricMenuPrompt()
        if choice == 1:
            item = editRubricItem(None)
            r.append(item)

        elif choice == 2:
            printRubricItems(r, True)
            print "Enter the item you would like to edit"
            sys.stdout.write("> ")
            choice = int(sys.stdin.readline().rstrip('\n'))

            item = editRubricItem(r[choice])
            r[choice] = item

        elif choice == 3:
            printRubricItems(r, True)
            print "Enter the item you would like to delete"
            sys.stdout.write("> ")
            choice = int(sys.stdin.readline().rstrip('\n'))

            del r[choice]

        elif choice == 4:
            printRubricItems(r, False)
        elif choice == 5:
            return r

def adminMenuPrompt():
    print "1) Add assignments"
    print "2) Delete assignments"
    print "3) Print assignments"
    print "4) Edit assignments"
    print "5) Tarball assignments"
    print "6) Add or edit assignment rubric"
    print "7) Grade assignment (Experimental)"

def adminLoop(assigns):
    while True:
        adminMenuPrompt()
        sys.stdout.write("> ")
        try:
            choice = sys.stdin.readline().rstrip('\n')
        except KeyboardInterrupt:
            saveAssignments(assigns)

        if choice == "exit" or choice == "quit":
            saveAssignments(assigns)
            exit()

        choice = int(choice)
        if choice == 1:
            addAssignments(assigns)
        elif choice == 2:
            deleteAssignments(assigns)
        elif choice == 3:
            printAllAssignments(assigns)
        elif choice == 4:
            editAssignments(assigns)
        elif choice == 5:
            tarballAssignments(assigns)
        elif choice == 6:
            editRubricAssignments(assigns)
        elif choice == 7:
            gradeAssignments(assigns)

#############################
####### Begin Program #######
#############################

#sys.argv[1] will be original program name (before c suid wrapper)
#sys.argv[2+] will be the actual arguments
#if only 2 arguments, print help

if len(sys.argv) < 3:
    printUsage(sys.argv[1])
    sys.exit(-1)

#if valid submit call, load class json
#save path user is currently in
userPath = os.getcwd()
#go to submit home
os.chdir("/home/submit/")

#load classes info
(adminClasses, studentClasses) = loadClasses()

#switch to content dir, this contains all class directoreis
os.chdir("content")

isManageing = False

if sys.argv[2] == "-l":
    if len(studentClasses) == 0:
        print "Sorry, you aren't enrolled in any classes"
        exit()
    loadAndPrintAllClasses(studentClasses)
    exit()
#prompt for class to admin
elif sys.argv[2] == "-m":
    #exits if no classes
    c = promptForManageClass(adminClasses)
    isManageing = True
else:
    #exits if no classes
    c = promptForStudentClass(studentClasses)

os.chdir(c["DirName"])

try:
    with open ("assignments.json", "r") as assignFile:
        assignString=assignFile.read()
except:
    assignString=""

if assignString == "":
    assigns = []
else:
    assigns = jsonpickle.decode(assignString)

if isManageing:
    #admin loop, exits after completion
    adminLoop(assigns)

if len(assigns) == 0:
    print "Sorry, there are no submittable assignments"

#command will exit if not source code or zip
tmpFilePath = cdAndCopyToTmp(userPath, sys.argv[2])

uid=os.getuid()
username=pwd.getpwuid(uid)[0]

print ("Welcome " + username)

while True:
    try:
        submittableAssignOffset = printSubmittableAssignments(assigns)
        print "Select from the above list the assignment you wish to submit"
        sys.stdout.write("> ")
        choice = sys.stdin.readline().rstrip('\n')
        if choice == "exit" or choice == "quit":
            os.remove(tmpFilePath)
            exit()
        choice = int(choice)
        submitAssignment(assigns, choice, submittableAssignOffset, tmpFilePath, sys.argv[2])
    except KeyboardInterrupt:
        exit()
