import discord
import manage
from discord.ext import commands
from beautifultable import BeautifulTable
import datetime
import json
import mongo

# load env variables
from dotenv import load_dotenv
load_dotenv()

# get token from env variables
import os
token = os.environ.get("bot_token")


client = commands.Bot(command_prefix = '.')
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
    # data = readFile()
    # dataList = list()
    # for course in data.keys():
    #     for task in data[course]:
    #         if datetime.datetime.now() < datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M"):
    #             date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
    #             # table.rows.append([course, task['description'], date.strftime("%d/%m/%y"), date.strftime("%H:%M"), task["status"]])
    #             d = {'course': course, 'desc': task['description'], 'due': date.strftime("%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
    #             dataList.append(d)
    # return dataList

def getAll():
    data = readFile()
    dataList = list()

    for course in data.keys():
        for task in data[course]:
            date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
            d = {'course': course, 'desc': task['description'], 'due': date.strftime("%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
            dataList.append(d)
    return dataList

@client.command(brief='Gets reminders from Mongodb (ALL for all reminders)')
async def get(ctx, course):
    output = mongo.printMongo(course)
    await ctx.send(output)

@client.command(brief="Add course to Mongodb")
async def add(ctx, course, description):
    mongo.addMongo(course,description)

@client.command(brief="Remove course from Mongodb")
async def remove(ctx, course, description):
    mongo.removeMongo(course, description)

def createEmbed(course, description, due, status):
    if status == "COMPLETE":
        c = discord.Colour.green()
    else:
        c = discord.Colour.red()
    embed = discord.Embed(
        title = course,
        description = description,
        colour = c
    )

    embed.add_field(name='Due', value=d['due'], inline=False)
    return embed

@client.command(brief='Displays all tasks')
async def all(ctx):
    data = getAll()
    eList = list()

    for d in data:
        embed = createEmbed(d['course'], d['desc'], d['due'], d['status'])
        eList.append(embed)
    
    for embed in eList:
        await ctx.send(embed=embed)        

@client.command(brief='displays all tasks due today')
async def today(ctx):
    data = getTasksForDay()
    
    eList = list()

    for d in data:
        embed = createEmbed()
        eList.append(embed)
    
    for embed in eList:
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

