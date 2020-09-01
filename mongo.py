import pymongo
from pymongo import MongoClient
from collections import OrderedDict

cluster = MongoClient(
    "mongodb+srv://Mitra:mitrapassword@manage.wwmlv.mongodb.net/Courses?retryWrites=true&w=majority")
db = cluster["Manage"]
collection = db["Users"]

taskBody = {
    "bsonType": "object",
                "required": ["desc", "dueDate", ],
                "properties": {
                    "desc": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "dueDate": {
                        "bsonType": "string",
                        "description": "must be a string and is not required"
                    },
                    "status": {
                        "bsonType": "bool",
                        "description": "must be a boolean and is required"
                    }
                }
}
taskSchema = {"$jsonSchema": taskBody}

courseBody = {
    "bsonType": "object",
    "required": ["courseCode", "tasks"],
    "properties": {
        "courseCode": {
            "bsonType": "string",
            "description": "must be a string and is required"
        },
        "tasks": {
            "bsonType": "array",
            "items": taskBody,
        }
    }
}
courseSchema = {"$jsonSchema": courseBody}

userSchema = {"$jsonSchema":
              {
                  "bsonType": "object",
                  "required": ["name", "courses"],
                  "properties": {
                      "name": {
                          "bsonType": "string",
                          "description": "must be string and is required"
                      },
                      "courses": {
                          "bsonType": "array",
                          "items": courseBody,
                      }
                  }
              }
              }


def addMongo(user, course, description, dueDate):
    courseObject = collection.find_one({"name": user,
                                        "courses.courseCode": course})
    print(courseObject)
    userExists = collection.count_documents({"name": user}) == 1
    # new user
    if(not userExists):
        cmd = OrderedDict([('collMod', 'Users'),
                           ('validator', userSchema),
                           ('validationLevel', 'moderate')])
        db.command(cmd)
        collection.insert_one({"name": user,
                               "courses": [{"courseCode": course, "tasks": [{"desc": description, "dueDate": dueDate, "status": False}]}]})
        print('added1')
    # existing user new course
    elif(userExists and courseObject == None):
        # validate course
        cmd = OrderedDict([('collMod', 'Courses'),
                           ('validator', courseSchema),
                           ('validationLevel', 'moderate')])
        db.command(cmd)
        # append course to courses array
        collection.update_one({"name": user},
                              {"$push": {"courses": {"courseCode": course,
                                                     "tasks": [{"desc": description, "dueDate": dueDate, "status": False}]}}})
        print("added2")
    # existing user existing course
    elif(userExists and courseObject != None):
        # validate task
        cmd = OrderedDict([('collMod', 'Courses'),
                           ('validator', taskSchema),
                           ('validationLevel', 'moderate')])
        db.command(cmd)
        # append task to tasks array
        collection.update_one({"name": user,"courses.courseCode":course},
                              {"$push": {"courses.$[course].tasks": {"desc": description, "dueDate": dueDate, "status": False } } },
                              upsert=False,
                              array_filters=[{"course.courseCode": course}])
        print("added3")

def removeMongo(user,course,description):
    collection.update_one(
        {"name":user,"courses.courseCode":course,"courses.tasks.desc":description},
        {"$pull": { "courses.$[course].tasks": {"desc":description} }},
        upsert=False,
        array_filters=[{"course.courseCode": course}])
    print("removed")

def editMongo(user,course,description,newDueDate):
    collection.update_one(
        {"name":user,"courses.courseCode":course,"courses.tasks.desc":description},
        {"$set": { "courses.$[course].tasks.$[task].dueDate":newDueDate} },
        upsert=False,
        array_filters=[{"course.courseCode": course},{"task.desc":description}])
    print("edited")

def getDataFromMongo(user):
    if user != "":
        return collection.find({"name": user})


def printMongo(course):
    # results is an array
    output = ""
    if course == "ALL":
        courses = collection.find({})
        for courseElement in courses:
            output = output+courseElement["courseCode"]+": "
            for task in courseElement["tasks"]:
                output = output+task["desc"]+" "
    elif course != "":
        targetCourse = collection.find({"courseCode": course})
        output = course+": "
        # there should only be one course with the name course
        # but mongodb makes me do it this way
        for courseElement in targetCourse:
            for task in courseElement["tasks"]:
                output = output+" "+task["desc"]

    # gives back json object

    return output
