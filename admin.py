import pymongo
from pymongo import MongoClient
from collections import OrderedDict
import mongo

cluster = MongoClient(
    "mongodb+srv://Mitra:mitrapassword@manage.wwmlv.mongodb.net/Courses?retryWrites=true&w=majority")
db = cluster["Manage"]
# this handles the courses collection
collection = db["Courses"]

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
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    }
                }
}
taskSchema = {"$jsonSchema": taskBody}

courseBody = {
    "bsonType": "object",
    "required": ["courseCode", "tasks","subscribers"],
    "properties": {
        "courseCode": {
            "bsonType": "string",
            "description": "must be a string and is required"
        },
        "tasks": {
            "bsonType": "array",
            "items": taskBody,
        },
        "subscribers":{
            "bsonType":"array",
            "items":{
                "bsonType": "string",
                "description": "must be a string and is required"
            }
        }
    }
}
courseSchema = {"$jsonSchema": courseBody}

def createCourse(courseCode):
    cmd = OrderedDict([('collMod', 'Courses'),
                           ('validator', courseSchema),
                           ('validationLevel', 'moderate')])
    db.command(cmd)
    # empty array is always valid
    collection.insert_one({"courseCode":courseCode,"tasks":[],"subscribers":[]})
    print("created course")

def addTask(courseCode,description,dueDate):
    collection.update_one(
        {"courseCode":courseCode},
        {"$push":{"tasks":{"desc":description,"dueDate":dueDate,"status":"not complete"} }})
    #add task to all subscribers
    courseObject = collection.find_one({"courseCode":courseCode})
    subs = courseObject["subscribers"]
    for user in subs:
        mongo.addMongo(user,courseCode,description,dueDate)
    print("added task")

def removeTask(courseCode,description):
    collection.update_one(
        {"courseCode":courseCode},
        {"$pull":{"tasks":{"desc":description} }})
    #add task to all subscribers
    courseObject = collection.find_one({"courseCode":courseCode})
    subs = courseObject["subscribers"]
    for user in subs:
        mongo.removeMongo(user,courseCode,description)
    print("removed task")

def subscribe(user,courseCode):
    collection.update_one({"courseCode":courseCode}, {"$push":{"subscribers":user}})
    # add the course to the user
    courseObject = collection.find_one({"courseCode":courseCode})
    course = {"courseCode":courseObject["courseCode"],"tasks":courseObject["tasks"]}
    mongo.addCourse(user,course)
    print("subscribed")

def unsubscribe(user,courseCode):
    collection.update_one({"courseCode":courseCode}, {"$pull":{"subscribers":user}})
    mongo.removeCourse(user,courseCode)
    print("unsubscribed")

