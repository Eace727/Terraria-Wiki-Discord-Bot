import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='-', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('You should go Keep yourself safe NOW!')
        await message.channel.send(file=discord.File('Keepyourselfsafe.jpg'))
    if message.content.startswith('$dog'):
        await message.channel.send(file=discord.File('Dog.jpg'))
    if message.content.startswith('mega'):
        await message.channel.send('What a Cutie')
        await message.channel.send(file=discord.File('Mega.jpg'))
    if message.content.startswith('eman'):
        await message.channel.send('What a Cutie')
        await message.channel.send(file=discord.File('Ethan.jpg'))
    if message.content.startswith('estavel'):
        await message.channel.send('What a Cutie')
        await message.channel.send(file=discord.File('karan.jpg'))


client.run(os.getenv('TOKEN'))
