#!/usr/bin/python
import npyscreen
import signal
import json
import os
import sys
import time

def sig_handler(signal, frame):
    rubricVals, comments = GA.getData()

    userData["Comments"] = comments

    r = userData["Rubric"]

    points = 0

    for i in range(len(r)):
        if i in rubricVals:
            r[i]["Correct"] = True
            points += r[i]["PossiblePoints"]
        else:
            r[i]["Correct"] = False

    userData["Rubric"] = r

    userData["CorrectPoints"] = points

    j[user] = userData

    with open("grades.json", "w") as f:
        json.dump(j, f)
    exit(0)

class GradeApp(npyscreen.NPSApp):
    def setData(self, userData):
        self.comments = userData["Comments"]
        rubricData = []
        rubricSelected = []
        for idx, item in enumerate(userData["Rubric"]):
            rubricData.append("{} [{}]".format(item["Text"], item["PossiblePoints"]))
            if item["Correct"]:
                rubricSelected.append(idx)
        self.rubricData = rubricData
        self.rubricSelected = rubricSelected

    def getData(self):
        return (self.rubric.value, self.comments.value)

    def main(self):
        F = npyscreen.FormBaseNew( minimum_columns = 70)

        F.add(npyscreen.TitleFixedText, name = "Comments")
        self.comments = F.add(npyscreen.MultiLineEdit, value=self.comments, max_height=5)
        F.add(npyscreen.TitleFixedText, name = "Rubric")
        self.rubric = F.add(npyscreen.MultiSelect,values = self.rubricData, value=self.rubricSelected, scroll_exit=True)
        F.edit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    with open("grades.json") as f:
        j = json.load(f)

    user = sys.argv[1]

    if user not in j:
        j[user] = j["Template"]

    userData = j[user]

    GA = GradeApp()
    GA.setData(userData)
    GA.run()
