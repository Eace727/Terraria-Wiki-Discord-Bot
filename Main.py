import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True


client = commands.Bot(command_prefix='!', intents=intents)

@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@client.tree.command(name="search", description="search the terraria wiki")
async def search_wiki(interaction: discord.Interaction, search: str):
    url = "https://terraria.wiki.gg/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["query"]["search"]:
        # Retrieve the first search result
        result = data["query"]["search"][0]
        title = result["title"]
        snippet = result["snippet"]

        # Format the response message
        message = f"**{title}**\n{snippet}..."
    else:
        message = "No results found."

    await interaction.response.send_message(message)



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

@client.event
async def on_ready():
    await client.tree.sync()
    print(f'Logged in as {client.user}!')


client.run(os.getenv('TOKEN'))
