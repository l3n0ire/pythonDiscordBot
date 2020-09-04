import os
import discord
import manage
from discord.ext import commands
from beautifultable import BeautifulTable
import datetime
import json
import mongo
import admin
import datetime
from datetime import timedelta
import asyncio
import time
from threading import Thread

# load env variables
from dotenv import load_dotenv
load_dotenv()

# get token from env variables
token = os.environ.get("bot_token")
threadDict = dict()

# set timezone
# os.environ['TZ'] = 'America/Toronto'
# time.tzset()


client = commands.Bot(command_prefix='.')
m = manage.Manage()


@client.event
async def on_ready():
    # When the bot has everything it needs, it is ready    
    loadReminders()
    timeUntilNine = calculateTimeForDaily()    
    print('Bot is ready.')
    await dailyRemind(timeUntilNine)


def calculateTimeForDaily():
    tommorow = datetime.datetime.now()
    morningNine = datetime.datetime(year=tommorow.year, month=tommorow.month, day=tommorow.day, hour=9, minute=0, second=0)
    return (morningNine - datetime.datetime.now()).seconds

@client.command(brief='sends message to user\'s dm after the specified time interval')
async def remind(ctx, message, sleepTime):
    await asyncio.sleep(float(sleepTime)*60*60)
    author = ctx.message.author
    if author.dm_channel == None:
        dm = await author.create_dm()
        await dm.send(message)
    else:
        await author.dm_channel.send(message)
        

async def dailyRemind(timeUntilNine):
    await asyncio.sleep(timeUntilNine)
    while True:
        data = admin.getTasks('ALL')
        for course in data:
            for task in course['tasks']:
                if datetime.datetime.strptime(task['dueDate'], '%d/%m/%y %H:%M') >= datetime.datetime.now():
                    await notify(course['courseCode'], task['desc'], task['dueDate'])
        await asyncio.sleep(24*60*60)
        

def loadReminders():
    data = admin.getTasks('ALL')
    for course in data:
        for task in course['tasks']:
            if datetime.datetime.strptime(task['dueDate'], '%d/%m/%y %H:%M') >= datetime.datetime.now():
                threadDict[course['courseCode']] = {task['desc']: asyncio.Task(reminder(task['dueDate'], course['courseCode'], task['desc']))}
    print('done loading')

@client.command(brief='deletes all the expired tasks')
async def deleteOldTasks(ctx, courseCode):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    data = admin.getTasks('ALL')
    for course in data:
        for task in course['tasks']:                
            if datetime.datetime.strptime(task['dueDate'], '%d/%m/%y %H:%M') < datetime.datetime.now():
                admin.removeTask(course['courseCode'], task['desc'])
    await ctx.send('Deleted all expired tasks!')

@client.event
async def on_raw_reaction_add(raw):
    #the message that the user reacted to
    courseCode=None
    if raw.message_id == 750764988448112662:
        if str(raw.emoji) == '🍎':
            courseCode ='MGTA01'
        elif str(raw.emoji) =='🍌':
            courseCode ='VPMA93'
        if courseCode!=None:
            try:
                admin.subscribe(raw.member,courseCode)
                await client.get_channel(raw.channel_id).send(raw.member.mention+" successfully enrolled in "+courseCode)
            except Exception as e:
                await client.get_channel(raw.channel_id).send("FAILED! could not subscribe. Error: "+str(e))

@client.event
async def on_raw_reaction_remove(raw):
    #the message that the user reacted to
    courseCode=None
    if raw.message_id == 750764988448112662:
        if str(raw.emoji) == '🍎':
            courseCode ='MGTA01'
        elif str(raw.emoji) =='🍌':
            courseCode ='VPMA93'
        if courseCode!=None:
            try:
                user =client.get_user(raw.user_id)
                admin.unsubscribe(user.name,courseCode)
                await client.get_channel(raw.channel_id).send(user.mention+" successfully unenrolled from "+courseCode)
            except Exception as e:
                await client.get_channel(raw.channel_id).send("FAILED! could not unsubscribe. Error: "+str(e))

async def reminder(dt, courseCode,description):
    newDate = datetime.datetime.strptime(dt, '%d/%m/%y %H:%M')
    date1 = datetime.datetime.utcfromtimestamp(newDate.timestamp()) - datetime.datetime.utcnow() 
    timeUntilRemind = date1.total_seconds()
    await asyncio.sleep(timeUntilRemind)
    await notify(courseCode,description,dt)

