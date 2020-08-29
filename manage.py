import json
from beautifultable import BeautifulTable
from termcolor import colored
import colorama
import datetime

# MONGO DB INFO:
# USERNAME: Mitra
# PASSWORD: MZZeVXCwY9SBf9F


class Manage:
    functionMapping = {
        "add": "addTask",
        "help": "commandList",
        "change": "changeStatus",
        "show": "displayCourse",
        "showall": "displayAll",
        "new": "newCourse",
        "list": "listCourses",
        "remove": "removeCourse",
        "display": "displayTasksForDay",
        "displayToday": "displayTasksDueToday"
    }

    def writeToFile(data: dict):
        with open('tasks.json', 'w') as json_file:
            json.dump(data, json_file)

    def readFile():
        with open("tasks.json") as f:
            data = json.load(f)
        return data

    def findTask(course: str, description: str, data: dict):
        for task in data[course]:
            if task["description"] == description:
                return data[course].index(task)

    def getDueDate():
        isValidDate = False
        while(not isValidDate):
            isValidDate = True
            dueDate = input("Due Date (DD/MM/YY): ")
            dueTime = input("Due Time (HH:MM): ")
            dueDate = dueDate + " " + dueTime
            try:
                datetime.datetime.strptime(dueDate, "%d/%m/%y %H:%M")
            except ValueError:
                print("Please enter a valid date and time.")
                isValidDate = False
        return dueDate

    def addTask(self):
        course = Manage.getCourse()
        description = input("Task Description: ")
        dueDate = Manage.getDueDate()
        status = input("Status: ")
        data = Manage.readFile()

        data[course].append({"description": description,
                             "dueDate": dueDate, "status": status})

        Manage.writeToFile(data)

    def getCourse():
        data = Manage.readFile()
        isValidCourse = False
        while not isValidCourse:
            isValidCourse = True
            course = input("Course: ")
            if course in data.keys():
                return course
            else:
                addCourse = Manage.checkValidCourse(course)
            if addCourse:
                Manage.addNewCourse(course)
                return course
            else:
                print("Please enter a valid course.")
                isValidCourse = False

    def removeCourse(self):
        data = Manage.readFile()
        course = input("Course: ")
        if course not in data.keys():
            print("Course {} does not exist".format(course))
            return

        data.pop(course)
        Manage.writeToFile(data)

    def displayTasksForDay(self):
        data = Manage.readFile()
        table = Manage.createTable()
        for course in data.keys():
            for task in data[course]:
                if datetime.datetime.now() < datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M"):
                    table = Manage.addToTable(table, task, course)
        print(table)
        print('\n')
        return table
    
    def displayTasksDueToday(self):
        data = Manage.readFile()
        table = Manage.createTable()
        for course in data.keys():
            for task in data[course]:
                if datetime.datetime.now().date() == datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M").date():
                    table = Manage.addToTable(table, task, course)
        print(table)
        print('\n')
        return table
                

    def checkValidCourse(course):
        print("The course {} does not exist.".format(course))
        answered = False
        while not answered:
            answer = input(
                "Would you like to add {} as a new course? (Y/N):".format(course))
            if(answer == 'Y' or answer == 'y'):
                Manage.addNewCourse(course)
                return True
            elif(answer == 'N' or answer == 'n'):
                return False

    def addNewCourse(course):
        data = Manage.readFile()

        newCourseDict = {
            course: []
        }

        data.update(newCourseDict)
        Manage.writeToFile(data)

    def newCourse(self):
        course = input("Course: ")
        data = Manage.readFile()
        if course in data.keys():
            print("The course {} already exists.".format(course))
        else:
            Manage.addNewCourse(course)

    def changeStatus(self):
        course = input("Course: ")
        description = input("Description: ")
        status = input("Status: ")
        data = Manage.readFile()
        taskIndex = Manage.findTask(course, description, data)

        data[course][taskIndex]["status"] = status

        Manage.writeToFile(data)

    def createTable():
        table = BeautifulTable()
        table.columns.header = ["Course", "Description",
                                "Due Date", "Due Time", "Status"]

        return table

    def listCourses(self):
        data = Manage.readFile()
        table = BeautifulTable()
        for course in data.keys():
            table.rows.append([course])
        print(table)

    def addToTable(table, task, course):
        date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
        table.rows.append([course, task['description'], date.strftime("%d/%m/%y"), date.strftime("%H:%M"), task["status"]])
        # if(task['status'] == 'COMPLETE'):
        #     table.rows.append([colored(course, 'green'), colored(task["description"], 'green'),
        #                        colored(date.strftime("%d/%m/%y"), 'green'), colored(date.strftime("%H:%M"), 'green'), colored(task["status"], 'green')])
        # elif(task['status'] == "INCOMPLETE"):
        #     table.rows.append([colored(course, 'red'), colored(task["description"], 'red'),
        #                        colored(date.strftime("%d/%m/%y"), 'red'), colored(date.strftime("%H:%M"), 'red'), colored(task["status"], 'red')])

        return table

    def displayCourse(self):
        course = input("Course: ")
        data = Manage.readFile()
        if course not in data.keys():
            print("COURSE NOT FOUND!")
            return

        table = Manage.createTable()
        for task in data[course]:
            table = Manage.addToTable(table, task, course)
        print(table)
        print('\n')

    def displayAll(self):
        data = Manage.readFile()
        table = Manage.createTable()

        for course in data.keys():
            for task in data[course]:
                table = Manage.addToTable(table, task, course)

        print(table)
        print('\n')

    def commandList(self):
        print('='*40)
        print("add: add a task")
        print("change: change the status of a task")
        print("show: displays the table for a course")
        print("showall: displays the table for all the courses")
        print("new: add a new course to the course list")
        print("list: lists all courses")
        print("exit: terminates the program")
        print("remove: deletes the specified course")
        print("display: displays all the tasks due in the future")
        print("displayToday: displays all the tasks due today")
        print('='*40)

    def modifyExistingTask(course):
        data = Manage.readFile()
        print("MODIFY")

    def exit():
        return


def check():
    command = input(">")
    manageClass = Manage()

    if command == "exit":
        return True

    if command not in Manage.functionMapping.keys():
        print("Please enter a valid command.")
        return False

    try:
        getattr(manageClass, Manage.functionMapping[command])()
    except AttributeError:
        raise NotImplementedError("Command does not exist")

    return False


def start():
    colorama.init()
    closeProgram = False
    m = Manage()
    table = BeautifulTable()
    print("="*21)
    print("||" + colored("Welcome to Manage", 'red', 'on_yellow') + "||")
    print("="*21)
    while not closeProgram:
        print('-'*40)
        print("Type {} to view all commands".format(
            colored("'help'", 'yellow')))
        closeProgram = check()
