import os
import discord
import manage
from discord.ext import commands
from beautifultable import BeautifulTable
import datetime
import json
import mongo
import datetime

# load env variables
from dotenv import load_dotenv
load_dotenv()

# get token from env variables
token = os.environ.get("bot_token")


client = commands.Bot(command_prefix='.')
m = manage.Manage()


@client.event
async def on_ready():
    # When the bot has everything it needs, it is ready
    print('Bot is ready.')


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
    user = ctx.message.author.name
    print(dueDate)
    try:
        datetime.datetime.strptime(dueDate, "%d/%m/%y %H:%M")
    except ValueError:
        await ctx.send("FAILED! Date is not in the correct format.")
        return
    print(user)
    try:
        mongo.addMongo(user, course, description, dueDate)
        await ctx.send("Successfully added for " + user + " in " + course+" Description: "+ description+" due on "+dueDate)
    except Exception as e:
       print(e)

@client.command(brief="Removes task from Mongodb")
async def remove(ctx, course, description):
    user = ctx.message.author.name
    try:
        mongo.removeMongo(user,course, description)
        await ctx.send("Successfully deleted Task "+ course+" "+description+" for "+user)
    except Exception as e:
        await ctx.send("FAILED! could not delete task. Error: "+e)

@client.command(brief="Edits the dueDate of a task")
async def edit(ctx,course,description, newDueDate):
    user = ctx.message.author.name
    try:
        mongo.editMongo(user,course,description,newDueDate)
        await ctx.send("Successfully edited due date of "+ course+" "+description+" for "+user+" to "+newDueDate)
    except Exception as e:
        await ctx.send("FAILED! could not edit task. Error: "+e)


def createEmbed(course, description, due, status):
    if status == "COMPLETE":
        c=discord.Colour.green()
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