def readFile():
    with open("tasks.json") as f:
        data = json.load(f)
    return data

# def getTasksForDay():
#     data = readFile()
#     dataList = list()
#     for course in data.keys():
#         for task in data[course]:
#             if datetime.datetime.now() < datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M"):
#                 date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
#                 # table.rows.append([course, task['description'], date.strftime("%d/%m/%y"), date.strftime("%H:%M"), task["status"]])
#                 d = {'course': course, 'desc': task['description'], 'due': date.strftime("%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
#                 dataList.append(d)
#     return dataList


def getAll():
    data = readFile()
    dataList = list()

    for course in data.keys():
        for task in data[course]:
            date = datetime.datetime.strptime(
                task["dueDate"], "%d/%m/%y %H:%M")
            d = {'course': course, 'desc': task['description'], 'due': date.strftime(
                "%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
            dataList.append(d)
    return dataList


@client.command(brief="Adds a task to Mongodb")
async def add(ctx, course, description, dueDate):
    user = ctx.message.author
    print(dueDate)
    try:
        datetime.datetime.strptime(dueDate, "%d/%m/%y %H:%M")
    except ValueError:
        await ctx.send("FAILED! Date is not in the correct format.")
        return
    print(user)
    try:
        mongo.addMongo(user.name, course, description, dueDate)
        await ctx.send("Successfully added for " + user.mention + " in " + course+" Description: "+ description+" due on "+dueDate)
    except Exception as e:
       print("FAILED! could not delete task. Error: "+str(e))

@client.command(brief="Removes task from Mongodb")
async def remove(ctx, course, description):
    user = ctx.message.author
    try:
        mongo.removeMongo(user.name,course, description)
        await ctx.send("Successfully deleted task \""+ course+" "+description+"\" for "+user.mention)
    except Exception as e:
        await ctx.send("FAILED! could not delete task. Error: "+str(e))

@client.command(brief="Edits the dueDate of a task")
async def edit(ctx,course,description, newDueDate):
    user = ctx.message.author
    try:
        mongo.editMongo(user.name,course,description,newDueDate)
        await ctx.send("Successfully edited due date of \""+ course+" "+description+"\" for "+user.mention+" to \""+newDueDate+"\"")
    except Exception as e:
        await ctx.send("FAILED! could not edit task. Error: "+str(e))

@client.command(brief="Sets status of task (complete, in progress, not complete)")
async def setStatus(ctx,course,description,status):
    user = ctx.message.author
    try:
        mongo.setStatusMongo(user.name,course,description,status)
        await ctx.send("Successfully set status of \""+ course+" "+description+"\" for "+user.mention+" to \""+status+"\"")
    except Exception as e:
        await ctx.send("FAILED! could not set status for task. Error: "+str(e))
    
def createEmbed(course, description, due, status):
    if status == "complete":
        c=discord.Colour.green()
    elif status == "in progress":
        c=discord.Colour.orange()
    else:
        c=discord.Colour.red()
    embed=discord.Embed(
        title=course,
        description=description,
        colour=c
    )

    embed.add_field(name='Due', value=due, inline=False)
    return embed

@ client.command(brief='Displays all tasks')
async def all(ctx):
    data=getAll()
    eList=list()

    for d in data:
        embed=createEmbed(d['course'], d['desc'], d['dueDate'], d['status'])
        eList.append(embed)

    for embed in eList:
        await ctx.send(embed=embed)

@ client.command(brief='displays all tasks due today')
async def today(ctx):
    data=mongo.getDataFromMongo(ctx.message.author.name)
    embedList=list()
    for user in data:
        for course in user["courses"]:
            for task in course["tasks"]:
                embed=createEmbed(
                    course['courseCode'], task['desc'], task['dueDate'], task['status'])
                embedList.append(embed)

    for embed in embedList:
        await ctx.send(embed=embed)

# admin stuff
@client.command(brief="Creates a new course")
async def createCourse(ctx, courseCode):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    try:
        admin.createCourse(courseCode)
        await ctx.send("Successfully added course "+courseCode)
    except Exception as e:
        await ctx.send("FAILED! could not add course. Error: "+str(e))

@client.command(brief="Adds a new task to a course")
async def addTask(ctx, courseCode, description, dueDate):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    try:
        datetime.datetime.strptime(dueDate, "%d/%m/%y %H:%M")
    except ValueError:
        await ctx.send("FAILED! Date is not in the correct format.")
        return
    try:
        admin.addTask(courseCode,description,dueDate)
        await ctx.send("Successfully added \""+description+"\" due on \""+dueDate+"\" for "+courseCode)
        threadDict[courseCode] = {description: asyncio.Task(reminder(dueDate, courseCode,description))}
    except Exception as e:
        await ctx.send("FAILED! could not add task. Error: "+str(e))

@client.command(brief="Removes a task from a course")
async def removeTask(ctx, courseCode, description):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    try:
        admin.removeTask(courseCode,description)
        threadDict.pop(courseCode).pop(description).cancel()
        await ctx.send("Successfully removed \""+description+"\" for "+courseCode)
    except Exception as e:
        await ctx.send("FAILED! could not remove task. Error: "+str(e))

@client.command(brief="Edits a task for a course")
async def editTask(ctx, courseCode, description, newDueDate):
    user = ctx.message.author
    if not isAdmin(user):
        await ctx.send("You do not have admin permissions")
        return
    try:
        admin.editTask(courseCode,description,newDueDate)
        await ctx.send("Successfully edited due date of \""+ courseCode+" "+description+"\" for "+user.mention+" to \""+newDueDate+"\"")
        threadDict.pop(courseCode).pop(description).cancel()
        threadDict[courseCode] = {description: asyncio.Task(reminder(newDueDate, courseCode,description))}
    except Exception as e:
        await ctx.send("FAILED! could not remove task. Error: "+str(e))

@client.command(brief="Enrols user to a course")
async def enroll(ctx, courseCode):
    user = ctx.message.author
    try:
        admin.subscribe(user,courseCode)
        await ctx.send(user.mention+" successfully enrolled in "+courseCode)
    except Exception as e:
        await ctx.send("FAILED! could not subscribe. Error: "+str(e))

@client.command(brief="Unenrols user froms a course")
async def unenroll(ctx, courseCode):
    user = ctx.message.author
    try:
        admin.unsubscribe(user,courseCode)
        await ctx.send(user.mention+" successfully unenrolled from "+courseCode)
    except Exception as e:
        await ctx.send("FAILED! could not unsubscribe. Error: "+e)

@client.command(brief="Shows subsribers for a course (ALL for all courses)")
async def showSubscribers(ctx, courseCode):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    try:
        await ctx.send(admin.showSubscribers(courseCode))
    except Exception as e:
        await ctx.send("FAILED! could not show subscribers. Error: "+str(e))

@client.command(brief="Shows tasks for a course (ALL for all courses)")
async def showTasks(ctx, courseCode):
    if not isAdmin(ctx.message.author):
        await ctx.send("You do not have admin permissions")
        return
    try:
        data=admin.getTasks(courseCode)
        embedList=list()
        for course in data:
            for task in course["tasks"]:
                embed=createEmbed(
                    course['courseCode'], task['desc'], task['dueDate'], task['status'])
                embedList.append(embed)
        for embed in embedList:
            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("FAILED! could not show tasks. Error: "+str(e))

@client.command()
async def getStatus(ctx, courseCode ,description):
    user = ctx.message.author
    await ctx.send(mongo.getStatusMongo(user,courseCode,description))

async def notify(courseCode, description, dueDate):
    subs = admin.getSubs(courseCode)
    
    for sub in subs:
        user = client.get_user(sub["id"])
        status = mongo.getStatusMongo(user,courseCode,description)
        print(status)
        embed=createEmbed(courseCode, description, dueDate,status)
        if user.dm_channel == None:
            dm = await user.create_dm()
            await dm.send(embed=embed)
        else:
            await user.dm_channel.send(embed=embed)
    

@client.command()
async def time(ctx):
    await ctx.send(datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%y %H:%M"))

def isAdmin(user):
    return client.get_channel(748928662614573090).permissions_for(user).administrator


    # embed = discord.Embed(
    #     title = 'MGEA05',
    #     description = 'Exam',
    #     colour = discord.Colour.blue()
    # )

    # embed.add_field(name='Due', value='23/12/21 23:59', inline=False)
    # # embed.add_field(name='Status', value='COMPLETE', inline=False) USE REACTIONS INSTEAD

    # await ctx.send(embed=embed)

# | Course | Description | Due Date | Due Time |  Status  |
# | MGEA05 |    Exam     | 23/12/21 |  23:59   | COMPLETE |
client.run(token)
