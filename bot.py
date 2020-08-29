import discord
import manage
from discord.ext import commands
from beautifultable import BeautifulTable
import datetime
import json

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

# @client.event
# async def on_member_join(member):
#     print(f'{member} has joined a server.')

# @client.event
# async def on_member_remove(member):
#     print(f'{member} has left a server.')
def readFile():
    with open("tasks.json") as f:
        data = json.load(f)
    return data

def getTasksForDay():
    data = readFile()
    dataList = list()
    for course in data.keys():
        for task in data[course]:
            if datetime.datetime.now() < datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M"):
                date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
                # table.rows.append([course, task['description'], date.strftime("%d/%m/%y"), date.strftime("%H:%M"), task["status"]])
                d = {'course': course, 'desc': task['description'], 'due': date.strftime("%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
                dataList.append(d)
    return dataList

def getAll():
    data = readFile()
    dataList = list()

    for course in data.keys():
        for task in data[course]:
            date = datetime.datetime.strptime(task["dueDate"], "%d/%m/%y %H:%M")
            d = {'course': course, 'desc': task['description'], 'due': date.strftime("%d/%m/%y") + ' ' + date.strftime("%H:%M"), 'status': task['status']}
            dataList.append(d)
            # table = Manage.addToTable(table, task, course)
    return dataList

# @client.command()
# async def getinfo(ctx):
#     embed = discord.Embed(
#         title = "Commands",
#         colour = discord.Colour.blue()
#     )

#     embed.add_field(name='.all', value='displays all tasks', inline=False)
#     embed.add_field(name='.today', value='displays tasks due in the future', inline=False)

#     await ctx.send(embed=embed)

@client.command(brief='Displays all tasks')
async def all(ctx):
    data = getAll()
    eList = list()

    for d in data:
        if d['status'] == 'COMPLETE':
            c = discord.Colour.green()
        else:
            c = discord.Colour.red()
        embed = discord.Embed(
            title = d['course'],
            description = d['desc'],
            
            colour = c
        )

        embed.add_field(name='Due', value=d['due'], inline=False)
        # embed.add_field(name='Status', value=d['status'], inline=False)
        eList.append(embed)
    
    for embed in eList:
        await ctx.send(embed=embed)        

@client.command(brief='displays all tasks due today')
async def today(ctx):
    data = getTasksForDay()
    
    eList = list()

    for d in data:
        if d['status'] == 'COMPLETE':
            c = discord.Colour.green()
        else:
            c = discord.Colour.red()
        embed = discord.Embed(
            title = d['course'],
            description = d['desc'],
            
            colour = c
        )

        embed.add_field(name='Due', value=d['due'], inline=False)
        # embed.add_field(name='Status', value=d['status'], inline=False)
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

