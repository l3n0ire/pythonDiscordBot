import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://colincool100:colinspassword@manage.wwmlv.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = cluster["Manage"]
collection = db["Tasks"]

def printMongo(course):
    # results is an array
    output = ""
    if course == "ALL":
        results =collection.find({})
        for result in results:
            output=output+" "+result["courseCode"]+ ": "+result["description"]
    elif course !="":
        results = collection.find({"courseCode":course})
        output=course+": "
        for result in results:
            output=output+" "+result["description"]
    
    # gives back json object
    
    return output