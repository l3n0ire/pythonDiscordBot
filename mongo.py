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
    courseObject = collection.find({"courseCode": course})
    print(collection.count_documents({"courseCode": course}))

    if(collection.count_documents({"name": user}) == 0):
        cmd = OrderedDict([('collMod', 'Users'),
        ('validator', userSchema),
        ('validationLevel', 'moderate')])
        db.command(cmd)
        collection.insert_one({"name": user,
        "courses": [{"courseCode": course, "tasks": [{"desc": description, "dueDate": dueDate, "status": False}]}]})
        print('added')
    elif(collection.count_documents({"courseCode": course}) == 0):
        cmd= OrderedDict([('collMod', 'Courses'),
            ('validator', courseSchema),
            ('validationLevel', 'moderate')])
        db.command(cmd)
        collection.insert_one({"courseCode": course,
        "tasks": [{"desc": description, "dueDate": dueDate, "status": False}]})
        print("added")
    elif(collection.count_documents({"courseCode": course}) == 1):
        cmd= OrderedDict([('collMod', 'Courses'),
            ('validator', taskSchema),
            ('validationLevel', 'moderate')])
        db.command(cmd)
        collection.update_one({"courseCode": course}, {"$push":
        {"tasks": {"desc": description, "dueDate": dueDate, "status": False}}})
        print("added")

def getDataFromMongo(user):
    if user != "":
        return collection.find({"name": user})

def printMongo(course):
    # results is an array
    output = ""
    if course == "ALL":
        courses= collection.find({})
        for courseElement in courses:
            output= output+courseElement["courseCode"]+": "
            for task in courseElement["tasks"]:
                output= output+task["desc"]+" "
    elif course != "":
        targetCourse= collection.find({"courseCode": course})
        output= course+": "
        # there should only be one course with the name course
        # but mongodb makes me do it this way
        for courseElement in targetCourse:
            for task in courseElement["tasks"]:
                output= output+" "+task["desc"]

    # gives back json object

    return output
