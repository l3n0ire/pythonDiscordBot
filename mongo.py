import pymongo
from pymongo import MongoClient
from collections import OrderedDict

cluster = MongoClient("mongodb+srv://colincool100:colinspassword@manage.wwmlv.mongodb.net/Courses?retryWrites=true&w=majority")
db = cluster["Manage"]
collection = db["Courses"]

courseSchema = {"$jsonSchema":
  {
    "bsonType": "object",
    "required":["courseCode","tasks"],
    "properties":{
        "courseCode":{
            "bsonType":"string",
            "description": "must be a string and is required"
        },
        "tasks":{
            "bsonType": "array",
            "items": {
                "bsonType":"object",
                "required": [ "desc", "dueDate",],
                "properties":{
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
        }
    }
  }
}

def addMongo(course,description):
    cmd =OrderedDict([('collMod', 'Courses'),
        ('validator', courseSchema),
        ('validationLevel', 'moderate')])
    db.command(cmd)
    try:
        collection.insert_one({"courseCode":course,
        "tasks":[{"desc":description, "dueDate":"today" ,"status":False}]})
    except:
        print("oof it didnt work")

def printMongo(course):
    # results is an array
    output = ""
    if course == "ALL":
        results =collection.find({})
        for result in results:
            output=output+" "+result["courseCode"]+ ": "+result["description"]
    elif course !="":
        targetCourse = collection.find({"courseCode":course})
        output=course+": "
        for task in targetCourse.tasks:
            output=output+" "+task["desc"]
    
    # gives back json object
    
    return output